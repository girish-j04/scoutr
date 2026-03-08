"use client";

import Image from "next/image";
import { useState, useRef, useEffect } from "react";
import { useClub } from "@/lib/ClubContext";

export default function ClubSwitcher() {
  const { activeClub, setActiveClub, clubs } = useClub();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <div ref={ref} className="relative flex-shrink-0">
      {/* Club identity + toggle */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-4 py-4 border-b border-pitch-700 hover:bg-pitch-800/60 transition-colors group"
        aria-expanded={open}
      >
        {/* Accent bar at top */}
        <div
          className="absolute top-0 left-0 right-0 h-[2px]"
          style={{ background: "var(--club-primary)" }}
        />
        <Image
          src={activeClub.badge_url}
          alt={`${activeClub.name} badge`}
          width={40}
          height={48}
          className="flex-shrink-0"
        />
        <div className="min-w-0 flex-1 text-left">
          <h1 className="font-bebas text-xl text-ink leading-tight truncate tracking-wide">
            {activeClub.name}
          </h1>
          <p className="text-[10px] text-ink-faint font-mono mt-0.5 tracking-wider uppercase">
            {activeClub.league} &middot; {activeClub.formation}
          </p>
        </div>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          className={`flex-shrink-0 text-ink-faint transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        >
          <path
            d="M2 4L6 8L10 4"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute top-full left-0 right-0 z-50 bg-pitch-900 border-b border-x border-pitch-700 shadow-2xl">
          {clubs.map((club) => (
            <button
              key={club.id}
              onClick={() => {
                setActiveClub(club);
                setOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-4 py-2.5 hover:bg-pitch-800 transition-colors text-left ${
                club.id === activeClub.id ? "bg-pitch-800/70" : ""
              }`}
            >
              <Image
                src={club.badge_url}
                alt={club.name}
                width={26}
                height={31}
                className="flex-shrink-0"
              />
              <div className="min-w-0 flex-1">
                <div className="text-sm font-body font-semibold text-ink truncate leading-tight">
                  {club.name}
                </div>
                <div className="text-[9px] font-mono text-ink-faint uppercase tracking-wider">
                  {club.league}
                </div>
              </div>
              {club.id === activeClub.id && (
                <div
                  className="ml-auto w-1.5 h-1.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: club.theme.primary }}
                />
              )}
            </button>
          ))}
          <div className="px-4 py-2 border-t border-pitch-700">
            <p className="text-[9px] font-mono text-ink-faint/50 uppercase tracking-widest text-center">
              Demo clubs
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
