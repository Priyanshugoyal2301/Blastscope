import { Scenario, BlastResults, DamageAssessment, ValidationSummary, ValidationCase } from '../types';

interface ReportGeneratorProps {
  scenario: Scenario | null;
  results: BlastResults | null;
  assessments: DamageAssessment[];
  validationSummary: ValidationSummary[];
  validationCases: ValidationCase[];
}

export default function ReportGenerator({
  scenario,
  results,
  assessments,
  validationSummary,
  validationCases
}: ReportGeneratorProps) {
  if (!scenario || !results) return null;

  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div id="print-report">
      {/* Report Header */}
      <div style={{ borderBottom: '3px solid #1e293b', paddingBottom: '16px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', margin: 0, fontFamily: 'sans-serif' }}>
            BlastScope Research Report
          </h1>
          <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>
            Version 0.6 · RC2
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '0.82rem', color: '#475569' }}>
          <span>Generated On: {currentDate}</span>
          <span>Model: Swisdak (1994) / UFC 3-340-02</span>
        </div>
      </div>

      {/* 1. Scenario Definition */}
      <section style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '6px', color: '#1e293b', marginBottom: '12px' }}>
          1. Scenario Definition
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '12px', fontSize: '0.88rem' }}>
          <tbody>
            <tr>
              <td style={{ padding: '6px 0', fontWeight: 600, color: '#475569', width: '30%' }}>Scenario Name:</td>
              <td style={{ padding: '6px 0', color: '#0f172a' }}>{scenario.name}</td>
            </tr>
            <tr>
              <td style={{ padding: '6px 0', fontWeight: 600, color: '#475569' }}>Charge Weight:</td>
              <td style={{ padding: '6px 0', color: '#0f172a' }}>{scenario.charge_weight} kg</td>
            </tr>
            <tr>
              <td style={{ padding: '6px 0', fontWeight: 600, color: '#475569' }}>Standoff Distance:</td>
              <td style={{ padding: '6px 0', color: '#0f172a' }}>{scenario.distance} m</td>
            </tr>
            <tr>
              <td style={{ padding: '6px 0', fontWeight: 600, color: '#475569' }}>Burst Configuration:</td>
              <td style={{ padding: '6px 0', color: '#0f172a' }}>{scenario.burst_type}</td>
            </tr>
            <tr>
              <td style={{ padding: '6px 0', fontWeight: 600, color: '#475569' }}>Unit System:</td>
              <td style={{ padding: '6px 0', color: '#0f172a' }}>{scenario.unit_system}</td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* 2. Explosive Properties */}
      <section style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '6px', color: '#1e293b', marginBottom: '12px' }}>
          2. Explosive Properties
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '12px', fontSize: '0.88rem' }}>
          <tbody>
            <tr>
              <td style={{ padding: '6px 0', fontWeight: 600, color: '#475569', width: '30%' }}>Explosive Agent:</td>
              <td style={{ padding: '6px 0', color: '#0f172a' }}>{scenario.explosive_name || 'TNT'}</td>
            </tr>
            <tr>
              <td style={{ padding: '6px 0', fontWeight: 600, color: '#475569' }}>Pressure Equivalency Factor:</td>
              <td style={{ padding: '6px 0', color: '#0f172a' }}>
                {scenario.explosive_id === 1 ? '1.00 (Baseline)' : 'Custom'}
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* 3. Blast Results */}
      <section style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '6px', color: '#1e293b', marginBottom: '12px' }}>
          3. Blast Calculation Environment
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', fontSize: '0.88rem' }}>
          <div>
            <table style={{ width: '100%' }}>
              <tbody>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Scaled Distance (Z):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.scaled_distance.toFixed(3)} m/kg¹/³</td>
                </tr>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Peak Incident Pressure (Pso):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.incident_pressure.toFixed(1)} kPa</td>
                </tr>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Peak Reflected Pressure (Pr):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.reflected_pressure.toFixed(1)} kPa</td>
                </tr>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Dynamic Pressure (Q0):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.dynamic_pressure.toFixed(1)} kPa</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div>
            <table style={{ width: '100%' }}>
              <tbody>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Positive Impulse (is):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.positive_impulse.toFixed(1)} kPa-ms</td>
                </tr>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Positive Duration (td):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.positive_duration.toFixed(2)} ms</td>
                </tr>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Negative Duration (td-):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.negative_duration.toFixed(2)} ms</td>
                </tr>
                <tr>
                  <td style={{ padding: '4px 0', fontWeight: 600, color: '#475569' }}>Arrival Time (ta):</td>
                  <td style={{ padding: '4px 0', color: '#0f172a', textAlign: 'right' }}>{results.arrival_time.toFixed(2)} ms</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* 4. Material Assessment */}
      <section style={{ marginBottom: '24px', pageBreakBefore: 'always' }}>
        <h2 style={{ fontSize: '1.25rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '6px', color: '#1e293b', marginBottom: '12px' }}>
          4. Material Assessment Results
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #0f172a', color: '#475569' }}>
              <th style={{ padding: '8px 4px' }}>Material Profile</th>
              <th style={{ padding: '8px 4px' }}>Category</th>
              <th style={{ padding: '8px 4px' }}>Damage Level</th>
              <th style={{ padding: '8px 4px', textAlign: 'right' }}>Damage Index</th>
              <th style={{ padding: '8px 4px' }}>Governing Mode</th>
              <th style={{ padding: '8px 4px' }}>Failure Mechanism</th>
            </tr>
          </thead>
          <tbody>
            {assessments.map((a, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #e2e8f0' }}>
                <td style={{ padding: '8px 4px', fontWeight: 600, color: '#0f172a' }}>{a.profile_name}</td>
                <td style={{ padding: '8px 4px', color: '#475569' }}>{a.failure_category}</td>
                <td style={{ padding: '8px 4px' }}>
                  <span style={{
                    fontWeight: 700,
                    color: a.damage_level === 'Safe' ? '#10b981' :
                           a.damage_level === 'Minor' ? '#d97706' :
                           a.damage_level === 'Moderate' ? '#ea580c' : '#dc2626'
                  }}>
                    {a.damage_level}
                  </span>
                </td>
                <td style={{ padding: '8px 4px', textAlign: 'right', fontWeight: 'bold' }}>{a.damage_index.toFixed(2)}</td>
                <td style={{ padding: '8px 4px', color: '#475569' }}>{a.controlling_mode}</td>
                <td style={{ padding: '8px 4px', color: '#475569' }}>{a.damage_mechanism}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* 5. PI Envelope Analysis */}
      <section style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '6px', color: '#1e293b', marginBottom: '12px' }}>
          5. Pressure-Impulse Envelope Analysis
        </h2>
        <p style={{ fontSize: '0.85rem', color: '#334155', lineHeight: '1.5' }}>
          Pressure-Impulse (P-I) boundaries define structural vulnerability under dynamic blast environments. If the calculated scenario coordinates 
          (Pso = {results.incident_pressure.toFixed(1)} kPa, is = {results.positive_impulse.toFixed(1)} kPa-ms) lie above a profile's capacity curve, 
          damage or failure is predicted. 
        </p>
        <p style={{ fontSize: '0.85rem', color: '#334155', lineHeight: '1.5', marginTop: '8px' }}>
          Calculations incorporate Dynamic Increase Factors (DIF) to account for material strain-rate enhancement under extreme rates of loading, 
          derived in accordance with UFC 3-340-02 equations.
        </p>
      </section>

      {/* 6. Validation Statistics */}
      {validationSummary.length > 0 && (
        <section style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '6px', color: '#1e293b', marginBottom: '12px' }}>
            6. Validation & Verification Statistics
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#334155', lineHeight: '1.5', marginBottom: '12px' }}>
            Model accuracy stats derived relative to {validationCases.length} peer-reviewed military and experimental ground-truth data points:
          </p>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #0f172a', color: '#475569' }}>
                <th style={{ padding: '6px 4px' }}>Ground Truth Class</th>
                <th style={{ padding: '6px 4px', textAlign: 'right' }}>Cases</th>
                <th style={{ padding: '6px 4px', textAlign: 'right' }}>Mean P Err</th>
                <th style={{ padding: '6px 4px', textAlign: 'right' }}>RMSE P Err</th>
                <th style={{ padding: '6px 4px', textAlign: 'right' }}>Mean I Err</th>
                <th style={{ padding: '6px 4px', textAlign: 'right' }}>RMSE I Err</th>
              </tr>
            </thead>
            <tbody>
              {validationSummary.map((sum, index) => (
                <tr key={index} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ padding: '6px 4px', fontWeight: sum.ground_truth_class.includes('TOTAL') ? 'bold' : 'normal' }}>
                    {sum.ground_truth_class}
                  </td>
                  <td style={{ padding: '6px 4px', textAlign: 'right' }}>{sum.total_cases}</td>
                  <td style={{ padding: '6px 4px', textAlign: 'right' }}>{sum.avg_pressure_error.toFixed(1)}%</td>
                  <td style={{ padding: '6px 4px', textAlign: 'right' }}>
                    {sum.rmse_pressure_error ? `${sum.rmse_pressure_error.toFixed(1)}%` : '-'}
                  </td>
                  <td style={{ padding: '6px 4px', textAlign: 'right' }}>{sum.avg_impulse_error.toFixed(1)}%</td>
                  <td style={{ padding: '6px 4px', textAlign: 'right' }}>
                    {sum.rmse_impulse_error ? `${sum.rmse_impulse_error.toFixed(1)}%` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {/* 7. Reference Citations */}
      <section style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '6px', color: '#1e293b', marginBottom: '12px' }}>
          7. Reference Standards & Citations
        </h2>
        <ul style={{ paddingLeft: '20px', fontSize: '0.82rem', color: '#475569', lineHeight: '1.6' }}>
          <li>
            <strong>UFC 3-340-02</strong>: Structures to Resist the Effects of Accidental Explosions, Unified Facilities Criteria, Department of Defense.
          </li>
          <li>
            <strong>Swisdak, M. M. (1994)</strong>: Simplified Kingery-Bulmash Equations, Naval Surface Warfare Center, Report NSWCDD/TR-93/161.
          </li>
          <li>
            <strong>TM5-1300</strong>: Design of Structures to Resist the Effects of Accidental Explosions, Department of the Army Technical Manual.
          </li>
        </ul>
      </section>

      {/* Footer Disclaimer */}
      <div style={{ borderTop: '1px solid #cbd5e1', paddingTop: '12px', marginTop: '40px', fontSize: '0.75rem', color: '#94a3b8', textAlign: 'center', lineHeight: '1.4' }}>
        Disclaimer: BlastScope calculations are provided for research and validation purposes. Detailed designs 
        subject to high-explosive loads must be verified by licensed structural engineers using professional finite element analyses.
      </div>
    </div>
  );
}
