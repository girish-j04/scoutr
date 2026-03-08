"use client";

import { useState } from "react";
import { DossierCandidate } from "@/lib/types";
import { exportPDF, triggerDownload } from "@/lib/api";
import { Button } from "@/components/ui/button";

export default function ExportButton({ candidate }: { candidate: DossierCandidate }) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExporting(true);
    try {
      const blob = await exportPDF(candidate);
      triggerDownload(blob, `ScoutR_${candidate.player.name.replace(/\s+/g, "_")}_Dossier.pdf`);
    } catch {
      console.warn("PDF export not available. Backend endpoint not connected yet.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Button
      onClick={handleExport}
      disabled={isExporting}
      variant="outline"
      size="sm"
      className="gap-1.5 text-[11px] font-mono text-ink-muted border-pitch-600 hover:border-emerald hover:text-emerald bg-transparent"
    >
      {isExporting ? (
        <>
          <svg className="animate-spin w-3 h-3" viewBox="0 0 12 12" fill="none">
            <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.5" strokeDasharray="20" strokeLinecap="round" />
          </svg>
          Generating...
        </>
      ) : (
        <>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M6 2V8M6 8L3.5 5.5M6 8L8.5 5.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M2 9.5H10" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
          </svg>
          Export PDF
        </>
      )}
    </Button>
  );
}
