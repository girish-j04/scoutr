export interface PressMetrics {
  ppda: number;
  pressure_success_rate: number;
  defensive_actions_per90: number;
}

export interface Player {
  player_id: string;
  name: string;
  club: string;
  league: string;
  age: number;
  position: string;
  nationality: string;
  contract_expiry: string;
  market_value: number;
  press_metrics: PressMetrics;
  progressive_carries: number;
  xA: number;
  xG: number;
}

export interface FeeRange {
  low: number;
  mid: number;
  high: number;
}

export type ContractRisk = "green" | "amber" | "red";

export interface DossierCandidate {
  player: Player;
  rank: number;
  ranking_reason: string;
  tactical_fit_score: number;
  fit_explanation: string;
  heatmap_zones: string[];
  formation_compatibility: string;
  fee_range: FeeRange;
  contract_risk: ContractRisk;
  scouting_summary: string;
  comparable_transfers: ComparableTransfer[];
}

export interface ComparableTransfer {
  player_name: string;
  from_club: string;
  to_club: string;
  fee: number;
  year: number;
}

export type AgentType = "scout" | "valuation" | "tactical" | "monitoring" | "orchestrator";

export interface ReasoningStep {
  step: string;
  detail: string;
  agent: AgentType;
}

export type AlertUrgency = "red" | "amber" | "green";

export interface MonitoringAlert {
  id: string;
  player_name: string;
  player_id: string;
  alert_type: "urgency" | "opportunity";
  urgency: AlertUrgency;
  description: string;
  timestamp: string;
}

export interface SquadGap {
  position: string;
  description: string;
  months_remaining: number;
}

export interface ClubProfile {
  name: string;
  league: string;
  formation: string;
  badge_url: string;
  budget_total: number;
  budget_remaining: number;
  squad_gap: SquadGap;
}

export interface QueryState {
  status: "idle" | "streaming" | "complete" | "error";
  query: string;
  reasoning_steps: ReasoningStep[];
  candidates: DossierCandidate[];
  error?: string;
}
