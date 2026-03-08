"use client";

import { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ReasoningStep as ReasoningStepType } from "@/lib/types";
import ReasoningStepComponent from "./ReasoningStep";

interface AgentReasoningStreamProps {
  steps: ReasoningStepType[];
  isStreaming: boolean;
}

export default function AgentReasoningStream({
  steps,
  isStreaming,
}: AgentReasoningStreamProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [steps.length]);

  if (steps.length === 0 && !isStreaming) return null;

  return (
    <div className="px-1">
      {/* Header */}
      {isStreaming && steps.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-3 mb-4"
        >
          <div className="flex gap-1">
            {["scout", "valuation", "tactical", "orchestrator"].map((agent, i) => (
              <motion.div
                key={agent}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: i * 0.15, type: "spring", stiffness: 500 }}
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: "var(--club-primary)" }}
              />
            ))}
          </div>
          <span className="text-xs font-mono tracking-wider" style={{ color: "var(--club-primary)" }}>
            DEPLOYING AGENTS...
          </span>
        </motion.div>
      )}

      {/* Steps timeline */}
      <AnimatePresence>
        {steps.map((step, i) => (
          <ReasoningStepComponent key={i} step={step} index={i} />
        ))}
      </AnimatePresence>

      {/* Streaming indicator */}
      {isStreaming && steps.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-2 pl-9 pb-3"
        >
          <span className="flex gap-0.5">
            <span className="w-1 h-1 rounded-full animate-bounce [animation-delay:0ms]" style={{ backgroundColor: "var(--club-primary)" }} />
            <span className="w-1 h-1 rounded-full animate-bounce [animation-delay:150ms]" style={{ backgroundColor: "var(--club-primary)" }} />
            <span className="w-1 h-1 rounded-full animate-bounce [animation-delay:300ms]" style={{ backgroundColor: "var(--club-primary)" }} />
          </span>
          <span className="text-[10px] font-mono text-ink-faint">Processing...</span>
        </motion.div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
