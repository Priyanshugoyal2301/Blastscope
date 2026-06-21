import { useMemo } from 'react';
import Plot from 'react-plotly.js';
import { SweepPoint } from '../../types';

interface HeatmapPlotProps {
  points: SweepPoint[];
  profileId: number;
  charges_kg: number[];
  distances_m: number[];
  title?: string;
}

// Map severity_score (0–1) to a discrete 5-band colorscale
const COLORSCALE: [number, string][] = [
  [0.00, '#10b981'],   // Safe — green
  [0.20, '#84cc16'],   // Safe → Minor transition
  [0.25, '#fbbf24'],   // Minor — amber
  [0.40, '#f97316'],   // Moderate — orange
  [0.60, '#ef4444'],   // Severe — red
  [0.80, '#b91c1c'],   // Severe → Failure
  [1.00, '#7c3aed'],   // Failure — purple
];

export default function HeatmapPlot({ points, profileId, charges_kg, distances_m, title }: HeatmapPlotProps) {
  const { z, hoverText } = useMemo(() => {
    // Build a lookup: (charge, distance) → point
    const lookup: Record<string, SweepPoint> = {};
    points.forEach(p => {
      if (p.profile_id === profileId) {
        lookup[`${p.charge_kg}_${p.distance_m}`] = p;
      }
    });

    const sortedC = [...charges_kg].sort((a, b) => a - b);
    const sortedD = [...distances_m].sort((a, b) => a - b);

    // z[row=charge][col=distance] = severity_score
    const zMatrix: number[][] = sortedC.map(c =>
      sortedD.map(d => {
        const pt = lookup[`${c}_${d}`];
        return pt ? pt.severity_score : 0;
      })
    );

    const hoverMatrix: string[][] = sortedC.map(c =>
      sortedD.map(d => {
        const pt = lookup[`${c}_${d}`];
        if (!pt) return `No data`;
        return (
          `<b>${pt.profile_name}</b><br>` +
          `Charge: ${c} kg | Distance: ${d} m<br>` +
          `Z = ${pt.scaled_distance.toFixed(3)}<br>` +
          `<b>${pt.damage_state}</b> (${pt.damage_level})<br>` +
          `Severity: ${(pt.severity_score * 100).toFixed(1)}%<br>` +
          `Peak P: ${pt.peak_pressure_kPa.toFixed(1)} kPa`
        );
      })
    );

    return { z: zMatrix, hoverText: hoverMatrix };
  }, [points, profileId, charges_kg, distances_m]);

  const sortedC = [...charges_kg].sort((a, b) => a - b);
  const sortedD = [...distances_m].sort((a, b) => a - b);

  const data = [{
    type: 'heatmap' as const,
    z,
    x: sortedD,
    y: sortedC,
    text: hoverText,
    hoverinfo: 'text' as const,
    colorscale: COLORSCALE,
    zmin: 0,
    zmax: 1,
    colorbar: {
      title: { text: 'Severity', font: { color: '#4b5563', size: 11 } },
      tickvals: [0, 0.2, 0.4, 0.6, 0.8, 1.0],
      ticktext: ['0 (Safe)', '0.2', '0.4 (Moderate)', '0.6', '0.8 (Severe)', '1.0 (Failure)'],
      tickfont: { color: '#4b5563', size: 9 },
      len: 0.9,
    },
  }];

  const layout = {
    title: {
      text: title ?? 'Vulnerability Heatmap (Charge × Distance)',
      font: { color: '#1f2937', size: 14 },
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: '#ffffff',
    font: { color: '#4b5563', family: 'Inter, system-ui, sans-serif', size: 11 },
    xaxis: {
      title: { text: 'Standoff Distance (m)', font: { color: '#4b5563' } },
      gridcolor: '#e5e7eb',
    },
    yaxis: {
      title: { text: 'Charge Weight (kg)', font: { color: '#4b5563' } },
      gridcolor: '#e5e7eb',
    },
    margin: { l: 70, r: 20, t: 48, b: 60 },
  };

  if (!points.length) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '320px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        No grid data to display. Run a Grid Study first.
      </div>
    );
  }

  return (
    <Plot
      data={data as any}
      layout={layout as any}
      useResizeHandler={true}
      style={{ width: '100%', height: '360px' }}
    />
  );
}
