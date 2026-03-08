"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { DossierCandidate } from "@/lib/types";
import DossierCard from "./DossierCard";
import TacticalDeepDive from "../tactical/TacticalDeepDive";
import ExportButton from "../ExportButton";

export default function DossierCardGrid({
  candidates,
  watchlist = [],
  onWatch,
}: {
  candidates: DossierCandidate[];
  watchlist?: string[];
  onWatch?: (id: string) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const expandedCandidate = candidates.find(
    (c) => c.player.player_id === expandedId
  );

  return (
    <div className="space-y-6">
      {/* Results header */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="font-display font-bold text-sm text-ink">Recommended Candidates</h2>
          <p className="text-[11px] text-ink-faint font-body mt-0.5">
            {candidates.length} players ranked by tactical fit, fee, and contract urgency
          </p>
        </div>
      </motion.div>

      {/* Cards grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {candidates.map((candidate, i) => (
          <DossierCard
            key={candidate.player.player_id}
            candidate={candidate}
            index={i}
            isWatched={watchlist.includes(candidate.player.player_id)}
            onWatch={onWatch}
            isExpanded={expandedId === candidate.player.player_id}
            onToggleExpand={() =>
              setExpandedId(
                expandedId === candidate.player.player_id
                  ? null
                  : candidate.player.player_id
              )
            }
          />
        ))}
      </div>

      {/* Tactical deep dive — shown below cards when expanded */}
      <AnimatePresence mode="wait">
        {expandedCandidate && (
          <motion.div
            key={expandedCandidate.player.player_id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
          >
            <div
              style={{
                backgroundColor: "#1A2520",
                border: "1px solid #243530",
                borderRadius: "4px",
                padding: "20px",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-display font-bold text-sm text-ink">
                  Tactical Deep Dive — {expandedCandidate.player.name}
                </h3>
                <ExportButton candidate={expandedCandidate} />
              </div>
              <TacticalDeepDive candidate={expandedCandidate} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
