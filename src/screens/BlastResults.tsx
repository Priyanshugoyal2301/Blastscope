import { Scenario, BlastResults } from '../types';
import { Shield } from 'lucide-react';

interface BlastResultsProps {
  activeScenario: Scenario | null;
  results: BlastResults | null;
}

export default function BlastResultsScreen({ activeScenario, results }: BlastResultsProps) {
  if (!activeScenario || !results) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }} className="animate-fade-in">
        Please select or save a scenario to view computed blast environmental results.
      </div>
    );
  }

  const isMetric = activeScenario.unit_system === 'Metric';

  // Units formatting
  const pUnit = isMetric ? 'kPa' : 'psi';
  const sdUnit = isMetric ? 'm/kg¹/³' : 'ft/lb¹/³';
  const iUnit = isMetric ? 'kPa-ms' : 'psi-ms';

  const cards = [
    { label: 'Scaled Distance (Z)', value: `${results.scaled_distance.toFixed(3)}`, unit: sdUnit, desc: 'Distance scaled by charge weight cube root.' },
    { label: 'Incident Pressure (Pso)', value: `${results.incident_pressure.toFixed(2)}`, unit: pUnit, desc: 'Peak shock front overpressure.' },
    { label: 'Reflected Pressure (Pr)', value: `${results.reflected_pressure.toFixed(2)}`, unit: pUnit, desc: 'Reflected front shock overpressure.' },
    { label: 'Positive Impulse (is)', value: `${results.positive_impulse.toFixed(2)}`, unit: iUnit, desc: 'Integral of positive phase overpressure.' },
    { label: 'Dynamic Pressure (q)', value: `${results.dynamic_pressure.toFixed(2)}`, unit: pUnit, desc: 'Pressure from blast wind velocity.' },
    { label: 'Arrival Time (ta)', value: `${results.arrival_time.toFixed(2)}`, unit: 'ms', desc: 'Time for shock front to reach standoff.' },
    { label: 'Positive Duration (to)', value: `${results.positive_duration.toFixed(2)}`, unit: 'ms', desc: 'Duration of positive pressure phase.' },
    { label: 'Negative Duration (to-)', value: `${results.negative_duration.toFixed(2)}`, unit: 'ms', desc: 'Duration of negative suction phase.' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }} className="animate-fade-in">
      {/* Overview Card */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', color: '#fff' }}>Calculated Wave Environment</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Scenario: <strong style={{ color: '#fff' }}>{activeScenario.name}</strong> ({activeScenario.charge_weight} kg equivalent)
          </p>
        </div>

        {/* Model Provenance */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', padding: '8px 14px', borderRadius: '8px' }}>
          <Shield size={16} style={{ color: 'var(--primary)' }} />
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 500 }}>Provenance Model</div>
            <div style={{ fontSize: '0.82rem', color: '#fff', fontWeight: 600 }}>
              {results.model_used} <span style={{ color: 'var(--accent)', fontSize: '0.75rem' }}>{results.model_version}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Grid cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px' }}>
        {cards.map((card, index) => (
          <div key={index} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.02em' }}>
              {card.label}
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', margin: '4px 0' }}>
              <span style={{ fontSize: '1.8rem', fontWeight: 700, color: '#fff', fontFamily: 'Outfit' }}>
                {card.value}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                {card.unit}
              </span>
            </div>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>
              {card.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
