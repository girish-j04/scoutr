"use client";

import { MonitoringAlert } from "@/lib/types";
import { AnimatedList } from "@/components/ui/animated-list";
import AlertCard from "./AlertCard";

export default function MonitoringFeed({ alerts }: { alerts: MonitoringAlert[] }) {
  return (
    <div className="mx-3 mt-4">
      <div className="flex items-center justify-between px-1 mb-2">
        <h3 className="stat-label">Monitoring Feed</h3>
        <span className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald animate-pulse-dot" />
          <span className="text-[9px] font-mono text-emerald tracking-wider">LIVE</span>
        </span>
      </div>
      <AnimatedList delay={800} className="gap-2">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </AnimatedList>
    </div>
  );
}
