export interface Explosive {
  id: number;
  name: string;
  pressure_equivalency: number;
  impulse_equivalency: number;
  general_equivalency?: number;
  detonation_velocity?: number;
  density?: number;
}

export interface MaterialProfile {
  id: number;
  material_id: number;
  profile_name: string;
  family: string;
  density: number;
  compressive_strength: number;
  tensile_strength: number;
  failure_mode: string;
  strain_rate_factor?: number;
  failure_category: string;
  damage_mechanism: string;
  notes: string;
  minor_pressure: number;
  minor_impulse: number;
  moderate_pressure: number;
  moderate_impulse: number;
  severe_pressure: number;
  severe_impulse: number;
  failure_pressure: number;
  failure_impulse: number;
  source_title?: string;
  source_year?: number;
  confidence_level?: string;
  failure_description?: string;
  threshold_source_type?: string;
  applicability_notes?: string;
}

export interface Scenario {
  id?: number;
  name: string;
  explosive_id: number;
  explosive_name?: string;
  charge_weight: number;
  distance: number;
  burst_type: 'Free Air' | 'Air' | 'Surface';
  unit_system: 'Metric' | 'Imperial';
  created_at?: string;
}

export interface ScenarioSavePayload {
  id?: number;
  name: string;
  explosiveId: number;
  chargeWeight: number;
  distance: number;
  burstType: 'Free Air' | 'Air' | 'Surface';
  unitSystem: 'Metric' | 'Imperial';
}

export interface BlastResults {
  scaled_distance: number;
  incident_pressure: number;
  reflected_pressure: number;
  dynamic_pressure: number;
  positive_impulse: number;
  positive_duration: number;
  negative_duration: number;
  arrival_time: number;
  model_used: string;
  model_version: string;
  shock_front_velocity?: number;
  particle_velocity?: number;
  decay_parameter?: number;
}

export interface DamageAssessment {
  profile_id: number;
  profile_name: string;
  family: string;
  failure_category: string;
  damage_level: 'Safe' | 'Minor' | 'Moderate' | 'Severe' | 'Failure';
  damage_state: string;
  severity_score: number;
  pressure_ratio: number;
  impulse_ratio: number;
  damage_index: number;
  controlling_mode: 'Pressure' | 'Impulse';
  damage_mechanism: string;
  assessment_reason: string;
  confidence_level?: string;
  source_reference?: string;
  response_model_version?: string;
}

export interface UnitDefinition {
  id: number;
  quantity: string;
  unit_symbol: string;
  conversion_factor: number;
  is_base: number;
}

export interface UfcReference {
  id: number;
  chapter: string;
  figure_number: string;
  title: string;
  category: string;
  keywords: string;
  description: string;
  source_page: number;
}

export interface ResearchNote {
  id: number;
  scenario_id: number;
  note: string;
  created_at: string;
}

export interface ValidationCase {
  id: number;
  charge_weight: number;
  distance: number;
  explosive_name: string;
  burst_type: string;
  scaled_distance: number;
  reference_pressure: number;
  reference_impulse: number;
  calculated_pressure?: number;
  calculated_impulse?: number;
  pressure_abs_error?: number;
  pressure_rel_error?: number;
  impulse_abs_error?: number;
  impulse_rel_error?: number;
  validation_source: string;
  validation_page: string;
  reference_type: string;
  ground_truth_class: string;
  model_version_id?: number;
  validated_at?: string;
}

export interface ValidationSummary {
  ground_truth_class: string;
  total_cases: number;
  avg_pressure_error: number;
  rmse_pressure_error: number;
  max_pressure_error: number;
  p95_pressure_error: number;
  avg_impulse_error: number;
  rmse_impulse_error: number;
  max_impulse_error: number;
  p95_impulse_error: number;
}

export interface PIEnvelopePoint {
  impulse: number;
  pressure: number;
}

export interface PIEnvelope {
  damage_state: string;
  curve_type: string;
  pressure_asymptote: number;
  impulse_asymptote: number;
  curve_constant: number;
  confidence_level: string;
  source_reference: string;
  equation_text: string;
  points: PIEnvelopePoint[];
}

// ─── Sprint 5: Parametric Studies ────────────────────────────────────────────

export type StudyType = 'distance' | 'charge' | 'explosive' | 'grid';

export interface SweepPoint {
  // Provenance
  study_id: string;
  study_type: string;
  explosive_name: string;
  // Scenario
  charge_kg: number;
  distance_m: number;
  scaled_distance: number;
  // Blast environment
  peak_pressure_kPa: number;
  peak_impulse_kPa_ms: number;
  reflected_pressure_kPa: number;
  arrival_time_ms: number;
  // Assessment
  profile_id: number;
  profile_name: string;
  family: string;
  damage_level: 'Safe' | 'Minor' | 'Moderate' | 'Severe' | 'Failure';
  damage_state: string;
  severity_score: number;
  controlling_mode: string;
  damage_index: number;
  pressure_ratio: number;
  impulse_ratio: number;
}

export interface VulnerabilityRanking {
  rank: number;
  profile_id: number;
  profile_name: string;
  family: string;
  mean_severity: number;
  vulnerability_score: number;
  min_safe_standoff_m: number | null;
  failure_radius_m: number | null;
}

export interface GridResult {
  study_id: string;
  study_type: string;
  explosive_name: string;
  charges_kg: number[];
  distances_m: number[];
  profile_ids: number[];
  n_points: number;
  points: SweepPoint[];
  summary: VulnerabilityRanking[];
}

export interface StudyConfig {
  studyType: StudyType;
  explosiveId: number;
  explosiveIds?: number[];       // for explosive comparison
  chargeKg: number;
  chargesKg?: number[];          // for charge sweep / grid
  distanceM: number;
  distancesM?: number[];         // for distance sweep / grid
  profileIds: number[];
  burstType: 'Surface' | 'Air' | 'Free Air';
}

// Point limit tiers (mirrors backend/studies/batch_runner.py)
export const STUDY_LIMITS = {
  IMMEDIATE: 2000,
  SOFT: 5000,
  HARD: 10000,
} as const;
