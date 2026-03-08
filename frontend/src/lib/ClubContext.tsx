"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { Club, CLUBS, DEFAULT_CLUB } from "./clubs";

interface ClubContextValue {
  activeClub: Club;
  setActiveClub: (club: Club) => void;
  clubs: Club[];
}

const ClubContext = createContext<ClubContextValue>({
  activeClub: DEFAULT_CLUB,
  setActiveClub: () => {},
  clubs: CLUBS,
});

export function ClubProvider({ children }: { children: ReactNode }) {
  const [activeClub, setActiveClub] = useState<Club>(DEFAULT_CLUB);

  return (
    <ClubContext.Provider value={{ activeClub, setActiveClub, clubs: CLUBS }}>
      <div
        style={
          {
            "--club-primary": activeClub.theme.primary,
            "--club-primary-muted": activeClub.theme.primaryMuted,
            "--club-primary-text": activeClub.theme.primaryText,
            display: "contents",
          } as React.CSSProperties
        }
      >
        {children}
      </div>
    </ClubContext.Provider>
  );
}

export function useClub() {
  return useContext(ClubContext);
}
