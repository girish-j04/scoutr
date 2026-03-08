"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { QueryState, DossierCandidate, MonitoringAlert } from "@/lib/types";
import { useClub } from "@/lib/ClubContext";
import { submitQuery, postWatchlist } from "@/lib/api";
import { AnimatePresence } from "framer-motion";

import { DotPattern } from "@/components/ui/dot-pattern";

import ClubSwitcher from "@/components/sidebar/ClubSwitcher";
import SquadGapCard from "@/components/sidebar/SquadGapCard";
import BudgetGauge from "@/components/sidebar/BudgetGauge";
import MonitoredPlayers from "@/components/sidebar/MonitoredPlayers";
import MonitoredPlayerDetail from "@/components/monitoring/MonitoredPlayerDetail";
import ChatInput from "@/components/chat/ChatInput";
import AgentReasoningStream from "@/components/chat/AgentReasoningStream";
import DossierCardGrid from "@/components/dossier/DossierCardGrid";
import { DossierCardSkeleton } from "@/components/common/Skeleton";

const EXAMPLE_QUERIES = [
  "LB under 24, high press, contract < 12 months, < €7M",
  "DM with elite passing range, Bundesliga, under 26",
  "Striker, Serie A or Ligue 1, xG > 0.45, available loan",
];

export default function AppDashboard() {
  const { activeClub } = useClub();
  
  // Search & Result State
  const [queryState, setQueryState] = useState<QueryState>({
    status: "idle",
    query: "",
    reasoning_steps: [],
    candidates: [],
  });

  // Monitoring State
  const [watchlist, setWatchlist] = useState<string[]>([]); // Start empty
  const [alerts, setAlerts] = useState<MonitoringAlert[]>([]);
  const [monitoredPlayers, setMonitoredPlayers] = useState<any[]>([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout>();

  const handleSubmit = useCallback(async (query: string) => {
    setQueryState({
      status: "streaming",
      query,
      reasoning_steps: [],
      candidates: [],
    });

    await submitQuery(
      query,
      (step) => {
        setQueryState((prev) => ({
          ...prev,
          reasoning_steps: [...prev.reasoning_steps, step],
        }));
      },
      (candidates) => {
        setQueryState((prev) => ({
          ...prev,
          status: "complete",
          candidates,
        }));
      },
      (_error) => {
        setQueryState((prev) => ({
          ...prev,
          status: "complete",
          candidates: [],
        }));
      }
    );
  }, []);

  const handleMonitor = useCallback((playerId: string) => {
    setWatchlist(prev => {
      if (prev.includes(playerId)) {
        return prev.filter(id => id !== playerId);
      }
      return [...prev, playerId];
    });
  }, []);

  // 1. Maintain a cache of player metadata from current candidates
  useEffect(() => {
    const currentCandidates = queryState.candidates.map(c => c.player);
    if (currentCandidates.length === 0) return;
    
    setMonitoredPlayers(prev => {
      const combined = [...prev];
      currentCandidates.forEach(p => {
        const index = combined.findIndex(item => item.player_id === p.player_id);
        if (index === -1) combined.push(p);
        else combined[index] = p;
      });
      return combined;
    });
  }, [queryState.candidates]);

  // 2. Hydrate missing player data for those in watchlist but not in local cache
  useEffect(() => {
    watchlist.forEach(async (id) => {
      const alreadyHaveMetadata = monitoredPlayers.some(p => p.player_id === id);
      if (!alreadyHaveMetadata) {
        try {
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/player/${id}`);
          if (res.ok) {
            const p = await res.json();
            setMonitoredPlayers(curr => {
              if (curr.some(item => item.player_id === id)) return curr;
              return [...curr, p];
            });
          }
        } catch (e) {
          console.error(`Failed to hydrate player ${id}`, e);
        }
      }
    });
  }, [watchlist, monitoredPlayers]);

  const displayMonitored = monitoredPlayers.filter(p => watchlist.includes(p.player_id));

  // Polling for alerts
  useEffect(() => {
    const poll = async () => {
      try {
        const ids = watchlist.map(id => parseInt(id)).filter(id => !isNaN(id));
        if (ids.length > 0) {
          const freshAlerts = await postWatchlist(ids);
          setAlerts(freshAlerts);
        } else {
          setAlerts([]);
        }
      } catch (e) {
        console.error("Polling failed", e);
      }
    };

    poll(); // Initial poll
    intervalRef.current = setInterval(poll, 10000); // Poll every 10s

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [watchlist]);

  const isLoading = queryState.status === "streaming";
  const hasResults = queryState.candidates.length > 0;
  const isIdle = queryState.status === "idle";

  const activeDetailPlayer = monitoredPlayers.find(p => p.player_id === selectedPlayerId);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="w-[280px] flex-shrink-0 bg-pitch-900 border-r border-pitch-700 flex flex-col overflow-hidden">
        {/* Club switcher */}
        <ClubSwitcher />

        {/* Scrollable sidebar body */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          <SquadGapCard gap={activeClub.squad_gap} />
          <BudgetGauge
            total={activeClub.budget_total}
            remaining={activeClub.budget_remaining}
          />
          
          <MonitoredPlayers 
            players={displayMonitored} 
            onSelect={(id) => setSelectedPlayerId(id)} 
          />
          
          <div className="h-4" />
        </div>

        {/* Fixed sidebar footer */}
        <div className="flex-shrink-0 border-t border-pitch-700 px-4 py-3">
          <div className="flex items-center gap-2">
            <div
              className="w-6 h-6 rounded-card flex items-center justify-center"
              style={{ backgroundColor: "var(--club-primary-muted)" }}
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M6 1L11 4V8L6 11L1 8V4L6 1Z" stroke="var(--club-primary)" strokeWidth="1" fill="none" />
              </svg>
            </div>
            <div>
              <span className="font-bebas text-sm text-ink block leading-tight tracking-wider">ScoutR</span>
              <span className="text-[8px] font-mono text-ink-faint tracking-wider">TRANSFER INTELLIGENCE</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────── */}
      <main className="flex-1 flex flex-col min-w-0 bg-pitch-950 overflow-hidden">
        {/* Fixed top bar */}
        <div className="flex-shrink-0 border-b border-pitch-700 px-6 py-3 flex items-center justify-between bg-pitch-900/50">
          <div>
            <h2 className="font-body font-semibold text-sm text-ink tracking-wide leading-tight">
              Sporting Director Co-Pilot
            </h2>
            <p className="text-[10px] font-mono text-ink-faint tracking-wider">
              {isLoading ? "AGENTS ACTIVE" : hasResults ? "ANALYSIS COMPLETE" : "READY"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full transition-colors ${isLoading ? "animate-pulse-dot" : ""}`}
              style={{
                backgroundColor: isLoading
                  ? "var(--club-primary)"
                  : hasResults
                  ? "#22956E"
                  : "rgba(107,124,116,0.3)",
              }}
            />
            <span className="text-[10px] font-mono text-ink-faint">
              {isLoading
                ? "Processing query..."
                : hasResults
                ? `${queryState.candidates.length} candidates found`
                : "Awaiting query"}
            </span>
          </div>
        </div>

        {/* Scrollable content */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          <div className="px-6 py-5 min-h-full flex flex-col">

            {/* Idle state */}
            {isIdle && (
              <div className="flex-1 relative flex flex-col items-center justify-center text-center max-w-xl mx-auto w-full py-12">
                <DotPattern
                  width={24}
                  height={24}
                  cr={0.8}
                  className="[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
                  style={{ color: "var(--club-primary)", opacity: 0.12 }}
                />
                <div className="relative z-10">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center mb-5 mx-auto border border-pitch-700"
                    style={{ backgroundColor: "var(--club-primary-muted)" }}
                  >
                    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                      <path d="M14 3L25 9V19L14 25L3 19V9L14 3Z" stroke="var(--club-primary)" strokeWidth="1.5" fill="none" />
                      <path d="M14 3V25M3 9L25 19M25 9L3 19" stroke="var(--club-primary)" strokeWidth="0.5" opacity="0.5" />
                    </svg>
                  </div>

                  <h3 className="font-body font-bold text-2xl text-ink mb-3 leading-snug tracking-tight">
                    Describe the player you need
                  </h3>
                  <p className="text-sm text-ink-muted font-body leading-relaxed mb-6 max-w-sm mx-auto">
                    ScoutR deploys four AI agents to search, value, and assess tactical fit across 50+ leagues simultaneously.
                  </p>

                  <div className="flex flex-wrap gap-2 justify-center">
                    {EXAMPLE_QUERIES.map((q) => (
                      <button
                        key={q}
                        onClick={() => handleSubmit(q)}
                        className="text-[11px] font-body px-3 py-1.5 rounded-sm border transition-colors text-left text-ink-muted bg-pitch-800"
                        style={{
                          borderColor: "var(--club-primary)",
                        }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--club-primary-muted)";
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--color-pitch-800)";
                        }}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Reasoning stream */}
            {(isLoading || queryState.reasoning_steps.length > 0) && (
              <div className="mb-6">
                {queryState.query && (
                  <div className="mb-4 px-1">
                    <span className="text-[10px] font-mono text-ink-faint uppercase tracking-wider">Query</span>
                    <p className="text-sm font-body text-ink mt-1 italic">&ldquo;{queryState.query}&rdquo;</p>
                  </div>
                )}
                <AgentReasoningStream steps={queryState.reasoning_steps} isStreaming={isLoading} />
              </div>
            )}

            {/* Loading skeletons */}
            {isLoading && queryState.reasoning_steps.length >= 6 && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mt-6">
                <DossierCardSkeleton />
                <DossierCardSkeleton />
                <DossierCardSkeleton />
              </div>
            )}

            {/* Results */}
            {hasResults && (
              <DossierCardGrid 
                candidates={queryState.candidates} 
                watchlist={watchlist}
                onWatch={handleMonitor}
              />
            )}
          </div>
        </div>

        {/* Fixed chat input */}
        <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
      </main>

      {/* Monitored Player Detail Modal */}
      <AnimatePresence>
        {activeDetailPlayer && (
          <MonitoredPlayerDetail 
            player={activeDetailPlayer} 
            alerts={alerts} 
            onClose={() => setSelectedPlayerId(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
}
