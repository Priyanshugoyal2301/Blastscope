import { VulnerabilityRanking } from '../types';
import { ShieldAlert, ShieldCheck } from 'lucide-react';

interface RiskContourPanelProps {
  rankings: VulnerabilityRanking[];
  chargeKg?: number;
  explosiveName?: string;
}

const RANK_COLORS = ['#ef4444', '#f97316', '#fbbf24', '#84cc16', '#10b981'];

function VulnBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = score > 0.7 ? '#ef4444' : score > 0.5 ? '#f97316' : score > 0.3 ? '#fbbf24' : '#10b981';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div style={{ flex: 1, height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '3px', transition: 'width 0.5s ease' }} />
      </div>
      <span style={{ fontSize: '0.72rem', fontFamily: 'JetBrains Mono', color, minWidth: '32px' }}>{score.toFixed(3)}</span>
    </div>
  );
}

export default function RiskContourPanel({ rankings, chargeKg, explosiveName }: RiskContourPanelProps) {
  if (!rankings.length) {
    return (
      <div className="glass-panel" style={{ padding: '20px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        Run a study to see vulnerability rankings.
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '0' }}>
      {/* Header */}
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)' }}>
        <h3 style={{ fontSize: '0.95rem', color: '#fff', margin: 0 }}>
          Vulnerability Rankings
        </h3>
        {(chargeKg || explosiveName) && (
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '4px 0 0' }}>
            {explosiveName && <span>{explosiveName}</span>}
            {chargeKg && <span> · {chargeKg} kg</span>}
          </p>
        )}
      </div>

      {/* Table */}
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
        <thead>
          <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
            <th style={{ padding: '10px 14px', color: 'var(--text-muted)', textAlign: 'left', fontWeight: 600 }}>#</th>
            <th style={{ padding: '10px 14px', color: 'var(--text-muted)', textAlign: 'left', fontWeight: 600 }}>Material</th>
            <th style={{ padding: '10px 14px', color: 'var(--text-muted)', textAlign: 'left', fontWeight: 600, minWidth: '120px' }}>Vuln. Score</th>
            <th style={{ padding: '10px 14px', color: 'var(--text-muted)', textAlign: 'right', fontWeight: 600 }}>Safe Standoff</th>
            <th style={{ padding: '10px 14px', color: 'var(--text-muted)', textAlign: 'right', fontWeight: 600 }}>Failure Radius</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((r, idx) => {
            const rankColor = RANK_COLORS[Math.min(idx, RANK_COLORS.length - 1)];
            const isHighRisk = r.vulnerability_score > 0.6;
            return (
              <tr
                key={r.profile_id}
                style={{
                  borderTop: '1px solid var(--border-color)',
                  background: isHighRisk ? 'rgba(239,68,68,0.02)' : 'transparent',
                  transition: 'background 0.2s',
                }}
              >
                <td style={{ padding: '12px 14px' }}>
                  <span style={{
                    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                    width: '22px', height: '22px', borderRadius: '50%',
                    background: rankColor, color: '#fff',
                    fontSize: '0.7rem', fontWeight: 700,
                  }}>
                    {r.rank}
                  </span>
                </td>
                <td style={{ padding: '12px 14px' }}>
                  <div style={{ fontWeight: 600, color: '#e2e8f0' }}>{r.profile_name}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{r.family}</div>
                </td>
                <td style={{ padding: '12px 14px', minWidth: '130px' }}>
                  <VulnBar score={r.vulnerability_score} />
                </td>
                <td style={{ padding: '12px 14px', textAlign: 'right' }}>
                  {r.min_safe_standoff_m !== null ? (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#10b981', fontFamily: 'JetBrains Mono', fontSize: '0.78rem' }}>
                      <ShieldCheck size={12} />
                      {r.min_safe_standoff_m.toFixed(1)} m
                    </span>
                  ) : (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>— never safe</span>
                  )}
                </td>
                <td style={{ padding: '12px 14px', textAlign: 'right' }}>
                  {r.failure_radius_m !== null ? (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#ef4444', fontFamily: 'JetBrains Mono', fontSize: '0.78rem' }}>
                      <ShieldAlert size={12} />
                      {r.failure_radius_m.toFixed(1)} m
                    </span>
                  ) : (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>— no failure</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Legend */}
      <div style={{ padding: '10px 20px', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <ShieldCheck size={11} style={{ color: '#10b981' }} />
          Safe Standoff — minimum distance for "Safe" outcome
        </span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <ShieldAlert size={11} style={{ color: '#ef4444' }} />
          Failure Radius — maximum distance with "Failure" outcome
        </span>
      </div>
    </div>
  );
}
