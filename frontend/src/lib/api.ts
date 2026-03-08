import { API_BASE_URL } from "./constants";
import { AgentType, DossierCandidate, MonitoringAlert, ReasoningStep } from "./types";

// ── Agent inference ──────────────────────────────────────────────────────────

function inferAgent(step: string): AgentType {
  if (step.includes("valuation") || step.includes("fee") || step.includes("contract")) return "valuation";
  if (step.includes("search") || step.includes("rank") || step.includes("candidate")) return "scout";
  if (step.includes("tactical") || step.includes("fit") || step.includes("assembly")) return "tactical";
  return "orchestrator";
}

// ── Response adapter: backend QueryResponse → frontend DossierCandidate[] ────

function toRawFee(val: number | undefined | null): number {
  if (!val) return 0;
  // Backend returns fees in millions (e.g. 5.0); frontend expects raw euros (5_000_000)
  return val < 1000 ? val * 1_000_000 : val;
}

function monthsToExpiry(months: number | undefined | null): string {
  if (!months) return "";
  const d = new Date();
  d.setMonth(d.getMonth() + months);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function adaptDossiers(data: any): DossierCandidate[] {
  // Backend sends QueryResponse.dossiers; guard against both shapes
  const dossiers: unknown[] = data.dossiers ?? data.candidates ?? [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return dossiers.map((d: any) => {
    const p = d.player ?? {};
    const pm = p.press_metrics ?? {};
    const fr = d.fee_range ?? {};
    return {
      player: {
        player_id: p.player_id ?? "",
        name: p.name ?? "",
        club: p.club ?? "",
        league: p.league ?? "",
        age: p.age ?? 0,
        position: p.position ?? "",
        nationality: p.nationality ?? "",
        // Backend uses contract_expiry_months (int); frontend uses contract_expiry (string)
        contract_expiry: p.contract_expiry ?? monthsToExpiry(p.contract_expiry_months),
        market_value: p.market_value ?? 0,
        press_metrics: {
          ppda: pm.ppda ?? 0,
          pressure_success_rate: pm.pressure_success_rate ?? 0,
          // Backend field is defensive_actions_per_90 (underscore); frontend uses per90
          defensive_actions_per90:
            pm.defensive_actions_per90 ?? pm.defensive_actions_per_90 ?? 0,
        },
        // Backend uses _per_90 suffix; frontend uses short names
        progressive_carries: p.progressive_carries ?? p.progressive_carries_per_90 ?? 0,
        xA: p.xA ?? p.xa_per_90 ?? 0,
        xG: p.xG ?? p.xg_per_90 ?? 0,
      },
      rank: d.rank ?? 1,
      ranking_reason: d.ranking_reason ?? d.reasoning?.ranking_reason ?? "",
      tactical_fit_score: d.tactical_fit_score ?? 0,
      fit_explanation: d.fit_explanation ?? d.valuation_narrative ?? "",
      heatmap_zones: d.heatmap_zones ?? [],
      // Backend returns formation_compatibility as string[] — take first or join
      formation_compatibility: Array.isArray(d.formation_compatibility)
        ? d.formation_compatibility[0] ?? ""
        : d.formation_compatibility ?? "",
      fee_range: {
        // Backend: {low_estimate, mid_estimate, high_estimate} in millions
        low: toRawFee(fr.low ?? fr.low_estimate),
        mid: toRawFee(fr.mid ?? fr.mid_estimate),
        high: toRawFee(fr.high ?? fr.high_estimate),
      },
      contract_risk: d.contract_risk ?? "green",
      scouting_summary: d.scouting_summary ?? "",
      comparable_transfers: (d.comparable_transfers ?? []).map(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (ct: any) => ({
          player_name: ct.player_name ?? "",
          from_club: ct.from_club ?? "",
          to_club: ct.to_club ?? "",
          // Backend: fee_millions (float in M); frontend: fee (raw euros)
          fee: toRawFee(ct.fee ?? ct.fee_millions),
          // Backend: transfer_year; frontend: year
          year: ct.year ?? ct.transfer_year ?? 0,
        })
      ),
    };
  });
}

// ── Session ID for follow-up context ─────────────────────────────────────────

const SESSION_KEY = "scoutr_session_id";

export function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return "";
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID?.() ?? `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

// ── SSE streaming via fetch (POST) ───────────────────────────────────────────

export interface SubmitQueryOptions {
  sessionId?: string;
}

export async function submitQuery(
  query: string,
  onStep: (step: ReasoningStep) => void,
  onComplete: (candidates: DossierCandidate[]) => void,
  onError: (error: string) => void,
  options?: SubmitQueryOptions
): Promise<() => void> {
  let aborted = false;
  const controller = new AbortController();

  const body: { query: string; session_id?: string } = { query };
  if (options?.sessionId) body.session_id = options.sessionId;

  (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/query/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        onError("Failed to connect to server.");
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const processChunk = (chunk: string) => {
        // Normalize CRLF → LF
        const lines = chunk.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
        let eventType = "";
        const dataLines: string[] = [];

        for (const line of lines) {
          if (line.startsWith("event:")) eventType = line.slice(6).trim();
          else if (line.startsWith("data:")) dataLines.push(line.slice(5));
        }

        if (!eventType || dataLines.length === 0) return;
        const eventData = dataLines.join("\n").trim();

        try {
          if (eventType === "agent_step") {
            const parsed = JSON.parse(eventData);
            onStep({
              step: parsed.step,
              detail: parsed.detail,
              agent: parsed.agent ?? inferAgent(parsed.step),
            });
          } else if (eventType === "final_result") {
            const parsed = JSON.parse(eventData);
            onComplete(adaptDossiers(parsed ?? {}));
          } else if (eventType === "error") {
            const parsed = JSON.parse(eventData);
            onError(parsed.error ?? "Unknown server error");
          }
        } catch {
          // Ignore malformed event chunks
        }
      };

      while (!aborted) {
        const { done, value } = await reader.read();

        if (done) {
          // Flush: process anything left in the buffer when stream closes,
          // even if it has no trailing \n\n
          buffer += decoder.decode();
          if (buffer.trim()) processChunk(buffer);
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Normalize CRLF → LF BEFORE splitting so \r\n\r\n becomes \n\n
        buffer = buffer.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

        // SSE events are separated by double newlines
        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";
        for (const chunk of parts) processChunk(chunk);
      }
    } catch (err) {
      if (!aborted) {
        onError("Failed to connect to the server.");
      }
    }
  })();

  return () => {
    aborted = true;
    controller.abort();
  };
}

export async function fetchMonitoringAlerts(): Promise<MonitoringAlert[]> {
  const res = await fetch(`${API_BASE_URL}/monitoring`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  const data = await res.json();
  // Backend returns { alerts: [...] } from check_watchlist()
  return data.alerts ?? data;
}

export async function postWatchlist(playerIds: number[]): Promise<MonitoringAlert[]> {
  const res = await fetch(`${API_BASE_URL}/watchlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_ids: playerIds }),
  });
  if (!res.ok) throw new Error("Failed to post watchlist");
  const data = await res.json();
  return data.alerts ?? data;
}

// ── PDF Export ───────────────────────────────────────────────────────────────

export async function exportPDF(candidate: DossierCandidate): Promise<Blob> {
  // Backend expects { player_ids: int[], query: string, club: string }
  const playerId = parseInt(candidate.player.player_id, 10);
  const res = await fetch(`${API_BASE_URL}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      player_ids: [isNaN(playerId) ? 1001 : playerId],
      query: "",
      club: "Leeds United",
    }),
  });
  if (!res.ok) throw new Error("Failed to generate PDF");
  return res.blob();
}

export function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function formatFee(value: number): string {
  if (value >= 1_000_000) {
    return `€${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `€${(value / 1_000).toFixed(0)}K`;
  }
  return `€${value}`;
}