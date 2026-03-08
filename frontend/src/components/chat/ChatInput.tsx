"use client";

import { useState } from "react";
import { GOLDEN_PATH_QUERY } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { TextAnimate } from "@/components/ui/text-animate";

interface ChatInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSubmit, isLoading }: ChatInputProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = () => {
    const q = query.trim();
    if (!q || isLoading) return;
    onSubmit(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-pitch-700 bg-pitch-950 px-4 py-3">
      <div className="flex items-end gap-3 max-w-4xl mx-auto">
        <Textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={GOLDEN_PATH_QUERY}
          disabled={isLoading}
          className="flex-1 max-h-[120px] resize-none bg-pitch-800 border-pitch-600 rounded-card px-4 py-3 text-sm font-body text-ink placeholder:text-ink-faint/50 focus-visible:ring-[var(--club-primary)]/50 focus-visible:border-[var(--club-primary)] disabled:opacity-50"
        />
        <Button
          onClick={handleSubmit}
          disabled={!query.trim() || isLoading}
          size="icon"
          className="flex-shrink-0 w-10 h-10 rounded-card active:scale-95 transition-all"
          style={{
            backgroundColor: "var(--club-primary)",
            color: "var(--club-primary-text)",
          }}
        >
          {isLoading ? (
            <span className="flex gap-0.5">
              <span className="w-1 h-1 bg-ink rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-1 h-1 bg-ink rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-1 h-1 bg-ink rounded-full animate-bounce [animation-delay:300ms]" />
            </span>
          ) : (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M3 8H13M13 8L9 4M13 8L9 12"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </Button>
      </div>
      <TextAnimate
        className="text-[10px] text-ink-faint/40 text-center mt-2 font-mono"
        animation="fadeIn"
        by="word"
        delay={0.5}
        duration={1}
        once
        as="p"
      >
        Describe the player you need. ScoutR agents will search, value, and assess tactical fit automatically.
      </TextAnimate>
    </div>
  );
}
