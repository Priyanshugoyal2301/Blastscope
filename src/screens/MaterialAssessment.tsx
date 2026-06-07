import { Scenario, DamageAssessment } from '../types';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

interface MaterialAssessmentProps {
  activeScenario: Scenario | null;
  assessments: DamageAssessment[];
}

export default function MaterialAssessmentScreen({ activeScenario, assessments }: MaterialAssessmentProps) {
  if (!activeScenario || assessments.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }} className="animate-fade-in">
        Please select or save a scenario to view computed material assessment reports.
      </div>
    );
  }

  const getBadgeClass = (level: string) => {
    switch (level) {
      case 'Safe': return 'badge-safe';
      case 'Minor': return 'badge-minor';
      case 'Moderate': return 'badge-moderate';
      case 'Severe': return 'badge-severe';
      case 'Failure': return 'badge-failure';
      default: return 'badge-safe';
    }
  };

  const getConfidenceColor = (conf?: string) => {
    switch (conf) {
      case 'High': return '#10b981';
      case 'Medium': return '#fbbf24';
      case 'Low': return '#f97316';
      default: return 'var(--text-muted)';
    }
  };

  const getSeverityBar = (score?: number, level?: string) => {
    if (score === undefined || score === null) return null;
    const pct = Math.min(100, Math.max(0, score * 100));
    let color = '#10b981';
    if (level === 'Minor') color = '#fbbf24';
    else if (level === 'Moderate') color = '#f97316';
    else if (level === 'Severe' || level === 'Failure') color = '#ef4444';
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ flex: 1, height: '5px', background: 'rgba(255,255,255,0.08)', borderRadius: '2px' }}>
          <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '2px', transition: 'width 0.4s' }} />
        </div>
        <span style={{ fontSize: '0.75rem', fontFamily: 'JetBrains Mono', color, minWidth: '30px' }}>
          {score.toFixed(2)}
        </span>
      </div>
    );
  };

  const sortedAssessments = [...assessments].sort((a, b) => b.damage_index - a.damage_index);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }} className="animate-fade-in">
      <div className="glass-panel" style={{ padding: '20px' }}>
        <h2 style={{ fontSize: '1.2rem', color: '#fff' }}>Material Damage Assessment</h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Progressive physical response assessment for <strong style={{ color: '#fff' }}>{activeScenario.name}</strong>.
          Material models return physics-grounded damage states with severity scores and confidence ratings.
        </p>
      </div>

      {/* Matrix Table */}
      <div className="glass-panel" style={{ overflow: 'auto', padding: 0 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', background: 'rgba(255, 255, 255, 0.02)' }}>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Material Target</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Family</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Level</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)', minWidth: '140px' }}>Physical State</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)', minWidth: '150px' }}>Severity Score</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)', textAlign: 'right' }}>DI</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Mode</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)', minWidth: '200px' }}>Failure Mechanism</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)', textAlign: 'right' }}>P Ratio</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)', textAlign: 'right' }}>i Ratio</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Confidence</th>
              <th style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Model Version</th>
            </tr>
          </thead>
          <tbody>
            {sortedAssessments.map((ass) => {
              const isDanger = ass.damage_level === 'Severe' || ass.damage_level === 'Failure';
              const confColor = getConfidenceColor(ass.confidence_level);
              return (
                <tr 
                  key={ass.profile_id} 
                  style={{ 
                    borderBottom: '1px solid var(--border-color)',
                    background: isDanger ? 'rgba(239, 68, 68, 0.01)' : 'transparent',
                    transition: 'all 0.2s'
                  }}
                >
                  <td style={{ padding: '14px 16px', fontWeight: 600, color: '#fff', whiteSpace: 'nowrap' }}>
                    {ass.profile_name}
                  </td>
                  <td style={{ padding: '14px 16px', color: 'var(--text-muted)' }}>
                    {ass.family}
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span className={`badge ${getBadgeClass(ass.damage_level)}`}>
                      {ass.damage_level}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', color: '#e2e8f0', fontWeight: 500 }}>
                    {ass.damage_state || ass.damage_level}
                  </td>
                  <td style={{ padding: '14px 16px', minWidth: '150px' }}>
                    {getSeverityBar(ass.severity_score, ass.damage_level)}
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 'bold', fontFamily: 'JetBrains Mono', color: ass.damage_index >= 1 ? 'var(--status-failure)' : 'var(--text-main)' }}>
                    {ass.damage_index.toFixed(2)}
                  </td>
                  <td style={{ padding: '14px 16px', color: 'var(--text-muted)' }}>
                    {ass.controlling_mode}
                  </td>
                  <td style={{ padding: '14px 16px', fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '220px', whiteSpace: 'normal', lineHeight: '1.4' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                      {isDanger ? <AlertTriangle size={13} style={{ color: 'var(--status-failure)', flexShrink: 0, marginTop: '2px' }} /> : <ShieldCheck size={13} style={{ color: 'var(--status-safe)', flexShrink: 0, marginTop: '2px' }} />}
                      <span>{ass.damage_mechanism}</span>
                    </div>
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 'bold', fontFamily: 'JetBrains Mono', color: ass.pressure_ratio > 1 ? 'var(--status-failure)' : 'var(--text-main)' }}>
                    {ass.pressure_ratio.toFixed(2)}x
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 'bold', fontFamily: 'JetBrains Mono', color: ass.impulse_ratio > 1 ? 'var(--status-failure)' : 'var(--text-main)' }}>
                    {ass.impulse_ratio.toFixed(2)}x
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      color: confColor,
                      border: `1px solid ${confColor}`,
                      borderRadius: '3px',
                      padding: '2px 6px',
                      opacity: 0.9
                    }}>
                      {ass.confidence_level || 'High'}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono', whiteSpace: 'nowrap' }}>
                    {ass.response_model_version || 'v1.0'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
