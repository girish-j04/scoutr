"use client";

import { DossierCandidate } from "@/lib/types";
import PitchDiagram from "./PitchDiagram";
import PressMetricsComparison from "./PressMetricsComparison";

export default function TacticalDeepDive({
  candidate,
}: {
  candidate: DossierCandidate;
}) {
  const { player, fit_explanation, formation_compatibility, heatmap_zones, comparable_transfers } = candidate;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
      {/* Left: Pitch diagram */}
      <div>
        <h4 className="stat-label mb-2">Positional Heatmap</h4>
        <PitchDiagram
          formation={formation_compatibility}
          heatmapZones={heatmap_zones}
        />
        <div className="mt-2 flex items-center gap-1.5">
          <span className="text-[9px] font-mono text-ink-faint">Formation:</span>
          <span className="text-[10px] font-mono font-medium text-ink-muted">
            {formation_compatibility}
          </span>
        </div>
      </div>

      {/* Right: Analysis */}
      <div className="space-y-5">
        {/* Fit explanation */}
        <div>
          <h4 className="stat-label mb-2">Tactical Fit Analysis</h4>
          <p className="text-sm text-ink-muted font-body leading-relaxed">
            {fit_explanation}
          </p>
        </div>

        {/* Press metrics comparison */}
        <div>
          <h4 className="stat-label mb-2">Press Metrics vs. Current Starter</h4>
          <PressMetricsComparison
            playerStats={{
              ppda: player.press_metrics.ppda,
              pressure_success_rate: player.press_metrics.pressure_success_rate,
              defensive_actions_per90: player.press_metrics.defensive_actions_per90,
              progressive_carries: player.progressive_carries,
              xA: player.xA,
            }}
            playerName={player.name}
          />
        </div>

        {/* Comparable transfers */}
        {comparable_transfers.length > 0 && (
          <div>
            <h4 className="stat-label mb-2">Comparable Transfers</h4>
            <div className="space-y-1.5">
              {comparable_transfers.map((t, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-[11px] font-body text-ink-muted py-1 border-b border-pitch-700 last:border-0"
                >
                  <span>
                    {t.player_name}{" "}
                    <span className="text-ink-faint">
                      ({t.from_club} → {t.to_club}, {t.year})
                    </span>
                  </span>
                  <span className="font-mono font-medium text-ink">
                    €{(t.fee / 1_000_000).toFixed(1)}M
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
