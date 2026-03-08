"use client";

import { motion } from "framer-motion";
import { Activity, ShieldAlert, TrendingUp } from "lucide-react";

interface MonitoredPlayer {
  id: string;
  name: string;
  status: "stable" | "declining" | "improving";
  urgency: "red" | "amber" | "green";
}

// No mock data needed, players are passed from parent

export default function MonitoredPlayers({ 
  players = [], 
  onSelect 
}: { 
  players?: any[], 
  onSelect?: (id: string) => void 
}) {
  const displayPlayers = players.length > 0 ? players : [];

  return (
    <div className="mx-3 mt-6">
      <div className="flex items-center justify-between px-1 mb-3">
        <h3 className="stat-label uppercase tracking-widest text-[10px] text-ink-faint">Monitored Squad</h3>
        <span className="text-[10px] font-mono text-ink-faint">{displayPlayers.length} Active</span>
      </div>

      <div className="space-y-1.5">
        {displayPlayers.length === 0 ? (
          <div className="px-3 py-4 border border-dashed border-pitch-700 rounded-sm text-center">
            <p className="text-[10px] text-ink-faint font-body italic">No players monitored</p>
          </div>
        ) : (
          displayPlayers.map((player) => (
            <motion.div
              layout
              key={player.player_id}
              onClick={() => onSelect?.(player.player_id)}
              className="group flex items-center justify-between p-2 card-surface hover:bg-pitch-700 cursor-pointer transition-colors border-l border-l-emerald/30"
            >
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-sm bg-emerald/10 flex items-center justify-center">
                  <Activity size={10} className="text-emerald" />
                </div>
                <div className="min-w-0">
                  <div className="text-[11px] font-display font-bold text-ink truncate max-w-[120px]">
                    {player.name}
                  </div>
                  <div className="text-[8px] font-mono text-ink-faint uppercase truncate">
                    {player.position}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-emerald animate-pulse" />
                <span className="text-[9px] font-mono text-emerald tracking-tight">LIVE</span>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
