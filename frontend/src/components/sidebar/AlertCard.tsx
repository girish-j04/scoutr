"use client";

import { MonitoringAlert } from "@/lib/types";
import { Badge } from "@/components/ui/badge";

const urgencyStyles = {
  red: {
    border: "border-l-risk-red",
    dot: "bg-risk-red",
    label: "URGENT",
    badgeClass: "bg-risk-red/15 text-risk-red border-risk-red/20",
  },
  amber: {
    border: "border-l-gold",
    dot: "bg-gold",
    label: "WATCH",
    badgeClass: "bg-gold/15 text-gold border-gold/20",
  },
  green: {
    border: "border-l-risk-green",
    dot: "bg-risk-green",
    label: "OPPORTUNITY",
    badgeClass: "bg-risk-green/15 text-risk-green border-risk-green/20",
  },
};

function timeAgo(timestamp: string): string {
  const diff = Date.now() - new Date(timestamp).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function AlertCard({ alert }: { alert: MonitoringAlert }) {
  const style = urgencyStyles[alert.urgency] || urgencyStyles.amber;

  return (
    <div
      className={`card-surface border-l-2 ${style.border} p-2.5 transition-all duration-200 hover:bg-pitch-700 cursor-pointer`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className={`w-1.5 h-1.5 rounded-full ${style.dot} animate-pulse-dot`} />
        <span className="font-display font-semibold text-xs text-ink truncate flex-1">
          {alert.player_name}
        </span>
        <Badge
          variant="outline"
          className={`${style.badgeClass} text-[8px] h-4 px-1.5 rounded-sm font-mono`}
        >
          {style.label}
        </Badge>
      </div>
      <p className="text-[11px] text-ink-muted font-body leading-snug line-clamp-2">
        {alert.description}
      </p>
      <span className="block text-[9px] text-ink-faint font-mono mt-1">
        {timeAgo(alert.timestamp)}
      </span>
    </div>
  );
}
