import { ClubProfile } from "./types";

export interface ClubTheme {
  primary: string;
  primaryMuted: string;
  primaryText: string;
}

export interface Club extends ClubProfile {
  id: string;
  theme: ClubTheme;
}

export const CLUBS: Club[] = [
  {
    id: "leeds",
    name: "Leeds United",
    league: "EFL Championship",
    formation: "4-3-3",
    badge_url: "/leeds-badge.svg",
    budget_total: 25_000_000,
    budget_remaining: 12_000_000,
    squad_gap: {
      position: "Left-back",
      description: "Left-back needed. Current starter contract expires in 4 months.",
      months_remaining: 4,
    },
    theme: {
      primary: "#FFD700",
      primaryMuted: "rgba(255, 215, 0, 0.15)",
      primaryText: "#0a0700",
    },
  },
  {
    id: "brentford",
    name: "Brentford FC",
    league: "EFL Championship",
    formation: "4-3-3",
    badge_url: "/brentford-badge.svg",
    budget_total: 18_000_000,
    budget_remaining: 8_500_000,
    squad_gap: {
      position: "Striker",
      description: "Centre-forward cover needed. Starting striker contract expires in 6 months.",
      months_remaining: 6,
    },
    theme: {
      primary: "#E30613",
      primaryMuted: "rgba(227, 6, 19, 0.15)",
      primaryText: "#ffffff",
    },
  },
  {
    id: "hamburger",
    name: "Hamburger SV",
    league: "Bundesliga 2",
    formation: "4-2-3-1",
    badge_url: "/hamburger-badge.svg",
    budget_total: 12_000_000,
    budget_remaining: 7_200_000,
    squad_gap: {
      position: "Defensive Midfielder",
      description: "Midfield anchor needed. First-choice DM out long-term with injury.",
      months_remaining: 8,
    },
    theme: {
      primary: "#005CA9",
      primaryMuted: "rgba(0, 92, 169, 0.15)",
      primaryText: "#ffffff",
    },
  },
  {
    id: "valencia",
    name: "Valencia CF",
    league: "La Liga 2",
    formation: "4-4-2",
    badge_url: "/valencia-badge.svg",
    budget_total: 15_000_000,
    budget_remaining: 9_000_000,
    squad_gap: {
      position: "Right Winger",
      description: "Wide attacker with pace needed. Contract expires in 3 months.",
      months_remaining: 3,
    },
    theme: {
      primary: "#FF6600",
      primaryMuted: "rgba(255, 102, 0, 0.15)",
      primaryText: "#ffffff",
    },
  },
];

export const DEFAULT_CLUB = CLUBS[0];
