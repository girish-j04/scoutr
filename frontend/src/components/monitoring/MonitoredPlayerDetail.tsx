"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Activity, Target, Shield, Zap, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { MonitoringAlert } from "@/lib/types";
import { NumberTicker } from "@/components/ui/number-ticker";

interface MonitoredPlayerDetailProps {
  player: any;
  alerts: any[];
  onClose: () => void;
}

export default function MonitoredPlayerDetail({ player, alerts, onClose }: MonitoredPlayerDetailProps) {
  // Find the most recent form alert for this player
  const formAlert = alerts.find(a => a.player_id === player.player_id && a.alert_type === "performance");
  const contractAlert = alerts.find(a => a.player_id === player.player_id && (a.alert_type === "urgency" || a.alert_type === "contract_urgency"));
  
  const formScore = formAlert?.form_score ?? 50;
  const matches = formAlert?.recent_matches ?? [];
  const styleFit = formAlert?.style_fit ?? "medium";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-pitch-950/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        className="w-full max-w-2xl card-surface overflow-hidden shadow-2xl border border-pitch-700"
        onClick={(e) => e.stopPropagation()}
        style={{ backgroundColor: "#1A2520" }}
      >
        {/* Header */}
        <div className="relative h-32 bg-gradient-to-br from-emerald/20 to-pitch-900 border-b border-pitch-700 p-6 flex items-end justify-between">
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-pitch-950/50 text-ink-faint hover:text-ink transition-colors"
          >
            <X size={20} />
          </button>
          
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="font-bebas text-4xl text-ink tracking-wide">{player.name}</h2>
              <div className="px-2 py-0.5 rounded-sm bg-emerald text-pitch-950 font-mono text-[10px] font-bold">
                MONITORED
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-ink-muted">
              <span>{player.club}</span>
              <span>&middot;</span>
              <span>{player.position}</span>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[10px] font-mono text-ink-faint uppercase tracking-widest block mb-1">Form Intensity</span>
            <div className="flex items-baseline gap-1">
              <span className="text-4xl font-bebas text-emerald">{formScore}</span>
              <span className="text-sm font-mono text-emerald/60">/100</span>
            </div>
          </div>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column: Form & Style */}
          <div className="space-y-6">
            <section>
              <h3 className="text-[10px] font-mono text-ink-faint uppercase tracking-widest mb-4 flex items-center gap-2">
                <Activity size={12} /> Live Performance Trend
              </h3>
              <div className="p-4 rounded-sm bg-pitch-900/50 border border-pitch-800">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-ink">Form Status</span>
                  <div className="flex items-center gap-2">
                    {formScore >= 70 ? (
                      <div className="flex items-center gap-1 text-emerald">
                        <TrendingUp size={16} />
                        <span className="text-xs font-bold uppercase">Trending Up</span>
                      </div>
                    ) : formScore >= 45 ? (
                      <div className="flex items-center gap-1 text-gold">
                        <Minus size={16} />
                        <span className="text-xs font-bold uppercase">Stable</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 text-red-400">
                        <TrendingDown size={16} />
                        <span className="text-xs font-bold uppercase">Declining</span>
                      </div>
                    )}
                  </div>
                </div>
                <p className="text-xs text-ink-muted leading-relaxed italic">
                  &ldquo;{formAlert?.description ?? "Maintaining baseline performance levels based on event consistency."}&rdquo;
                </p>
              </div>
            </section>

            <section>
              <h3 className="text-[10px] font-mono text-ink-faint uppercase tracking-widest mb-4 flex items-center gap-2">
                <Shield size={12} /> Tactical Intelligence
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-sm bg-pitch-900/50 border border-pitch-800">
                  <span className="text-[9px] font-mono text-ink-faint block mb-1">Style Fit</span>
                  <div className="text-sm font-bold text-ink uppercase">{styleFit}</div>
                </div>
                <div className="p-3 rounded-sm bg-pitch-900/50 border border-pitch-800">
                  <span className="text-[9px] font-mono text-ink-faint block mb-1">Market Volatility</span>
                  <div className="text-sm font-bold text-ink uppercase">Stable</div>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column: Recent Matches */}
          <div>
            <h3 className="text-[10px] font-mono text-ink-faint uppercase tracking-widest mb-4 flex items-center gap-2">
              <Zap size={12} /> Recent Match Statistics
            </h3>
            <div className="space-y-2">
              {matches.length > 0 ? (
                matches.map((m: any, idx: number) => (
                  <div 
                    key={idx}
                    className="p-3 rounded-sm bg-pitch-900/30 border border-pitch-800/50 flex items-center justify-between"
                  >
                    <div>
                      <div className="text-[10px] font-mono text-ink-faint">{m.match_date}</div>
                      <div className="text-xs font-bold text-ink">Match #{idx + 1}</div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="text-[9px] font-mono text-ink-faint">G/A</div>
                        <div className="text-xs font-bold text-emerald">{m.goals}/{m.assists}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-[9px] font-mono text-ink-faint">Rating</div>
                        <div className="text-xs font-bold text-gold">{m.rating}</div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="py-8 text-center border border-dashed border-pitch-800 rounded-sm">
                  <p className="text-[10px] text-ink-faint italic font-body">No recent match data available</p>
                </div>
              )}
            </div>
            
            {contractAlert && (
              <div className="mt-4 p-3 rounded-sm bg-red-400/10 border border-red-400/30">
                <div className="text-[10px] font-mono text-red-400 uppercase tracking-widest mb-1">Urgent Alert</div>
                <p className="text-[11px] text-ink-muted leading-tight">{contractAlert.description}</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-pitch-950/50 border-t border-pitch-700 flex justify-end">
          <button 
            onClick={onClose}
            className="px-4 py-2 rounded-sm bg-pitch-800 text-ink text-xs font-bold hover:bg-pitch-700 transition-colors border border-pitch-600"
          >
            DISMISS
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
