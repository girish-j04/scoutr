"use client";

import { SquadGap } from "@/lib/types";

export default function SquadGapCard({ gap }: { gap: SquadGap }) {
  const urgencyColor =
    gap.months_remaining <= 3
      ? "border-l-risk-red"
      : gap.months_remaining <= 6
        ? "border-l-gold"
        : "border-l-risk-green";

  return (
    <div className="mx-3 mt-4">
      <h3 className="stat-label px-1 mb-2">Squad Priority</h3>
      <div
        className={`card-surface border-l-2 ${urgencyColor} p-3`}
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
              stroke="#D4A843"
              strokeWidth="1.2"
              fill="none"
            />
            <circle cx="7" cy="7" r="2" fill="#D4A843" />
          </svg>
          <span className="font-display font-bold text-sm text-gold">
            {gap.position}
          </span>
        </div>
        <p className="text-xs text-ink-muted font-body leading-relaxed">
          {gap.description}
        </p>
        <div className="mt-2 flex items-center gap-1.5">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-gold animate-pulse-dot" />
          <span className="text-[10px] font-mono text-ink-faint uppercase tracking-wider">
            {gap.months_remaining} months remaining
          </span>
        </div>
      </div>
    </div>
  );
}
