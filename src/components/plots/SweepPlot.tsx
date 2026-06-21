import { useMemo } from 'react';
import Plot from 'react-plotly.js';
import { SweepPoint } from '../../types';

interface SweepPlotProps {
  points: SweepPoint[];
  xAxis: 'distance_m' | 'charge_kg' | 'scaled_distance';
  yAxis: 'peak_pressure_kPa' | 'peak_impulse_kPa_ms' | 'severity_score';
  groupBy: 'profile_name' | 'explosive_name';
  title?: string;
}

const DAMAGE_COLORS: Record<string, string> = {
  Safe: '#10b981',
  Minor: '#fbbf24',
  Moderate: '#f97316',
  Severe: '#ef4444',
  Failure: '#7c3aed',
};

const Y_LABELS: Record<string, string> = {
  peak_pressure_kPa: 'Peak Pressure (kPa)',
  peak_impulse_kPa_ms: 'Specific Impulse (kPa·ms)',
  severity_score: 'Severity Score',
};

const X_LABELS: Record<string, string> = {
  distance_m: 'Standoff Distance (m)',
  charge_kg: 'Charge Weight (kg)',
  scaled_distance: 'Scaled Distance Z (m·kg⁻¹/³)',
};

export default function SweepPlot({ points, xAxis, yAxis, groupBy, title }: SweepPlotProps) {
  const traces = useMemo(() => {
    const groups: Record<string, SweepPoint[]> = {};
    points.forEach(p => {
      const key = p[groupBy] as string;
      if (!groups[key]) groups[key] = [];
      groups[key].push(p);
    });

    return Object.entries(groups).map(([label, pts]) => {
      const sorted = [...pts].sort((a, b) => (a[xAxis] as number) - (b[xAxis] as number));
      const x = sorted.map(p => p[xAxis]);
      const y = sorted.map(p => p[yAxis] as number);
      const colors = sorted.map(p => DAMAGE_COLORS[p.damage_level] ?? '#94a3b8');
      const hoverText = sorted.map(p =>
        `<b>${p.profile_name}</b><br>` +
        `${X_LABELS[xAxis]}: ${(p[xAxis] as number).toFixed(2)}<br>` +
        `${Y_LABELS[yAxis]}: ${(p[yAxis] as number).toFixed(3)}<br>` +
        `Damage: <b>${p.damage_state}</b><br>` +
        `Severity: ${(p.severity_score * 100).toFixed(1)}%<br>` +
        `Z = ${p.scaled_distance.toFixed(3)} m·kg⁻¹/³`
      );

      return {
        type: 'scatter' as const,
        mode: 'lines+markers' as const,
        name: label,
        x,
        y,
        text: hoverText,
        hoverinfo: 'text' as const,
        marker: {
          color: colors,
          size: 8,
          symbol: 'circle',
          line: { color: 'rgba(255,255,255,0.3)', width: 1 },
        },
        line: { color: DAMAGE_COLORS[pts[0]?.damage_level] ?? '#64748b', width: 2 },
      };
    });
  }, [points, xAxis, yAxis, groupBy]);

  const layout = useMemo(() => ({
    title: {
      text: title ?? `${Y_LABELS[yAxis]} vs ${X_LABELS[xAxis]}`,
      font: { color: '#1f2937', size: 14 },
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: '#ffffff',
    font: { color: '#4b5563', family: 'Inter, system-ui, sans-serif', size: 11 },
    xaxis: {
      title: { text: X_LABELS[xAxis], font: { color: '#4b5563' } },
      gridcolor: '#e5e7eb',
      zerolinecolor: '#d1d5db',
      type: (xAxis === 'scaled_distance' ? 'log' : 'linear') as 'log' | 'linear',
    },
    yaxis: {
      title: { text: Y_LABELS[yAxis], font: { color: '#4b5563' } },
      gridcolor: '#e5e7eb',
      type: 'log' as const,
    },
    legend: {
      bgcolor: 'rgba(255, 255, 255, 0.9)',
      bordercolor: '#e5e7eb',
      borderwidth: 1,
      font: { color: '#4b5563', size: 10 },
    },
    margin: { l: 60, r: 20, t: 48, b: 56 },
    shapes: [],
  }), [xAxis, yAxis, title]);

  if (!points.length) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        No sweep data to display. Run a study first.
      </div>
    );
  }

  return (
    <Plot
      data={traces as any}
      layout={layout as any}
      useResizeHandler={true}
      style={{ width: '100%', height: '340px' }}
    />
  );
}
