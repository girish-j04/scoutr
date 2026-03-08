"use client";

import { useState, useCallback } from "react";
import { QueryState } from "@/lib/types";
import {
  LEEDS_PROFILE,
  MOCK_ALERTS,
  MOCK_CANDIDATES,
} from "@/lib/constants";
import { submitQuery } from "@/lib/api";

import { DotPattern } from "@/components/ui/dot-pattern";

import ClubIdentityPanel from "@/components/sidebar/ClubIdentityPanel";
import SquadGapCard from "@/components/sidebar/SquadGapCard";
import BudgetGauge from "@/components/sidebar/BudgetGauge";
import MonitoringFeed from "@/components/sidebar/MonitoringFeed";
import ChatInput from "@/components/chat/ChatInput";
import AgentReasoningStream from "@/components/chat/AgentReasoningStream";
import DossierCardGrid from "@/components/dossier/DossierCardGrid";
import { DossierCardSkeleton } from "@/components/common/Skeleton";

export default function Home() {
  const [queryState, setQueryState] = useState<QueryState>({
    status: "idle",
    query: "",
    reasoning_steps: [],
    candidates: [],
  });

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
        // Fall back to mock data if backend is unavailable
        setQueryState((prev) => ({
          ...prev,
          status: "complete",
          candidates: MOCK_CANDIDATES,
        }));
      }
    );
  }, []);

  const isLoading = queryState.status === "streaming";
  const hasResults = queryState.candidates.length > 0;
  const isIdle = queryState.status === "idle";

  return (
    <div className="flex h-screen overflow-hidden">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="w-[280px] flex-shrink-0 bg-pitch-900 border-r border-pitch-700 flex flex-col overflow-hidden">
        {/* Fixed club header */}
        <ClubIdentityPanel club={LEEDS_PROFILE} />

        {/* Scrollable sidebar body */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          <SquadGapCard gap={LEEDS_PROFILE.squad_gap} />
          <BudgetGauge
            total={LEEDS_PROFILE.budget_total}
            remaining={LEEDS_PROFILE.budget_remaining}
          />
          <MonitoringFeed alerts={MOCK_ALERTS} />
          <div className="h-4" />
        </div>

        {/* Fixed sidebar footer */}
        <div className="flex-shrink-0 border-t border-pitch-700 px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-card bg-emerald/20 flex items-center justify-center">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M6 1L11 4V8L6 11L1 8V4L6 1Z" stroke="#22956E" strokeWidth="1" fill="none" />
              </svg>
            </div>
            <div>
              <span className="text-[10px] font-display font-bold text-ink block leading-tight">ScoutR</span>
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
            <h2 className="font-display font-bold text-sm text-ink">Sporting Director Co-Pilot</h2>
            <p className="text-[10px] font-mono text-ink-faint tracking-wider">
              {isLoading ? "AGENTS ACTIVE" : hasResults ? "ANALYSIS COMPLETE" : "READY"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full transition-colors ${
              isLoading ? "bg-gold animate-pulse-dot" : hasResults ? "bg-emerald" : "bg-ink-faint/30"
            }`} />
            <span className="text-[10px] font-mono text-ink-faint">
              {isLoading ? "Processing query..." : hasResults ? `${queryState.candidates.length} candidates found` : "Awaiting query"}
            </span>
          </div>
        </div>

        {/* Scrollable content — plain div, constrained by flex */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          <div className="px-6 py-5 min-h-full flex flex-col">

            {/* Idle state */}
            {isIdle && (
              <div className="flex-1 relative flex flex-col items-center justify-center text-center max-w-lg mx-auto w-full py-12">
                <DotPattern
                  width={24}
                  height={24}
                  cr={0.8}
                  className="text-emerald/15 [mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
                />
                <div className="relative z-10">
                  <div className="w-16 h-16 rounded-full bg-pitch-800 border border-pitch-700 flex items-center justify-center mb-4 mx-auto">
                    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                      <path d="M14 3L25 9V19L14 25L3 19V9L14 3Z" stroke="#1B7A5A" strokeWidth="1.5" fill="none" />
                      <path d="M14 3V25M3 9L25 19M25 9L3 19" stroke="#1B7A5A" strokeWidth="0.5" opacity="0.4" />
                    </svg>
                  </div>
                  <h3 className="font-display font-bold text-lg text-ink mb-2">Describe the player you need</h3>
                  <p className="text-sm text-ink-muted font-body leading-relaxed mb-1">
                    ScoutR will deploy its agents to search, value, and assess tactical fit across 50+ leagues automatically.
                  </p>
                  <p className="text-xs text-ink-faint font-body">
                    Try: &ldquo;Find me a left-back under 24, comfortable in a high press...&rdquo;
                  </p>
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

            {/* Loading skeletons — appear after enough steps have streamed */}
            {isLoading && queryState.reasoning_steps.length >= 6 && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mt-6">
                <DossierCardSkeleton />
                <DossierCardSkeleton />
                <DossierCardSkeleton />
              </div>
            )}

            {/* Results */}
            {hasResults && <DossierCardGrid candidates={queryState.candidates} />}
          </div>
        </div>

        {/* Fixed chat input */}
        <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
      </main>
    </div>
  );
}
