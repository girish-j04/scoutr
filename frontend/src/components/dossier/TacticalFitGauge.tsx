"use client";

import { motion } from "framer-motion";
import { NumberTicker } from "@/components/ui/number-ticker";

interface TacticalFitGaugeProps {
  score: number;
  size?: number;
}

export default function TacticalFitGauge({ score, size = 64 }: TacticalFitGaugeProps) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const offset = circumference - progress;

  const scoreColor =
    score >= 85 ? "var(--club-primary)" : score >= 70 ? "#22956E" : score >= 50 ? "#9CA89F" : "#C44E4E";

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1A2520"
          strokeWidth="3"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={scoreColor}
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <NumberTicker
          value={score}
          delay={0.5}
          className="font-mono font-bold text-base leading-none"
          style={{ color: scoreColor }}
        />
        <span className="text-[7px] font-mono text-ink-faint uppercase tracking-wider mt-0.5">
          FIT
        </span>
      </div>
    </div>
  );
}
