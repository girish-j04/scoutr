import { ClubProfile, DossierCandidate, MonitoringAlert, ReasoningStep } from "./types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const GOLDEN_PATH_QUERY =
  "Find me a left-back under 24, comfortable in a high press, contract expiring within 12 months, available for under €7M, preferably from a league with similar intensity to the Championship.";

export const LEEDS_PROFILE: ClubProfile = {
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
};

export const MOCK_REASONING_STEPS: ReasoningStep[] = [
  {
    step: "Parsing query",
    detail: "Extracting criteria: position=LB, age<24, press_intensity=high, contract<12mo, fee<€7M",
    agent: "orchestrator",
  },
  {
    step: "Searching player database",
    detail: "Scanning 2,847 players across 12 leagues matching positional and age criteria",
    agent: "scout",
  },
  {
    step: "Filtering by press metrics",
    detail: "Applied PPDA and pressure success rate filters — 47 candidates remain",
    agent: "scout",
  },
  {
    step: "Ranking candidates",
    detail: "Weighted scoring: tactical fit 40%, fee fit 30%, contract urgency 30%",
    agent: "scout",
  },
  {
    step: "Estimating market value",
    detail: "Cross-referencing comparable transfers for top 3 candidates",
    agent: "valuation",
  },
  {
    step: "Assessing contract risk",
    detail: "Evaluating contract expiry timelines and club financial positions",
    agent: "valuation",
  },
  {
    step: "Computing tactical fit",
    detail: "Analysing positional heatmaps against Leeds United 4-3-3 system",
    agent: "tactical",
  },
  {
    step: "Generating dossiers",
    detail: "Compiling scouting reports for 3 recommended candidates",
    agent: "orchestrator",
  },
];

export const MOCK_CANDIDATES: DossierCandidate[] = [
  {
    player: {
      player_id: "p001",
      name: "Sergio Gómez",
      club: "RSC Anderlecht",
      league: "Belgian Pro League",
      age: 23,
      position: "Left-back",
      nationality: "Spain",
      contract_expiry: "2026-06",
      market_value: 5_500_000,
      press_metrics: {
        ppda: 8.2,
        pressure_success_rate: 34.1,
        defensive_actions_per90: 14.7,
      },
      progressive_carries: 6.3,
      xA: 0.18,
      xG: 0.04,
    },
    rank: 1,
    ranking_reason:
      "Elite pressing numbers in a high-intensity league, strong progressive carrying ability, and contract situation creates negotiation leverage.",
    tactical_fit_score: 91,
    fit_explanation:
      "Gómez's high defensive line positioning and aggressive pressing patterns are an excellent match for Leeds' 4-3-3 system. His progressive carries from deep would add a dimension currently missing from the left side. Press metrics rank in the 94th percentile for full-backs in comparable leagues.",
    heatmap_zones: ["left-wing", "left-halfspace", "left-back"],
    formation_compatibility: "4-3-3",
    fee_range: { low: 3_800_000, mid: 5_200_000, high: 6_500_000 },
    contract_risk: "amber",
    scouting_summary:
      "Technically gifted left-back with elite pressing numbers. Belgian league intensity translates well to the Championship. Contract expiry in 14 months creates a strong negotiation position.",
    comparable_transfers: [
      { player_name: "Ian Maatsen", from_club: "Chelsea", to_club: "Burnley", fee: 3_500_000, year: 2023 },
      { player_name: "Pervis Estupiñán", from_club: "Villarreal", to_club: "Brighton", fee: 15_000_000, year: 2022 },
    ],
  },
  {
    player: {
      player_id: "p002",
      name: "Maximilian Mittelstädt",
      club: "Hertha BSC",
      league: "Bundesliga 2",
      age: 22,
      position: "Left-back",
      nationality: "Germany",
      contract_expiry: "2026-03",
      market_value: 4_200_000,
      press_metrics: {
        ppda: 7.9,
        pressure_success_rate: 31.8,
        defensive_actions_per90: 13.2,
      },
      progressive_carries: 5.8,
      xA: 0.14,
      xG: 0.03,
    },
    rank: 2,
    ranking_reason:
      "Strong Bundesliga 2 performer with proven pressing credentials. Contract expires in under 12 months — could be available at a significant discount.",
    tactical_fit_score: 84,
    fit_explanation:
      "Mittelstädt plays in a high-pressing Hertha system and his defensive positioning suits a 4-3-3. Slightly less progressive in possession than Gómez but more disciplined defensively. Would integrate quickly into Leeds' system.",
    heatmap_zones: ["left-back", "left-halfspace"],
    formation_compatibility: "4-3-3",
    fee_range: { low: 2_500_000, mid: 3_800_000, high: 5_000_000 },
    contract_risk: "red",
    scouting_summary:
      "Reliable, defensively disciplined left-back from a comparable second-tier league. Contract situation is the strongest lever — 9 months remaining. Bundesliga 2 physicality maps well to the Championship.",
    comparable_transfers: [
      { player_name: "Angeliño", from_club: "PSV", to_club: "Man City", fee: 5_300_000, year: 2019 },
    ],
  },
  {
    player: {
      player_id: "p003",
      name: "Quentin Merlin",
      club: "FC Nantes",
      league: "Ligue 1",
      age: 21,
      position: "Left-back",
      nationality: "France",
      contract_expiry: "2026-08",
      market_value: 6_000_000,
      press_metrics: {
        ppda: 9.1,
        pressure_success_rate: 29.4,
        defensive_actions_per90: 11.8,
      },
      progressive_carries: 7.1,
      xA: 0.21,
      xG: 0.05,
    },
    rank: 3,
    ranking_reason:
      "Highest ceiling of the three candidates. Elite progressive carrying and creative output from full-back. Press metrics slightly below the other two but age profile offers long-term upside.",
    tactical_fit_score: 78,
    fit_explanation:
      "Merlin is the most attack-minded option. His progressive carries and xA numbers are outstanding for a full-back, but his pressing intensity is slightly below Leeds' system requirements. Would need coaching adjustment in the defensive phase.",
    heatmap_zones: ["left-wing", "left-halfspace", "attacking-third"],
    formation_compatibility: "4-3-3",
    fee_range: { low: 4_500_000, mid: 5_800_000, high: 7_000_000 },
    contract_risk: "green",
    scouting_summary:
      "Young, high-ceiling full-back with exceptional attacking output from Ligue 1. The most creative option but carries more tactical adaptation risk. Fee at the upper end of the budget range.",
    comparable_transfers: [
      { player_name: "Nuno Mendes", from_club: "Sporting CP", to_club: "PSG", fee: 7_000_000, year: 2021 },
      { player_name: "Rayan Aït-Nouri", from_club: "Angers", to_club: "Wolves", fee: 11_000_000, year: 2021 },
    ],
  },
];

export const MOCK_ALERTS: MonitoringAlert[] = [
  {
    id: "a001",
    player_name: "Sergio Gómez",
    player_id: "p001",
    alert_type: "opportunity",
    urgency: "amber",
    description: "Anderlecht reported to be open to January negotiations. Contract talks stalled since October.",
    timestamp: "2025-12-14T09:30:00Z",
  },
  {
    id: "a002",
    player_name: "Maximilian Mittelstädt",
    player_id: "p002",
    alert_type: "urgency",
    urgency: "red",
    description: "Stuttgart and Wolfsburg scouts spotted at Hertha's last 2 matches. Competition increasing.",
    timestamp: "2025-12-13T16:45:00Z",
  },
  {
    id: "a003",
    player_name: "Quentin Merlin",
    player_id: "p003",
    alert_type: "opportunity",
    urgency: "green",
    description: "Nantes under FFP pressure — likely to accept offers below market value in the January window.",
    timestamp: "2025-12-12T11:00:00Z",
  },
];

export const FORMATION_POSITIONS: Record<string, { x: number; y: number; label: string }[]> = {
  "4-3-3": [
    { x: 50, y: 90, label: "GK" },
    { x: 20, y: 70, label: "LB" },
    { x: 40, y: 73, label: "CB" },
    { x: 60, y: 73, label: "CB" },
    { x: 80, y: 70, label: "RB" },
    { x: 30, y: 50, label: "CM" },
    { x: 50, y: 45, label: "CM" },
    { x: 70, y: 50, label: "CM" },
    { x: 20, y: 25, label: "LW" },
    { x: 50, y: 20, label: "ST" },
    { x: 80, y: 25, label: "RW" },
  ],
};

export const HEATMAP_ZONE_COORDS: Record<string, { cx: number; cy: number; rx: number; ry: number }> = {
  "left-back": { cx: 20, cy: 70, rx: 10, ry: 12 },
  "left-halfspace": { cx: 28, cy: 50, rx: 12, ry: 14 },
  "left-wing": { cx: 15, cy: 30, rx: 10, ry: 15 },
  "attacking-third": { cx: 40, cy: 22, rx: 18, ry: 10 },
  "right-back": { cx: 80, cy: 70, rx: 10, ry: 12 },
  "right-halfspace": { cx: 72, cy: 50, rx: 12, ry: 14 },
  "right-wing": { cx: 85, cy: 30, rx: 10, ry: 15 },
  "central-midfield": { cx: 50, cy: 48, rx: 14, ry: 12 },
};
