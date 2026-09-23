import type { Direction, District, DistrictId, IndicatorId, Initiative } from '../types';
export interface IndicatorMetadata {
  id: IndicatorId; direction: Direction; name: string; weight: number; higher_is_better: boolean;
}
export interface Synergy {
  first_initiative_id: string; second_initiative_id: string;
  bonuses: { indicator: IndicatorId; delta: number }[];
}
export interface Catalog {
  budget: number; required_decisions: number; max_per_direction: number; horizon: number;
  critical_threshold: number; baseline_score: number; baseline_n_crit: number; weakest_district: DistrictId;
  districts: District[]; initiatives: Initiative[];
  indicator_metadata: Record<IndicatorId, IndicatorMetadata>;
  indicator_weights: Record<IndicatorId, number>; direction_weights: Record<Direction, number>;
  population_shares: Record<DistrictId, number>;
  baseline_indicators: Record<DistrictId, Record<IndicatorId, number>>;
  baseline_district_scores: Record<DistrictId, number>;
  synergies: Synergy[];
  incompatibilities: { first_initiative_id: string; second_initiative_id: string; scope: string }[];
}
export interface ValidationIssue { code: string; message: string }
export interface InvalidSimulation {
  valid: false; errors: ValidationIssue[]; budget_used: number | null; budget_remaining: number | null;
}
export interface SimulationResult {
  valid: true; budget_used: number; budget_remaining: number;
  score_before: number; score_after: number; score_delta: number;
  d_avg_before: number; d_avg_after: number; n_crit_before: number; n_crit_after: number;
  weakest_district_before: DistrictId; weakest_district_after: DistrictId;
  min_district_score_before: number; min_district_score_after: number;
  district_scores_before: Record<DistrictId, number>; district_scores_after: Record<DistrictId, number>;
  district_score_changes: Record<DistrictId, number>;
  indicators_before: Record<DistrictId, Record<IndicatorId, number>>;
  indicators_after: Record<DistrictId, Record<IndicatorId, number>>;
  indicator_changes: Record<DistrictId, Record<IndicatorId, number>>;
  triggered_synergies: { synergy: Synergy; district: DistrictId }[];
}
export type SimulationResponse = SimulationResult | InvalidSimulation;
export interface AIAnalysis {
  summary: string; strengths: string[]; risks: string[]; tradeoffs: string[]; recommendations: string[];
}
