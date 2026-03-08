"use client";

import { NumberTicker } from "@/components/ui/number-ticker";
import { formatFee } from "@/lib/api";

interface BudgetGaugeProps {
  total: number;
  remaining: number;
}

export default function BudgetGauge({ total, remaining }: BudgetGaugeProps) {
  const spent = total - remaining;
  const pct = (remaining / total) * 100;

  return (
    <div className="mx-3 mt-4">
      <h3 className="stat-label px-1 mb-2">Transfer Budget</h3>
      <div className="card-surface p-3">
        <div className="flex items-baseline justify-between mb-2">
          <span className="font-mono font-bold text-lg text-ink">
            €<NumberTicker value={remaining / 1_000_000} decimalPlaces={1} className="text-ink font-mono font-bold text-lg" />M
          </span>
          <span className="text-[10px] text-ink-faint font-mono">
            of {formatFee(total)}
          </span>
        </div>
        <div className="w-full h-1.5 bg-pitch-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${pct}%`,
              background: `linear-gradient(90deg, #1B7A5A, #22956E)`,
            }}
          />
        </div>
        <div className="flex justify-between mt-1.5">
          <span className="text-[10px] text-ink-faint font-mono">
            {formatFee(spent)} spent
          </span>
          <span className="text-[10px] text-emerald font-mono font-medium">
            <NumberTicker value={Math.round(pct)} className="text-emerald font-mono font-medium text-[10px]" />% available
          </span>
        </div>
      </div>
    </div>
  );
}
