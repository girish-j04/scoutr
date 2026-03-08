"use client";

import Image from "next/image";
import { ClubProfile } from "@/lib/types";

export default function ClubIdentityPanel({ club }: { club: ClubProfile }) {
  return (
    <div className="flex items-center gap-3 px-4 py-5 border-b border-pitch-700">
      <Image
        src={club.badge_url}
        alt={`${club.name} badge`}
        width={44}
        height={52}
        className="flex-shrink-0"
      />
      <div className="min-w-0">
        <h1 className="font-display font-extrabold text-base text-ink leading-tight truncate">
          {club.name}
        </h1>
        <p className="text-xs text-ink-faint font-body mt-0.5">
          {club.league} &middot; {club.formation}
        </p>
      </div>
    </div>
  );
}
