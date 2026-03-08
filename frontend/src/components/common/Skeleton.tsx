"use client";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return <div className={`skeleton ${className}`} />;
}

export function DossierCardSkeleton() {
  return (
    <div className="card-surface gold-accent-left p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-48" />
        </div>
        <Skeleton className="w-14 h-14 rounded-full" />
      </div>
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <Skeleton className="h-2 w-12" />
            <Skeleton className="h-1.5 flex-1" />
            <Skeleton className="h-2 w-8" />
          </div>
        ))}
      </div>
      <div className="pt-2 border-t border-pitch-700 flex justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-3 w-16" />
      </div>
    </div>
  );
}

export function ReasoningStreamSkeleton() {
  return (
    <div className="space-y-4 px-1">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="flex gap-3">
          <Skeleton className="w-6 h-6 rounded-full shrink-0" />
          <div className="flex-1 space-y-1.5">
            <Skeleton className="h-2 w-20" />
            <Skeleton className="h-3 w-48" />
            <Skeleton className="h-2.5 w-64" />
          </div>
        </div>
      ))}
    </div>
  );
}
