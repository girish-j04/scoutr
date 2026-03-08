"use client";

import { motion } from "framer-motion";
import { DossierCandidate } from "@/lib/types";
import { MagicCard } from "@/components/ui/magic-card";
import { BorderBeam } from "@/components/ui/border-beam";
import { NumberTicker } from "@/components/ui/number-ticker";
import { Badge } from "@/components/ui/badge";
import TacticalFitGauge from "./TacticalFitGauge";
import StatBar from "./StatBar";
import ContractRiskDot from "./ContractRiskDot";

interface DossierCardProps {
  candidate: DossierCandidate;
  index: number;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

export default function DossierCard({
  candidate,
  index,
  isExpanded,
  onToggleExpand,
}: DossierCardProps) {
  const { player, rank, fee_range, contract_risk, tactical_fit_score, ranking_reason } = candidate;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.12, ease: "easeOut" }}
      className={`rounded-card cursor-pointer group relative ${isExpanded ? "ring-1 ring-gold/30" : ""}`}
      style={{ borderRadius: "4px" }}
    >
      <MagicCard
        gradientColor="#2D5A3D"
        gradientOpacity={0.5}
        gradientFrom="#D4A843"
        gradientTo="#1B7A5A"
        gradientSize={220}
        className="rounded-card"
      >
        {/* Inner content — click handler lives here, on the actual visible surface */}
        <div
          onClick={onToggleExpand}
          className="relative border-l-2 border-l-gold p-4 select-none"
          style={{
            backgroundColor: "#1A2520",
            borderRadius: "inherit",
            borderTop: "1px solid #243530",
            borderRight: "1px solid #243530",
            borderBottom: "1px solid #243530",
          }}
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Badge
                  variant={rank === 1 ? "default" : "outline"}
                  className={
                    rank === 1
                      ? "bg-gold/20 text-gold border-gold/30 font-mono text-[9px] h-5 px-1.5 rounded-sm"
                      : rank === 2
                        ? "bg-transparent text-ink-muted border-ink-faint/20 font-mono text-[9px] h-5 px-1.5 rounded-sm"
                        : "bg-transparent text-ink-faint border-ink-faint/10 font-mono text-[9px] h-5 px-1.5 rounded-sm"
                  }
                >
                  #{rank}
                </Badge>
                <h3 className="font-display font-extrabold text-base text-ink truncate leading-tight">
                  {player.name}
                </h3>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] text-ink-muted font-body">
                <span>{player.club}</span>
                <span className="text-ink-faint">&middot;</span>
                <span>{player.age}y</span>
                <span className="text-ink-faint">&middot;</span>
                <span>{player.position}</span>
                <span className="text-ink-faint">&middot;</span>
                <span>{player.nationality}</span>
              </div>
            </div>
            <TacticalFitGauge score={tactical_fit_score} size={56} />
          </div>

          {/* Stats */}
          <div className="space-y-1.5 mb-3">
            <StatBar label="PPDA" value={player.press_metrics.ppda} maxValue={15} delay={index * 0.05} tooltip="Passes Per Defensive Action — lower is more aggressive pressing" />
            <StatBar label="Press %" value={player.press_metrics.pressure_success_rate} maxValue={50} delay={index * 0.05 + 0.05} unit="%" tooltip="Percentage of pressures that win possession" />
            <StatBar label="Prog C" value={player.progressive_carries} maxValue={10} delay={index * 0.05 + 0.1} tooltip="Progressive carries per 90 minutes" />
            <StatBar label="xA" value={player.xA} maxValue={0.4} delay={index * 0.05 + 0.15} tooltip="Expected assists per 90 minutes" />
            <StatBar label="Def/90" value={player.press_metrics.defensive_actions_per90} maxValue={20} delay={index * 0.05 + 0.2} tooltip="Defensive actions per 90 minutes" />
          </div>

          {/* Footer */}
          <div className="flex items-end justify-between pt-2" style={{ borderTop: "1px solid #243530" }}>
            <div>
              <span className="text-[9px] font-mono text-ink-faint uppercase tracking-wider block mb-0.5">
                Fee Range
              </span>
              <span className="font-mono font-bold text-sm text-ink">
                €<NumberTicker value={fee_range.low / 1_000_000} decimalPlaces={1} className="text-ink font-mono font-bold text-sm" />M
                <span className="text-ink-faint mx-1">–</span>
                €<NumberTicker value={fee_range.high / 1_000_000} decimalPlaces={1} className="text-ink font-mono font-bold text-sm" />M
              </span>
            </div>
            <ContractRiskDot risk={contract_risk} />
          </div>

          {/* Ranking reason */}
          <p className="text-[11px] text-ink-muted font-body italic leading-relaxed mt-3 line-clamp-2">
            &ldquo;{ranking_reason}&rdquo;
          </p>

          {/* Expand chevron */}
          <div className="flex justify-center mt-2">
            <motion.svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
              className="text-ink-faint group-hover:text-ink-muted transition-colors"
            >
              <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </motion.svg>
          </div>
        </div>

        {/* BorderBeam on rank 1 only */}
        {rank === 1 && (
          <BorderBeam size={80} duration={8} colorFrom="#D4A843" colorTo="#1B7A5A" borderWidth={1} />
        )}
      </MagicCard>
    </motion.div>
  );
}
