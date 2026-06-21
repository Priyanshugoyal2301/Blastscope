import { Scenario, ScenarioSavePayload, Explosive, MaterialProfile, BlastResults, DamageAssessment, UnitDefinition, UfcReference, ResearchNote, ValidationCase, ValidationSummary, PIEnvelope, SweepPoint, GridResult } from '../types';

declare global {
  interface Window {
    api?: {
      invoke: (channel: string, payload?: any) => Promise<any>;
    };
  }
}

// Check if window.api is defined (running in Electron)
const isElectron = typeof window !== 'undefined' && window.api !== undefined;

// Mock database states for browser fallback
const mockExplosives: Explosive[] = [
  { id: 1, name: "TNT", pressure_equivalency: 1.0, impulse_equivalency: 1.0, general_equivalency: 1.0, detonation_velocity: 6900.0, density: 1.65 },
  { id: 2, name: "C4", pressure_equivalency: 1.37, impulse_equivalency: 1.19, general_equivalency: 1.34, detonation_velocity: 8040.0, density: 1.59 },
  { id: 3, name: "ANFO", pressure_equivalency: 0.82, impulse_equivalency: 0.89, general_equivalency: 0.82, detonation_velocity: 5270.0, density: 0.93 },
  { id: 4, name: "RDX", pressure_equivalency: 1.14, impulse_equivalency: 1.09, general_equivalency: 1.14, detonation_velocity: 8750.0, density: 1.82 },
  { id: 5, name: "HMX", pressure_equivalency: 1.32, impulse_equivalency: 1.12, general_equivalency: 1.30, detonation_velocity: 9100.0, density: 1.91 }
];

const mockProfiles: MaterialProfile[] = [
  { id: 1, material_id: 1, profile_name: "Glass 6mm Monolithic", family: "Glass", density: 2500.0, compressive_strength: 250.0, tensile_strength: 45.0, failure_mode: "Brittle Shards", strain_rate_factor: 1.0, failure_category: "Brittle", damage_mechanism: "Fracture", notes: "Standard annealed window glazing.", minor_pressure: 15.0, minor_impulse: 100.0, moderate_pressure: 25.0, moderate_impulse: 150.0, severe_pressure: 50.0, severe_impulse: 250.0, failure_pressure: 80.0, failure_impulse: 400.0, source_title: "ISO 16933:2007", source_year: 2007, confidence_level: "High", failure_description: "Spiderweb cracking", threshold_source_type: "Code-Based", applicability_notes: "Standard window pane monolithic glazing" },
  { id: 2, material_id: 1, profile_name: "Glass 12mm Laminated", family: "Glass", density: 2500.0, compressive_strength: 250.0, tensile_strength: 45.0, failure_mode: "PVB Tearing", strain_rate_factor: 1.1, failure_category: "Brittle", damage_mechanism: "PVB Tearing", notes: "Tough laminated security glazing pane.", minor_pressure: 25.0, minor_impulse: 150.0, moderate_pressure: 60.0, moderate_impulse: 350.0, severe_pressure: 120.0, severe_impulse: 700.0, failure_pressure: 200.0, failure_impulse: 1200.0, source_title: "Glazing Criteria", source_year: 2020, confidence_level: "High", failure_description: "Interlayer tearing", threshold_source_type: "Experimental", applicability_notes: "Laminated window pane PVB polymer interlayer" },
  { id: 3, material_id: 2, profile_name: "Brick Masonry Unreinforced", family: "Masonry", density: 2000.0, compressive_strength: 15.0, tensile_strength: 0.5, failure_mode: "Flexural Collapse", strain_rate_factor: 1.2, failure_category: "Brittle", damage_mechanism: "Three-Hinge Collapse", notes: "Traditional unreinforced masonry wall facade.", minor_pressure: 14.0, minor_impulse: 70.0, moderate_pressure: 35.0, moderate_impulse: 150.0, severe_pressure: 80.0, severe_impulse: 380.0, failure_pressure: 120.0, failure_impulse: 500.0, source_title: "Talbott et al.", source_year: 2004, confidence_level: "Medium", failure_description: "Three-hinge collapse", threshold_source_type: "Code-Based", applicability_notes: "Unreinforced brick facades and partition walls" },
  { id: 4, material_id: 3, profile_name: "Reinforced Concrete M30", family: "Concrete", density: 2400.0, compressive_strength: 30.0, tensile_strength: 3.5, failure_mode: "Flexure/Spalling", strain_rate_factor: 1.25, failure_category: "Quasi-brittle", damage_mechanism: "Spalling", notes: "Standard reinforced structural concrete slab.", minor_pressure: 120.0, minor_impulse: 300.0, moderate_pressure: 300.0, moderate_impulse: 500.0, severe_pressure: 1200.0, severe_impulse: 1000.0, failure_pressure: 2000.0, failure_impulse: 2500.0, source_title: "Wang et al.", source_year: 2014, confidence_level: "High", failure_description: "Rear face spalling", threshold_source_type: "Analytical", applicability_notes: "Simply supported reinforced concrete slab elements" },
  { id: 5, material_id: 3, profile_name: "Ultra-High Performance Concrete (UHPC)", family: "Concrete", density: 2600.0, compressive_strength: 150.0, tensile_strength: 12.0, failure_mode: "Localized Shear", strain_rate_factor: 1.3, failure_category: "Fiber-Reinforced Quasi-Brittle", damage_mechanism: "Fiber Pullout", notes: "Premium steel micro-fiber concrete panel.", minor_pressure: 600.0, minor_impulse: 800.0, moderate_pressure: 2500.0, moderate_impulse: 2000.0, severe_pressure: 6000.0, severe_impulse: 5000.0, failure_pressure: 8000.0, failure_impulse: 8000.0, source_title: "UFC 3-340-02", source_year: 2008, confidence_level: "Medium", failure_description: "Fiber pullout / shear crack", threshold_source_type: "Experimental", applicability_notes: "High-strength fiber-reinforced concrete columns" },
  { id: 6, material_id: 4, profile_name: "Structural Steel Grade 250", family: "Steel", density: 7850.0, compressive_strength: 250.0, tensile_strength: 250.0, failure_mode: "Plastic Yielding", strain_rate_factor: 1.4, failure_category: "Ductile", damage_mechanism: "Plastic Yielding", notes: "Ductile structural steel column profile.", minor_pressure: 150.0, minor_impulse: 400.0, moderate_pressure: 800.0, moderate_impulse: 1200.0, severe_pressure: 3500.0, severe_impulse: 3000.0, failure_pressure: 5000.0, failure_impulse: 4000.0, source_title: "UFC 3-340-02", source_year: 2008, confidence_level: "High", failure_description: "Boundary tearing / plastic yield", threshold_source_type: "Analytical", applicability_notes: "Ductile steel plates and boundary joints" }
];

let mockScenarios: Scenario[] = [
  { id: 1, name: "Slab Protection Sweep", explosive_id: 1, explosive_name: "TNT", charge_weight: 100.0, distance: 15.0, burst_type: "Surface", unit_system: "Metric", created_at: new Date().toISOString() },
  { id: 2, name: "Façade Arena Test", explosive_id: 2, explosive_name: "C4", charge_weight: 50.0, distance: 22.0, burst_type: "Free Air", unit_system: "Metric", created_at: new Date().toISOString() },
  { id: 3, name: "High Capacity Safe Boundary", explosive_id: 3, explosive_name: "ANFO", charge_weight: 500.0, distance: 55.0, burst_type: "Air", unit_system: "Metric", created_at: new Date().toISOString() }
];

let mockNotes: Record<number, ResearchNote[]> = {
  1: [
    { id: 101, scenario_id: 1, note: "Governed heavily by concrete spalling threshold at this standoff. Recommending upgrading to UHPC.", created_at: new Date().toISOString() }
  ],
  2: [
    { id: 102, scenario_id: 2, note: "Reflected pressure is significant. Standard 6mm glass will shatter into shards. Laminated glass required.", created_at: new Date().toISOString() }
  ]
};

const mockValidationCases: ValidationCase[] = [
  { id: 1, charge_weight: 1.0, distance: 1.0, explosive_name: "TNT", burst_type: "Surface", scaled_distance: 1.0, reference_pressure: 1353.7, reference_impulse: 244.7, validation_source: "UFC 3-340-02", validation_page: "Figure 2-15", reference_type: "Digitized", ground_truth_class: "Digitized" },
  { id: 2, charge_weight: 1.0, distance: 1.5, explosive_name: "TNT", burst_type: "Surface", scaled_distance: 1.5, reference_pressure: 545.2, reference_impulse: 155.3, validation_source: "UFC 3-340-02", validation_page: "Figure 2-15", reference_type: "Digitized", ground_truth_class: "Digitized" },
  { id: 3, charge_weight: 1.0, distance: 2.0, explosive_name: "TNT", burst_type: "Surface", scaled_distance: 2.0, reference_pressure: 290.5, reference_impulse: 111.4, validation_source: "UFC 3-340-02", validation_page: "Figure 2-15", reference_type: "Digitized", ground_truth_class: "Digitized" },
  { id: 4, charge_weight: 5.0, distance: 2.0, explosive_name: "TNT", burst_type: "Surface", scaled_distance: 1.17, reference_pressure: 955.0, reference_impulse: 305.0, validation_source: "ConWep Example", validation_page: "Table 4-2", reference_type: "Analytical", ground_truth_class: "ConWep" },
  { id: 5, charge_weight: 10.0, distance: 2.0, explosive_name: "TNT", burst_type: "Surface", scaled_distance: 0.93, reference_pressure: 1680.0, reference_impulse: 380.0, validation_source: "NSWC Field Test", validation_page: "Report 94-1", reference_type: "Experimental", ground_truth_class: "Experimental" }
];

interface CoeffRange {
  min: number;
  max: number;
  coeffs: number[];
}

const SURFACE_INCIDENT_PRESSURE: CoeffRange[] = [
  { min: 0.20, max: 2.90, coeffs: [7.2106, -2.1069, -0.3229, 0.1117, 0.0685, 0.0, 0.0] },
  { min: 2.90, max: 23.80, coeffs: [7.5938, -3.0523, 0.40977, 0.0261, -0.01267, 0.0, 0.0] },
  { min: 23.80, max: 198.5, coeffs: [6.0536, -1.4066, 0.0, 0.0, 0.0, 0.0, 0.0] }
];

const SURFACE_REFLECTED_PRESSURE: CoeffRange[] = [
  { min: 0.06, max: 2.00, coeffs: [9.0060, -2.6893, -0.6295, 0.1011, 0.29255, 0.13505, 0.019736] },
  { min: 2.00, max: 40.00, coeffs: [8.8396, -1.7330, -2.6400, 2.2930, -0.8232, 0.14247, -0.0099] }
];

const SURFACE_INCIDENT_IMPULSE: CoeffRange[] = [
  { min: 0.20, max: 0.96, coeffs: [5.5220, 1.1170, 0.6000, -0.2920, -0.0870, 0.0, 0.0] },
  { min: 0.96, max: 2.38, coeffs: [5.4650, -0.3080, -1.4640, 1.3620, -0.4320, 0.0, 0.0] },
  { min: 2.38, max: 33.70, coeffs: [5.2749, -0.4677, -0.2499, 0.0588, -0.00554, 0.0, 0.0] },
  { min: 33.70, max: 158.7, coeffs: [5.9825, -1.0620, 0.0, 0.0, 0.0, 0.0, 0.0] }
];

const SURFACE_REFLECTED_IMPULSE: CoeffRange[] = [
  { min: 0.06, max: 40.00, coeffs: [6.7853, -1.3466, 0.1010, -0.01123, 0.0, 0.0, 0.0] }
];

const SURFACE_ARRIVAL_TIME: CoeffRange[] = [
  { min: 0.06, max: 1.50, coeffs: [-0.7604, 1.8058, 0.1257, -0.0437, -0.0310, -0.00669, 0.0] },
  { min: 1.50, max: 40.00, coeffs: [-0.7137, 1.5732, 0.5561, -0.4213, 0.1054, -0.00929, 0.0] }
];

const SURFACE_POSITIVE_DURATION: CoeffRange[] = [
  { min: 0.20, max: 1.02, coeffs: [0.5426, 3.2299, -1.5931, -5.9667, -4.0815, -0.9149, 0.0] },
  { min: 1.02, max: 2.80, coeffs: [0.5440, 2.7082, -9.7354, 14.3425, -9.7791, 2.8535, 0.0] },
  { min: 2.80, max: 40.00, coeffs: [-2.4608, 7.1639, -5.6215, 2.2711, -0.44994, 0.03486, 0.0] }
];

const SPHERICAL_INCIDENT_PRESSURE: CoeffRange[] = [
  { min: 0.148, max: 2.90, coeffs: [6.56473, -2.06707, -0.28669, 0.13897, 0.08131, 0.0, 0.0] },
  { min: 2.90, max: 23.80, coeffs: [3.61594, 4.48734, -5.46266, 2.02546, -0.26044, 0.0, 0.0] },
  { min: 23.80, max: 198.5, coeffs: [5.39971, -1.33447, 0.0, 0.0, 0.0, 0.0, 0.0] }
];

const SPHERICAL_REFLECTED_PRESSURE: CoeffRange[] = [
  { min: 0.148, max: 2.90, coeffs: [8.26049, -2.54107, -0.34397, 0.049, 0.04288, 0.0, 0.0] },
  { min: 2.90, max: 40.00, coeffs: [12.36133, -11.12002, 5.5102, -1.36809, 0.12638, 0.0, 0.0] }
];

const SPHERICAL_INCIDENT_IMPULSE: CoeffRange[] = [
  { min: 0.148, max: 2.90, coeffs: [4.97684, -0.92232, -0.11323, 0.07582, 0.03658, 0.0, 0.0] },
  { min: 2.90, max: 23.80, coeffs: [-2.50228, 16.73448, -14.93514, 5.40371, -0.70159, 0.0, 0.0] },
  { min: 23.80, max: 198.5, coeffs: [5.84795, -1.2916, 0.0, 0.0, 0.0, 0.0, 0.0] }
];

const SPHERICAL_REFLECTED_IMPULSE: CoeffRange[] = [
  { min: 0.148, max: 2.90, coeffs: [5.851, -0.85787, -0.11274, 0.03248, 0.01446, 0.0, 0.0] },
  { min: 2.90, max: 40.00, coeffs: [5.38228, -0.017, -0.61626, 0.18847, -0.01981, 0.0, 0.0] }
];

const SPHERICAL_ARRIVAL_TIME: CoeffRange[] = [
  { min: 0.148, max: 2.90, coeffs: [-0.52539, 1.14767, 0.08316, 0.0, 0.0, 0.0, 0.0] },
  { min: 2.90, max: 40.00, coeffs: [0.20682, 0.46614, 0.07737, 0.0, 0.0, 0.0, 0.0] }
];

const SPHERICAL_POSITIVE_DURATION: CoeffRange[] = [
  { min: 0.148, max: 2.90, coeffs: [1.08504, 0.34797, 0.07646, 0.0, 0.0, 0.0, 0.0] },
  { min: 2.90, max: 40.00, coeffs: [1.61406, -0.06479, -0.00253, 0.0, 0.0, 0.0, 0.0] }
];

function evalSwisdakPolynomial(coeffs: number[], Z: number): number {
  const U = Math.log(Z);
  let log_Y = 0.0;
  for (let i = 0; i < coeffs.length; i++) {
    log_Y += coeffs[i] * Math.pow(U, i);
  }
  return Math.exp(log_Y);
}

function selectAndEval(tables: CoeffRange[], Z: number): number {
  const overall_min = tables[0].min;
  const overall_max = tables[tables.length - 1].max;
  const Z_clamped = Math.min(Math.max(Z, overall_min), overall_max);
  
  for (const range of tables) {
    if (Z_clamped >= range.min && Z_clamped <= range.max) {
      return evalSwisdakPolynomial(range.coeffs, Z_clamped);
    }
  }
  return evalSwisdakPolynomial(tables[tables.length - 1].coeffs, Z_clamped);
}

function solveDecayParameter(pso: number, impulse: number, duration: number): number {
  let k = impulse / (pso * duration);
  k = Math.max(1e-4, Math.min(k, 0.4999));
  
  let b = 0.0;
  if (k > 0.4) {
    b = 6.0 * (0.5 - k);
  } else {
    b = 1.0 / k;
  }
  
  for (let i = 0; i < 20; i++) {
    const eb = Math.exp(-b);
    const f = (b - 1.0 + eb) / (b * b) - k;
    const df = (2.0 - b - (b + 2.0) * eb) / (b * b * b);
    if (Math.abs(df) < 1e-12) {
      break;
    }
    const next_b = b - f / df;
    if (next_b <= 0) {
      b = b / 2.0;
    } else if (Math.abs(next_b - b) < 1e-6) {
      b = next_b;
      break;
    } else {
      b = next_b;
    }
  }
  return b;
}

function calculateKbParameters(scaled_distance: number, burst_type: string) {
  const Z = Math.max(scaled_distance, 0.05);
  let incident_p: number;
  let reflected_p: number;
  let positive_impulse: number;
  let reflected_impulse: number;
  let arrival_time: number;
  let positive_duration: number;

  if (burst_type === "Surface") {
    incident_p = selectAndEval(SURFACE_INCIDENT_PRESSURE, Z);
    reflected_p = selectAndEval(SURFACE_REFLECTED_PRESSURE, Z);
    positive_impulse = selectAndEval(SURFACE_INCIDENT_IMPULSE, Z);
    reflected_impulse = selectAndEval(SURFACE_REFLECTED_IMPULSE, Z);
    arrival_time = selectAndEval(SURFACE_ARRIVAL_TIME, Z);
    positive_duration = selectAndEval(SURFACE_POSITIVE_DURATION, Z);
  } else {
    incident_p = selectAndEval(SPHERICAL_INCIDENT_PRESSURE, Z);
    reflected_p = selectAndEval(SPHERICAL_REFLECTED_PRESSURE, Z);
    positive_impulse = selectAndEval(SPHERICAL_INCIDENT_IMPULSE, Z);
    reflected_impulse = selectAndEval(SPHERICAL_REFLECTED_IMPULSE, Z);
    arrival_time = selectAndEval(SPHERICAL_ARRIVAL_TIME, Z);
    positive_duration = selectAndEval(SPHERICAL_POSITIVE_DURATION, Z);
  }

  const P0 = 101.325;
  const dynamic_p = 2.5 * (incident_p * incident_p) / (7.0 * P0 + incident_p);
  
  const C0 = 340.292;
  const shock_front_velocity = C0 * Math.sqrt(1.0 + 6.0 * incident_p / (7.0 * P0));
  const particle_velocity = (5.0 * C0 * incident_p) / (7.0 * P0 * Math.sqrt(1.0 + 6.0 * incident_p / (7.0 * P0)));
  
  const decay_b = solveDecayParameter(incident_p, positive_impulse, positive_duration);
  const negative_duration = positive_duration * (1.0 + 1.0 / decay_b);

  return {
    scaled_distance: Z,
    incident_pressure: incident_p,
    reflected_pressure: reflected_p,
    dynamic_pressure: dynamic_p,
    positive_impulse,
    reflected_impulse,
    positive_duration,
    negative_duration,
    arrival_time,
    shock_front_velocity,
    particle_velocity,
    decay_parameter: decay_b
  };
}

// Physics simulation matching dual TNT math using Swisdak (1994)
function simulateCalculateBlast(weight: number, distance: number, burstType: string, explosiveId: number): BlastResults {
  const explosive = mockExplosives.find(e => e.id === explosiveId) || mockExplosives[0];
  const pFactor = explosive.pressure_equivalency;
  const iFactor = explosive.impulse_equivalency;
  const gFactor = explosive.general_equivalency || pFactor;

  const W_p = weight * pFactor;
  const W_i = weight * iFactor;
  const W_g = weight * gFactor;

  const Z_p = distance / Math.pow(W_p, 1.0 / 3.0);
  const Z_i = distance / Math.pow(W_i, 1.0 / 3.0);
  const Z_g = distance / Math.pow(W_g, 1.0 / 3.0);

  const kb_p = calculateKbParameters(Z_p, burstType);
  const kb_i = calculateKbParameters(Z_i, burstType);

  const w_p_factor = Math.pow(W_p, 1.0 / 3.0);
  const w_i_factor = Math.pow(W_i, 1.0 / 3.0);

  const incident_p = kb_p.incident_pressure;
  const reflected_p = kb_p.reflected_pressure;

  return {
    scaled_distance: Z_g,
    incident_pressure: incident_p,
    reflected_pressure: reflected_p,
    dynamic_pressure: kb_p.dynamic_pressure,
    positive_impulse: kb_i.positive_impulse * w_i_factor,
    positive_duration: kb_i.positive_duration * w_i_factor,
    negative_duration: kb_i.negative_duration * w_i_factor,
    arrival_time: kb_p.arrival_time * w_p_factor,
    shock_front_velocity: kb_p.shock_front_velocity,
    particle_velocity: kb_p.particle_velocity,
    decay_parameter: kb_i.decay_parameter,
    model_used: "Kingery-Bulmash",
    model_version: "v2.0"
  };
}

function simulateAssessBatch(results: BlastResults): DamageAssessment[] {
  const angle = 0.0;
  const angle_rad = (angle * Math.PI) / 180.0;
  
  const H = 3.0;
  const W = 4.0;
  const S = Math.min(H, W / 2.0);
  const P0 = 101.325;

  return mockProfiles.map(prof => {
    const isFacade = prof.family === 'Glass' || prof.family === 'Masonry';
    let P_actual = results.incident_pressure;
    let I_actual = results.positive_impulse;

    if (isFacade) {
      const P_incident = results.incident_pressure;
      const P_reflected = results.reflected_pressure;
      const I_incident = results.positive_impulse;
      const I_reflected = results.positive_impulse;

      const cos2 = Math.pow(Math.cos(angle_rad), 2);
      const P_adj = P_incident + (P_reflected - P_incident) * cos2;
      const I_adj = I_incident + (I_reflected - I_incident) * cos2;

      const c0 = 0.340;
      const term = 1.0 + (6.0 * P_incident) / (7.0 * P0);
      const U_shock = c0 * Math.sqrt(Math.max(0.1, term));

      const t_c = U_shock > 0 ? (3.0 * S) / U_shock : 9999.0;
      const t_d = results.positive_duration || 10.0;

      const Q_so = results.dynamic_pressure || 0.0;
      const P_stag = P_incident + Q_so;

      if (t_c < t_d) {
        const I_cleared = P_adj * (t_c / 2.0) + P_stag * ((t_d - t_c) / 2.0);
        I_actual = Math.min(I_adj, I_cleared);
      } else {
        I_actual = I_adj;
      }
      P_actual = P_adj;
    }

    const P_ratio = P_actual / prof.minor_pressure;
    const I_ratio = I_actual / prof.minor_impulse;
    const DI = Math.max(P_ratio, I_ratio);
    const mode = P_ratio >= I_ratio ? 'Pressure' : 'Impulse';

    let level: 'Safe' | 'Minor' | 'Moderate' | 'Severe' | 'Failure' = 'Safe';
    
    if (prof.failure_pressure && prof.failure_impulse && P_actual >= prof.failure_pressure && I_actual >= prof.failure_impulse) {
      level = 'Failure';
    } else if (prof.severe_pressure && prof.severe_impulse && P_actual >= prof.severe_pressure && I_actual >= prof.severe_impulse) {
      level = 'Severe';
    } else if (prof.moderate_pressure && prof.moderate_impulse && P_actual >= prof.moderate_pressure && I_actual >= prof.moderate_impulse) {
      level = 'Moderate';
    } else if (prof.minor_pressure && prof.minor_impulse && P_actual >= prof.minor_pressure && I_actual >= prof.minor_impulse) {
      level = 'Minor';
    } else {
      level = 'Safe';
    }

    let state = level as string;
    let score = DI / 4.0;
    if (prof.family === 'Concrete') {
      state = level === 'Safe' ? 'Elastic' : level === 'Minor' ? 'Cracking' : level === 'Moderate' ? 'Spalling' : 'Scabbing';
    } else if (prof.family === 'Steel') {
      state = level === 'Safe' ? 'Elastic' : level === 'Minor' ? 'Yield' : level === 'Moderate' ? 'Membrane' : 'Tearing';
    } else if (prof.family === 'Glass') {
      state = level === 'Safe' ? 'Glazing Safe' : level === 'Minor' ? 'Low Hazard' : 'High Hazard';
      score = Math.min(1.0, DI / 2.0);
    }

    return {
      profile_id: prof.id,
      profile_name: prof.profile_name,
      family: prof.family,
      failure_category: prof.failure_category,
      damage_level: level,
      damage_state: state,
      severity_score: Math.min(1.0, Math.max(0.0, score)),
      pressure_ratio: P_ratio,
      impulse_ratio: I_ratio,
      damage_index: DI,
      controlling_mode: mode,
      damage_mechanism: prof.damage_mechanism,
      assessment_reason: `Damage Index ${DI.toFixed(2)} governed by ${mode} (P-ratio: ${P_ratio.toFixed(2)}, I-ratio: ${I_ratio.toFixed(2)})`,
      confidence_level: prof.confidence_level || 'High',
      source_reference: prof.source_title || 'UFC 3-340-02',
      response_model_version: 'v2.0 (Mock Fallback)'
    };
  });
}

// API Export dispatcher
export const api = {
  scenarios: {
    list: (): Promise<Scenario[]> => 
      isElectron 
        ? window.api!.invoke('scenarios:list') 
        : Promise.resolve([...mockScenarios]),
        
    save: (scenario: ScenarioSavePayload): Promise<{ scenarioId: number; resultId: number; assessments: DamageAssessment[] }> => {
      if (isElectron) {
        return window.api!.invoke('scenarios:save', scenario);
      }
      
      const exp = mockExplosives.find(e => e.id === scenario.explosiveId) || mockExplosives[0];
      const newId = scenario.id || (mockScenarios.length > 0 ? Math.max(...mockScenarios.map(s => s.id || 0)) + 1 : 1);
      
      const newScenario: Scenario = {
        id: newId,
        name: scenario.name,
        explosive_id: scenario.explosiveId,
        explosive_name: exp.name,
        charge_weight: scenario.chargeWeight,
        distance: scenario.distance,
        burst_type: scenario.burstType,
        unit_system: scenario.unitSystem,
        created_at: new Date().toISOString()
      };
      
      if (scenario.id) {
        mockScenarios = mockScenarios.map(s => s.id === scenario.id ? newScenario : s);
      } else {
        mockScenarios.push(newScenario);
      }
      
      const blastResults = simulateCalculateBlast(scenario.chargeWeight, scenario.distance, scenario.burstType, scenario.explosiveId);
      const assessments = simulateAssessBatch(blastResults);
      
      return Promise.resolve({
        scenarioId: newId,
        resultId: 999,
        assessments
      });
    },
    
    saveNote: (scenarioId: number, note: string): Promise<ResearchNote> => {
      if (isElectron) {
        return window.api!.invoke('scenarios:saveNote', { scenarioId, note });
      }
      const newNote: ResearchNote = {
        id: Math.floor(Math.random() * 10000),
        scenario_id: scenarioId,
        note,
        created_at: new Date().toISOString()
      };
      if (!mockNotes[scenarioId]) {
        mockNotes[scenarioId] = [];
      }
      mockNotes[scenarioId].push(newNote);
      return Promise.resolve(newNote);
    },
    
    listNotes: (scenarioId: number): Promise<ResearchNote[]> => 
      isElectron 
        ? window.api!.invoke('scenarios:listNotes', { scenarioId }) 
        : Promise.resolve(mockNotes[scenarioId] || [])
  },
  
  explosives: {
    list: (): Promise<Explosive[]> => 
      isElectron 
        ? window.api!.invoke('explosives:list') 
        : Promise.resolve([...mockExplosives])
  },
  
  materials: {
    listProfiles: (): Promise<MaterialProfile[]> => 
      isElectron 
        ? window.api!.invoke('materials:listProfiles') 
        : Promise.resolve([...mockProfiles]),
        
    getPIEnvelopes: (profileId: number): Promise<PIEnvelope[]> => {
      if (isElectron) {
        return window.api!.invoke('materials:getPIEnvelopes', { profileId });
      }
      const prof = mockProfiles.find(p => p.id === profileId) || mockProfiles[0];
      const states: Array<{ state: string; p: number; i: number; c: string }> = [
        { state: 'Minor', p: prof.minor_pressure, i: prof.minor_impulse, c: 'High' },
        { state: 'Moderate', p: prof.moderate_pressure, i: prof.moderate_impulse, c: 'High' },
        { state: 'Severe', p: prof.severe_pressure, i: prof.severe_impulse, c: 'High' },
        { state: 'Failure', p: prof.failure_pressure, i: prof.failure_impulse, c: 'High' }
      ];
      
      const envelopes = states.map(s => {
        const p0 = s.p * 0.7;
        const i0 = s.i * 0.7;
        const kc = (s.p - p0) * (s.i - i0);
        const points = [];
        const start = i0 * 1.1;
        const end = Math.max(start * 100, 20000.0);
        const logStart = Math.log10(start);
        const logEnd = Math.log10(end);
        const step = (logEnd - logStart) / 299;
        for (let idx = 0; idx < 300; idx++) {
          const imp = Math.pow(10, logStart + idx * step);
          const press = p0 + kc / (imp - i0);
          points.push({ impulse: imp, pressure: press });
        }
        return {
          damage_state: s.state,
          curve_type: 'Hyperbolic',
          pressure_asymptote: p0,
          impulse_asymptote: i0,
          curve_constant: kc,
          confidence_level: s.c,
          source_reference: prof.source_title || 'UFC 3-340-02',
          equation_text: `(P - ${p0.toFixed(1)}) * (I - ${i0.toFixed(1)}) = ${kc.toFixed(1)}`,
          points
        };
      });
      return Promise.resolve(envelopes);
    }
  },
  
  blast: {
    calculateEnvironment: (params: {
      chargeWeight: number;
      distance: number;
      burstType: string;
      explosiveId: number;
      model?: string;
    }): Promise<BlastResults> => 
      isElectron 
        ? window.api!.invoke('blast:calculateEnvironment', params) 
        : Promise.resolve(simulateCalculateBlast(params.chargeWeight, params.distance, params.burstType, params.explosiveId))
  },
  
  material: {
    assessBatch: (results: BlastResults, profileIds?: number[]): Promise<DamageAssessment[]> => 
      isElectron 
        ? window.api!.invoke('material:assessBatch', { results, profileIds }) 
        : Promise.resolve(simulateAssessBatch(results))
  },
  
  research: {
    parametricSweep: (params: {
      baseScenarioId: number;
      variableName: 'chargeWeight' | 'distance';
      minValue: number;
      maxValue: number;
      stepValue: number;
      model?: string;
    }): Promise<Array<BlastResults & { sweep_variable: number }>> => {
      if (isElectron) {
        return window.api!.invoke('research:parametricSweep', params);
      }
      
      const base = mockScenarios.find(s => s.id === params.baseScenarioId) || mockScenarios[0];
      const results: Array<BlastResults & { sweep_variable: number }> = [];
      
      const step = params.stepValue > 0 ? params.stepValue : 1;
      for (let val = params.minValue; val <= params.maxValue; val += step) {
        const d = params.variableName === 'distance' ? val : base.distance;
        const w = params.variableName === 'chargeWeight' ? val : base.charge_weight;
        const res = simulateCalculateBlast(w, d, base.burst_type, base.explosive_id);
        results.push({
          ...res,
          sweep_variable: val
        });
      }
      return Promise.resolve(results);
    },
    
    compareScenarios: (scenarioIds: number[]): Promise<Array<{
      scenarioId: number;
      scenarioName: string;
      chargeWeight: number;
      explosiveName: string;
      burstType: string;
      curve: Array<{
        distance: number;
        incident_pressure: number;
        reflected_pressure: number;
        positive_impulse: number;
      }>;
    }>> => {
      if (isElectron) {
        return window.api!.invoke('research:compareScenarios', { scenarioIds });
      }
      
      const curves = scenarioIds.map(id => {
        const sc = mockScenarios.find(s => s.id === id) || mockScenarios[0];
        const curvePoints = [];
        for (let d = 1; d <= 100; d += 2) {
          const res = simulateCalculateBlast(sc.charge_weight, d, sc.burst_type, sc.explosive_id);
          curvePoints.push({
            distance: d,
            incident_pressure: res.incident_pressure,
            reflected_pressure: res.reflected_pressure,
            positive_impulse: res.positive_impulse
          });
        }
        return {
          scenarioId: sc.id!,
          scenarioName: sc.name,
          chargeWeight: sc.charge_weight,
          explosiveName: sc.explosive_name || 'TNT',
          burstType: sc.burst_type,
          curve: curvePoints
        };
      });
      return Promise.resolve(curves);
    }
  },
  
  validation: {
    runSweep: (): Promise<ValidationCase[]> => {
      if (isElectron) {
        return window.api!.invoke('validation:runSweep');
      }
      const updated = mockValidationCases.map(c => {
        const res = simulateCalculateBlast(c.charge_weight, c.distance, c.burst_type, 1);
        const p_calc = res.incident_pressure;
        const i_calc = res.positive_impulse;
        const p_abs = Math.abs(p_calc - c.reference_pressure);
        const p_rel = (p_abs / c.reference_pressure) * 100.0;
        const i_abs = Math.abs(i_calc - c.reference_impulse);
        const i_rel = (i_abs / c.reference_impulse) * 100.0;
        return {
          ...c,
          calculated_pressure: p_calc,
          calculated_impulse: i_calc,
          pressure_abs_error: p_abs,
          pressure_rel_error: p_rel,
          impulse_abs_error: i_abs,
          impulse_rel_error: i_rel
        };
      });
      return Promise.resolve(updated);
    },
    
    getSummary: (): Promise<ValidationSummary[]> => {
      if (isElectron) {
        return window.api!.invoke('validation:getSummary');
      }
      const groups = ['Digitized', 'ConWep', 'Experimental', 'Analytical'];
      const summary: ValidationSummary[] = groups.map(grp => {
        const groupCases = mockValidationCases.filter(c => c.ground_truth_class === grp);
        const errsP: number[] = [];
        const errsI: number[] = [];
        groupCases.forEach(c => {
          const res = simulateCalculateBlast(c.charge_weight, c.distance, c.burst_type, 1);
          errsP.push((Math.abs(res.incident_pressure - c.reference_pressure) / c.reference_pressure) * 100.0);
          errsI.push((Math.abs(res.positive_impulse - c.reference_impulse) / c.reference_impulse) * 100.0);
        });
        
        const sortedP = [...errsP].sort((a,b) => a-b);
        const sortedI = [...errsI].sort((a,b) => a-b);
        const p95P = sortedP[Math.min(sortedP.length - 1, Math.max(0, Math.ceil(0.95 * sortedP.length) - 1))] || 0;
        const p95I = sortedI[Math.min(sortedI.length - 1, Math.max(0, Math.ceil(0.95 * sortedI.length) - 1))] || 0;
        
        return {
          ground_truth_class: grp,
          total_cases: groupCases.length,
          avg_pressure_error: errsP.reduce((sum, val) => sum + val, 0) / (errsP.length || 1),
          rmse_pressure_error: Math.sqrt(errsP.reduce((sum, val) => sum + val * val, 0) / (errsP.length || 1)),
          max_pressure_error: Math.max(...errsP, 0),
          p95_pressure_error: p95P,
          avg_impulse_error: errsI.reduce((sum, val) => sum + val, 0) / (errsI.length || 1),
          rmse_impulse_error: Math.sqrt(errsI.reduce((sum, val) => sum + val * val, 0) / (errsI.length || 1)),
          max_impulse_error: Math.max(...errsI, 0),
          p95_impulse_error: p95I
        };
      });
      
      const totalCases = mockValidationCases;
      const totalErrsP: number[] = [];
      const totalErrsI: number[] = [];
      totalCases.forEach(c => {
        const res = simulateCalculateBlast(c.charge_weight, c.distance, c.burst_type, 1);
        totalErrsP.push((Math.abs(res.incident_pressure - c.reference_pressure) / c.reference_pressure) * 100.0);
        totalErrsI.push((Math.abs(res.positive_impulse - c.reference_impulse) / c.reference_impulse) * 100.0);
      });
      
      const sortedTotalP = [...totalErrsP].sort((a,b) => a-b);
      const sortedTotalI = [...totalErrsI].sort((a,b) => a-b);
      const p95TotalP = sortedTotalP[Math.min(sortedTotalP.length - 1, Math.max(0, Math.ceil(0.95 * sortedTotalP.length) - 1))] || 0;
      const p95TotalI = sortedTotalI[Math.min(sortedTotalI.length - 1, Math.max(0, Math.ceil(0.95 * sortedTotalI.length) - 1))] || 0;
      
      summary.push({
        ground_truth_class: "OVERALL TOTAL",
        total_cases: totalCases.length,
        avg_pressure_error: totalErrsP.reduce((sum, val) => sum + val, 0) / (totalErrsP.length || 1),
        rmse_pressure_error: Math.sqrt(totalErrsP.reduce((sum, val) => sum + val * val, 0) / (totalErrsP.length || 1)),
        max_pressure_error: Math.max(...totalErrsP, 0),
        p95_pressure_error: p95TotalP,
        avg_impulse_error: totalErrsI.reduce((sum, val) => sum + val, 0) / (totalErrsI.length || 1),
        rmse_impulse_error: Math.sqrt(totalErrsI.reduce((sum, val) => sum + val * val, 0) / (totalErrsI.length || 1)),
        max_impulse_error: Math.max(...totalErrsI, 0),
        p95_impulse_error: p95TotalI
      });
      
      return Promise.resolve(summary);
    }
  },

  units: {
    list: (): Promise<UnitDefinition[]> => {
      if (isElectron) {
        return window.api!.invoke('units:list');
      }
      return Promise.resolve([
        { id: 1, quantity: "Pressure", unit_symbol: "kPa", conversion_factor: 1.0, is_base: 1 },
        { id: 2, quantity: "Pressure", unit_symbol: "MPa", conversion_factor: 1000.0, is_base: 0 },
        { id: 3, quantity: "Pressure", unit_symbol: "psi", conversion_factor: 6.89476, is_base: 0 },
        { id: 4, quantity: "Distance", unit_symbol: "m", conversion_factor: 1.0, is_base: 1 },
        { id: 5, quantity: "Distance", unit_symbol: "ft", conversion_factor: 0.3048, is_base: 0 },
        { id: 6, quantity: "Impulse", unit_symbol: "kPa-ms", conversion_factor: 1.0, is_base: 1 }
      ]);
    },
    
    convert: (value: number, from: string, to: string): Promise<{ value: number }> => {
      if (isElectron) {
        return window.api!.invoke('units:convert', { value, from, to });
      }
      // Simple fallback converter
      let baseVal = value;
      if (from === 'MPa') baseVal = value * 1000.0;
      else if (from === 'psi') baseVal = value * 6.89476;
      else if (from === 'ft') baseVal = value * 0.3048;
      
      let finalVal = baseVal;
      if (to === 'MPa') finalVal = baseVal / 1000.0;
      else if (to === 'psi') finalVal = baseVal / 6.89476;
      else if (to === 'ft') finalVal = baseVal / 0.3048;
      
      return Promise.resolve({ value: finalVal });
    }
  },
  
  ufc: {
    search: (query: string): Promise<UfcReference[]> => {
      if (isElectron) {
        return window.api!.invoke('ufc:search', { query });
      }
      const ufcMock: UfcReference[] = [
        { id: 1, chapter: "Chapter 2", figure_number: "Figure 2-7", title: "Positive Phase Shock Wave Parameters for a Free-Air Burst", category: "Blast Parameters", keywords: "Free-Air Burst, Incident Pressure, Impulse, Positive Duration, Arrival Time", description: "Contains curves for scaled positive incident parameters vs scaled distance.", source_page: 34 },
        { id: 2, chapter: "Chapter 2", figure_number: "Figure 2-8", title: "Positive Phase Reflected Shock Wave Parameters for a Free-Air Burst", category: "Reflected Parameters", keywords: "Free-Air Burst, Reflected Pressure, Reflected Impulse", description: "Contains curves for scaled positive reflected parameters vs scaled distance.", source_page: 42 },
        { id: 3, chapter: "Chapter 2", figure_number: "Figure 2-15", title: "Positive Phase Shock Wave Parameters for a Surface Burst", category: "Blast Parameters", keywords: "Surface Burst, Incident Pressure, Incident Impulse, Duration", description: "Contains curves for scaled surface burst parameters vs scaled distance.", source_page: 55 },
        { id: 4, chapter: "Chapter 2", figure_number: "Figure 2-16", title: "Positive Phase Reflected Shock Wave Parameters for a Surface Burst", category: "Reflected Parameters", keywords: "Surface Burst, Reflected Pressure, Reflected Impulse", description: "Contains curves for scaled surface burst reflected parameters vs scaled distance.", source_page: 61 },
        { id: 5, chapter: "Chapter 2", figure_number: "Figure 2-29", title: "TNT Equivalency Curves for Solid High Explosives", category: "Explosives Library", keywords: "TNT Equivalence, Solid Explosives, Shock Output", description: "Graph representing comparative blast wave outputs for various formulations.", source_page: 98 }
      ];
      const term = query.toLowerCase();
      const filtered = ufcMock.filter(f => 
        f.title.toLowerCase().includes(term) || 
        f.figure_number.toLowerCase().includes(term) || 
        f.keywords.toLowerCase().includes(term)
      );
      return Promise.resolve(filtered);
    }
  },

  // ─── Studies (Sprint 5) ────────────────────────────────────────────────────
  studies: {
    async distanceSweep(params: {
      explosive_id: number;
      charge_kg: number;
      distances_m: number[];
      profile_ids: number[];
      burst_type?: string;
    }): Promise<SweepPoint[]> {
      if (isElectron) {
        return window.api!.invoke('studies:distanceSweep', params);
      }
      // Browser fallback: simulate a simple 3-point sweep
      return Promise.resolve(
        params.distances_m.map((d, i) => ({
          study_id: 'browser-demo',
          study_type: 'distance_sweep',
          explosive_name: 'TNT',
          charge_kg: params.charge_kg,
          distance_m: d,
          scaled_distance: d / Math.pow(params.charge_kg, 1 / 3),
          peak_pressure_kPa: 500 / (d * d),
          peak_impulse_kPa_ms: 200 / d,
          reflected_pressure_kPa: 1000 / (d * d),
          arrival_time_ms: d / 340 * 1000,
          profile_id: params.profile_ids[0] ?? 1,
          profile_name: 'Reinforced Concrete M30',
          family: 'Concrete',
          damage_level: i < 2 ? 'Severe' : 'Moderate',
          damage_state: i < 2 ? 'Scabbing' : 'Spalling',
          severity_score: i < 2 ? 0.72 : 0.52,
          controlling_mode: 'Pressure',
          damage_index: i < 2 ? 2.1 : 1.4,
          pressure_ratio: i < 2 ? 2.1 : 1.4,
          impulse_ratio: i < 2 ? 1.8 : 1.1,
        } as SweepPoint))
      );
    },

    async chargeSweep(params: {
      explosive_id: number;
      charges_kg: number[];
      distance_m: number;
      profile_ids: number[];
      burst_type?: string;
    }): Promise<SweepPoint[]> {
      if (isElectron) {
        return window.api!.invoke('studies:chargeSweep', params);
      }
      return Promise.resolve(
        params.charges_kg.map((c, i) => ({
          study_id: 'browser-demo',
          study_type: 'charge_sweep',
          explosive_name: 'TNT',
          charge_kg: c,
          distance_m: params.distance_m,
          scaled_distance: params.distance_m / Math.pow(c, 1 / 3),
          peak_pressure_kPa: 50 * c / (params.distance_m * params.distance_m),
          peak_impulse_kPa_ms: 20 * Math.pow(c, 1/3) / params.distance_m,
          reflected_pressure_kPa: 100 * c / (params.distance_m * params.distance_m),
          arrival_time_ms: params.distance_m / 340 * 1000,
          profile_id: params.profile_ids[0] ?? 1,
          profile_name: 'Reinforced Concrete M30',
          family: 'Concrete',
          damage_level: i > 2 ? 'Failure' : 'Severe',
          damage_state: i > 2 ? 'Breaching' : 'Scabbing',
          severity_score: Math.min(1.0, 0.5 + i * 0.12),
          controlling_mode: 'Pressure',
          damage_index: 1.5 + i * 0.4,
          pressure_ratio: 1.5 + i * 0.4,
          impulse_ratio: 1.2 + i * 0.3,
        } as SweepPoint))
      );
    },

    async explosiveComparison(params: {
      explosive_ids: number[];
      charge_kg: number;
      distances_m: number[];
      profile_ids: number[];
      burst_type?: string;
    }): Promise<SweepPoint[]> {
      if (isElectron) {
        return window.api!.invoke('studies:explosiveComparison', params);
      }
      const explosiveNames = ['TNT', 'C4', 'ANFO'];
      const points: SweepPoint[] = [];
      params.explosive_ids.forEach((eid, ei) => {
        params.distances_m.forEach((d, _di) => {
          const factor = eid === 2 ? 1.37 : eid === 3 ? 0.82 : 1.0;
          points.push({
            study_id: 'browser-demo',
            study_type: 'explosive_comparison',
            explosive_name: explosiveNames[ei] ?? 'TNT',
            charge_kg: params.charge_kg,
            distance_m: d,
            scaled_distance: d / Math.pow(params.charge_kg * factor, 1/3),
            peak_pressure_kPa: 500 * factor / (d * d),
            peak_impulse_kPa_ms: 200 * factor / d,
            reflected_pressure_kPa: 1000 * factor / (d * d),
            arrival_time_ms: d / 340 * 1000,
            profile_id: params.profile_ids[0] ?? 1,
            profile_name: 'Reinforced Concrete M30',
            family: 'Concrete',
            damage_level: 'Moderate',
            damage_state: 'Spalling',
            severity_score: 0.48,
            controlling_mode: 'Pressure',
            damage_index: 1.5,
            pressure_ratio: 1.5,
            impulse_ratio: 1.2,
          } as SweepPoint);
        });
      });
      return Promise.resolve(points);
    },

    async runGrid(params: {
      explosive_id: number;
      charges_kg: number[];
      distances_m: number[];
      profile_ids: number[];
      burst_type?: string;
    }): Promise<GridResult> {
      if (isElectron) {
        return window.api!.invoke('studies:runGrid', params);
      }
      const pts = await api.studies.distanceSweep({
        explosive_id: params.explosive_id,
        charge_kg: params.charges_kg[0] ?? 100,
        distances_m: params.distances_m,
        profile_ids: params.profile_ids,
      });
      return Promise.resolve({
        study_id: 'browser-demo',
        study_type: 'grid',
        explosive_name: 'TNT',
        charges_kg: params.charges_kg,
        distances_m: params.distances_m,
        profile_ids: params.profile_ids,
        n_points: pts.length,
        points: pts,
        summary: [{
          rank: 1,
          profile_id: 1,
          profile_name: 'Reinforced Concrete M30',
          family: 'Concrete',
          mean_severity: 0.62,
          vulnerability_score: 0.71,
          min_safe_standoff_m: 45.0,
          failure_radius_m: 12.0,
        }],
      } as GridResult);
    },

    async exportCSV(sweep_points: SweepPoint[], save_path?: string): Promise<{ path: string; n_rows: number }> {
      if (isElectron) {
        return window.api!.invoke('studies:exportCSV', { sweep_points, save_path });
      }
      // Browser: create a download link
      const headers = Object.keys(sweep_points[0] ?? {});
      const rows = sweep_points.map(p => headers.map(h => (p as any)[h]).join(','));
      const csv = [headers.join(','), ...rows].join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `blastscope_${sweep_points[0]?.study_id ?? 'export'}.csv`;
      a.click();
      return Promise.resolve({ path: 'browser-download', n_rows: sweep_points.length });
    },
  },
  database: {
    async export(): Promise<{ success: boolean; filePath?: string; error?: string; canceled?: boolean }> {
      if (isElectron) {
        return window.api!.invoke('database:export');
      }
      return Promise.resolve({ success: false, error: 'Database export is only supported in native desktop mode.' });
    },
    async import(): Promise<{ success: boolean; filePath?: string; error?: string; canceled?: boolean }> {
      if (isElectron) {
        return window.api!.invoke('database:import');
      }
      return Promise.resolve({ success: false, error: 'Database import is only supported in native desktop mode.' });
    }
  },
  inverse: {
    predict: (params: {
      burstType: string;
      incident_pressure: number;
      reflected_pressure: number;
      positive_impulse: number;
      reflected_impulse: number;
      arrival_time: number;
      positive_duration: number;
    }): Promise<{
      weight: number;
      scaled_distance: number;
      distance: number;
      confidence: number;
      model_used: string;
      ood?: boolean;
    }> => {
      if (isElectron) {
        return window.api!.invoke('inverse:predict', params);
      }
      return Promise.resolve({
        weight: 100.0,
        scaled_distance: 1.0,
        distance: 4.641588,
        confidence: 95.0,
        model_used: "Random Forest (Mock Fallback)",
        ood: false
      });
    }
  }
};

