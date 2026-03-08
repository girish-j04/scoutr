"use client";

import { ContractRisk } from "@/lib/types";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";

const riskConfig: Record<ContractRisk, { color: string; label: string; detail: string }> = {
  red: { color: "bg-risk-red", label: "Expiring", detail: "Contract expires within 6 months — strongest negotiation leverage" },
  amber: { color: "bg-gold", label: "12-18mo", detail: "Contract expires in 12-18 months — club may be open to negotiate" },
  green: { color: "bg-risk-green", label: "18mo+", detail: "Contract has 18+ months remaining — weaker negotiation position" },
};

export default function ContractRiskDot({ risk }: { risk: ContractRisk }) {
  const config = riskConfig[risk];

  return (
    <Tooltip>
      <TooltipTrigger className="cursor-help">
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${config.color}`} />
          <span className="text-[10px] font-mono text-ink-faint uppercase tracking-wider">
            {config.label}
          </span>
        </div>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-[220px] text-[10px]">
        {config.detail}
      </TooltipContent>
    </Tooltip>
  );
}
