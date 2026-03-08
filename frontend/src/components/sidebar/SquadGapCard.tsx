"use client";

import { SquadGap } from "@/lib/types";

export default function SquadGapCard({ gap }: { gap: SquadGap }) {
  return (
    <div className="mx-3 mt-4">
      <h3 className="stat-label px-1 mb-2">Squad Priority</h3>
      <div
        className="card-surface p-3"
        style={{ borderLeftWidth: "2px", borderLeftStyle: "solid", borderLeftColor: "var(--club-primary)" }}
      >
        <div className="flex items-center gap-2 mb-1.5">
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            className="flex-shrink-0"
          >
            <path
              d="M7 1L13 4.5V9.5L7 13L1 9.5V4.5L7 1Z"
              stroke="var(--club-primary)"
              strokeWidth="1.2"
              fill="none"
            />
            <circle cx="7" cy="7" r="2" fill="var(--club-primary)" />
          </svg>
          <span className="font-bebas text-base tracking-wider" style={{ color: "var(--club-primary)" }}>
            {gap.position}
          </span>
        </div>
        <p className="text-xs text-ink-muted font-body leading-relaxed">
          {gap.description}
        </p>
        <div className="mt-2 flex items-center gap-1.5">
          <span
            className="inline-block w-1.5 h-1.5 rounded-full animate-pulse-dot"
            style={{ backgroundColor: "var(--club-primary)" }}
          />
          <span className="text-[10px] font-mono text-ink-faint uppercase tracking-wider">
            {gap.months_remaining} months remaining
          </span>
        </div>
      </div>
    </div>
  );
}
