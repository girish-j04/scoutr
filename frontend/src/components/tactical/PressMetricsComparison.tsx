"use client";

import { motion } from "framer-motion";

interface MetricRow {
  label: string;
  playerValue: number;
  currentStarterValue: number;
  maxValue: number;
  unit?: string;
}

const CURRENT_STARTER_STATS = {
  ppda: 11.4,
  pressure_success_rate: 24.2,
  defensive_actions_per90: 10.1,
  progressive_carries: 3.2,
  xA: 0.06,
};

export default function PressMetricsComparison({
  playerStats,
  playerName,
}: {
  playerStats: {
    ppda: number;
    pressure_success_rate: number;
    defensive_actions_per90: number;
    progressive_carries: number;
    xA: number;
  };
  playerName: string;
}) {
  const metrics: MetricRow[] = [
    { label: "PPDA", playerValue: playerStats.ppda, currentStarterValue: CURRENT_STARTER_STATS.ppda, maxValue: 15 },
    { label: "Press %", playerValue: playerStats.pressure_success_rate, currentStarterValue: CURRENT_STARTER_STATS.pressure_success_rate, maxValue: 50, unit: "%" },
    { label: "Def/90", playerValue: playerStats.defensive_actions_per90, currentStarterValue: CURRENT_STARTER_STATS.defensive_actions_per90, maxValue: 20 },
    { label: "Prog C", playerValue: playerStats.progressive_carries, currentStarterValue: CURRENT_STARTER_STATS.progressive_carries, maxValue: 10 },
    { label: "xA", playerValue: playerStats.xA, currentStarterValue: CURRENT_STARTER_STATS.xA, maxValue: 0.4 },
  ];

  return (
    <div>
      {/* Legend */}
      <div className="flex items-center gap-4 mb-3">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-1.5 rounded-full bg-emerald" />
          <span className="text-[10px] font-mono text-ink-muted">{playerName}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-1.5 rounded-full bg-ink-faint/40" />
          <span className="text-[10px] font-mono text-ink-faint">Current Starter</span>
        </div>
      </div>

      {/* Metric rows */}
      <div className="space-y-3">
        {metrics.map((metric, i) => {
          const playerPct = Math.min((metric.playerValue / metric.maxValue) * 100, 100);
          const starterPct = Math.min((metric.currentStarterValue / metric.maxValue) * 100, 100);

          return (
            <div key={metric.label}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-mono text-ink-faint uppercase tracking-wider">
                  {metric.label}
                </span>
                <div className="flex gap-3">
                  <span className="text-[10px] font-mono font-medium text-emerald">
                    {metric.playerValue}{metric.unit || ""}
                  </span>
                  <span className="text-[10px] font-mono text-ink-faint">
                    {metric.currentStarterValue}{metric.unit || ""}
                  </span>
                </div>
              </div>
              <div className="relative h-3 flex flex-col gap-0.5">
                <div className="h-1.5 bg-pitch-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ background: "linear-gradient(90deg, #1B7A5A, #22956E)" }}
                    initial={{ width: 0 }}
                    animate={{ width: `${playerPct}%` }}
                    transition={{ duration: 0.6, delay: 0.2 + i * 0.08, ease: "easeOut" }}
                  />
                </div>
                <div className="h-1 bg-pitch-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full bg-ink-faint/30"
                    initial={{ width: 0 }}
                    animate={{ width: `${starterPct}%` }}
                    transition={{ duration: 0.6, delay: 0.3 + i * 0.08, ease: "easeOut" }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
