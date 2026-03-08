"use client";

import { motion } from "framer-motion";
import { TypingAnimation } from "@/components/ui/typing-animation";
import { ReasoningStep as ReasoningStepType, AgentType } from "@/lib/types";

const agentConfig: Record<AgentType, { icon: React.ReactNode; label: string; color: string }> = {
  orchestrator: {
    label: "Orchestrator",
    color: "#E8E6E1",
    icon: (
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.2" />
        <circle cx="6" cy="6" r="2" fill="currentColor" />
      </svg>
    ),
  },
  scout: {
    label: "Scout Agent",
    color: "#22956E",
    icon: (
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <circle cx="5" cy="5" r="3.5" stroke="currentColor" strokeWidth="1.2" />
        <path d="M8 8L11 11" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      </svg>
    ),
  },
  valuation: {
    label: "Valuation Agent",
    color: "#D4A843",
    icon: (
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M1 11V5H3V11H1Z" fill="currentColor" />
        <path d="M5 11V3H7V11H5Z" fill="currentColor" />
        <path d="M9 11V1H11V11H9Z" fill="currentColor" />
      </svg>
    ),
  },
  tactical: {
    label: "Tactical Fit Agent",
    color: "#3D9E6F",
    icon: (
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <rect x="1" y="1" width="10" height="10" rx="1" stroke="currentColor" strokeWidth="1.2" />
        <line x1="1" y1="6" x2="11" y2="6" stroke="currentColor" strokeWidth="0.8" />
        <circle cx="3" cy="8" r="1" fill="currentColor" />
        <circle cx="6" cy="4" r="1" fill="currentColor" />
        <circle cx="9" cy="3" r="1" fill="currentColor" />
      </svg>
    ),
  },
  monitoring: {
    label: "Monitoring Agent",
    color: "#C44E4E",
    icon: (
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M6 1V4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        <circle cx="6" cy="7" r="4" stroke="currentColor" strokeWidth="1.2" />
        <path d="M6 5.5V7L7.5 8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      </svg>
    ),
  },
};

export default function ReasoningStepComponent({
  step,
  index,
}: {
  step: ReasoningStepType;
  index: number;
}) {
  const config = agentConfig[step.agent];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.08, ease: "easeOut" }}
      className="flex gap-3 group"
    >
      {/* Timeline connector */}
      <div className="flex flex-col items-center pt-1">
        <div
          className="w-6 h-6 rounded-full flex items-center justify-center border"
          style={{
            color: config.color,
            borderColor: `${config.color}40`,
            backgroundColor: `${config.color}10`,
          }}
        >
          {config.icon}
        </div>
        <div className="w-px flex-1 bg-pitch-700 mt-1" />
      </div>

      {/* Content */}
      <div className="pb-4 min-w-0 flex-1">
        <div className="flex items-center gap-2 mb-0.5">
          <span
            className="text-[10px] font-mono uppercase tracking-wider"
            style={{ color: config.color }}
          >
            {config.label}
          </span>
        </div>
        <p className="text-xs font-display font-semibold text-ink leading-snug">
          {step.step}
        </p>
        <TypingAnimation
          className="text-[11px] text-ink-muted font-body mt-0.5 leading-relaxed"
          duration={15}
          delay={index * 0.08 * 1000 + 200}
          showCursor={false}
          startOnView={false}
          as="p"
        >
          {step.detail}
        </TypingAnimation>
      </div>
    </motion.div>
  );
}
