"use client";

import { motion } from "framer-motion";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";

interface StatBarProps {
  label: string;
  value: number;
  maxValue: number;
  delay?: number;
  unit?: string;
  tooltip?: string;
}

export default function StatBar({
  label,
  value,
  maxValue,
  delay = 0,
  unit = "",
  tooltip,
}: StatBarProps) {
  const pct = Math.min((value / maxValue) * 100, 100);

  const labelElement = (
    <span className="text-[10px] font-mono text-ink-faint w-16 text-right shrink-0 uppercase tracking-wider">
      {label}
    </span>
  );

  return (
    <div className="flex items-center gap-2">
      {tooltip ? (
        <Tooltip>
          <TooltipTrigger className="cursor-help">
            {labelElement}
          </TooltipTrigger>
          <TooltipContent side="left" className="max-w-[200px] text-[10px]">
            {tooltip}
          </TooltipContent>
        </Tooltip>
      ) : (
        labelElement
      )}
      <div className="flex-1 h-1.5 bg-pitch-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{
            background: "linear-gradient(90deg, var(--club-primary), color-mix(in srgb, var(--club-primary) 70%, white))",
          }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, delay: 0.4 + delay, ease: "easeOut" }}
        />
      </div>
      <span className="text-[10px] font-mono font-medium text-ink w-10 shrink-0">
        {value}
        {unit}
      </span>
    </div>
  );
}
