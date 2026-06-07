import { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { MaterialProfile, BlastResults, PIEnvelope } from '../../types';
import { api } from '../../services/api';

interface PIPlotProps {
  activeResults: BlastResults;
  profiles: MaterialProfile[];
}

export default function PIPlot({ activeResults, profiles }: PIPlotProps) {
  const [selectedProfileId, setSelectedProfileId] = useState<number>(
    profiles.length > 0 ? profiles[0].id : 0
  );
  const [envelopes, setEnvelopes] = useState<PIEnvelope[]>([]);
  const [loading, setLoading] = useState(false);

  // Auto-select first profile if none is selected
  useEffect(() => {
    if (profiles.length > 0 && !selectedProfileId) {
      setSelectedProfileId(profiles[0].id);
    }
  }, [profiles]);

  useEffect(() => {
    if (selectedProfileId) {
      setLoading(true);
      api.materials.getPIEnvelopes(selectedProfileId)
        .then((res) => {
          setEnvelopes(res);
          setLoading(false);
        })
        .catch((err) => {
          console.error('Failed to load P-I envelopes:', err);
          setLoading(false);
        });
    }
  }, [selectedProfileId]);

  const activeProfile = profiles.find((p) => p.id === selectedProfileId);

  // Determine scenario point based on material type
  // Facades (Glass, Masonry) use Reflected Pressure. Structure (Concrete, Steel) uses Incident Pressure.
  const isFacade = activeProfile
    ? activeProfile.family === 'Glass' || activeProfile.family === 'Masonry'
    : true;

  const P_load = isFacade ? activeResults.reflected_pressure : activeResults.incident_pressure;
  const I_load = activeResults.positive_impulse;

  const dataTraces: any[] = [];

  // Plot envelopes (hyperbolic) if loaded, else fall back to orthogonal thresholds
  if (envelopes && envelopes.length > 0) {
    const colorMap: Record<string, string> = {
      'Minor': '#10b981',      // Green
      'Moderate': '#fbbf24',   // Yellow
      'Severe': '#f97316',     // Orange
      'Failure': '#ef4444'      // Red
    };
    const dashMap: Record<string, string> = {
      'Minor': 'dot',
      'Moderate': 'dashdot',
      'Severe': 'dash',
      'Failure': 'solid'
    };

    envelopes.forEach((env) => {
      const color = colorMap[env.damage_state] || '#ffffff';
      const dash = dashMap[env.damage_state] || 'solid';

      if (env.points && env.points.length > 0) {
        dataTraces.push({
          x: env.points.map((pt) => pt.impulse),
          y: env.points.map((pt) => pt.pressure),
          type: 'scatter',
          mode: 'lines',
          name: `${env.damage_state} (${env.confidence_level} Conf)`,
          line: { color, dash, width: 2.2 },
          hovertemplate: `<b>${env.damage_state} Limit</b><br>` +
                         `Impulse: %{x:.1f} kPa-ms<br>` +
                         `Pressure: %{y:.1f} kPa<br>` +
                         `Eq: ${env.equation_text}<br>` +
                         `Ref: ${env.source_reference}<extra></extra>`
        });
      }
    });
  } else if (activeProfile) {
    // Orthogonal fallback
    const limits = [
      { name: 'Minor Limit', p: activeProfile.minor_pressure, i: activeProfile.minor_impulse, color: '#10b981', dash: 'dot' },
      { name: 'Moderate Limit', p: activeProfile.moderate_pressure, i: activeProfile.moderate_impulse, color: '#fbbf24', dash: 'dashdot' },
      { name: 'Severe Limit', p: activeProfile.severe_pressure, i: activeProfile.severe_impulse, color: '#f97316', dash: 'dash' },
      { name: 'Failure Limit', p: activeProfile.failure_pressure, i: activeProfile.failure_impulse, color: '#ef4444', dash: 'solid' },
    ];

    limits.forEach((lim) => {
      if (lim.p && lim.i) {
        dataTraces.push({
          x: [lim.i, lim.i, 100000],
          y: [100000, lim.p, lim.p],
          type: 'scatter',
          mode: 'lines',
          name: `${lim.name} (P: ${lim.p} kPa, I: ${lim.i} kPa-ms)`,
          line: { color: lim.color, dash: lim.dash, width: 2 },
        });
      }
    });
  }

  // Add the current scenario blast load point
  dataTraces.push({
    x: [I_load],
    y: [P_load],
    type: 'scatter',
    mode: 'markers',
    name: 'Current Scenario Load',
    marker: {
      color: '#3b82f6',
      size: 14,
      symbol: 'cross-open-dot',
      line: { color: '#ffffff', width: 2 },
    },
    hovertemplate: `<b>Current Load</b><br>Impulse: %{x:.1f} kPa-ms<br>Pressure: %{y:.1f} kPa<extra></extra>`
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: 0, fontSize: '0.9rem', color: '#fff' }}>
          P-I Diagram ({isFacade ? 'Reflected Loading' : 'Incident Loading'})
        </h4>
        <select
          value={selectedProfileId}
          onChange={(e) => setSelectedProfileId(Number(e.target.value))}
          style={{
            background: '#0b0f19',
            border: '1px solid var(--border-color)',
            color: '#fff',
            fontSize: '0.8rem',
            padding: '4px 8px',
            borderRadius: '3px',
            outline: 'none',
          }}
        >
          {profiles.map((p) => (
            <option key={p.id} value={p.id}>
              {p.profile_name}
            </option>
          ))}
        </select>
      </div>

      <div style={{ flex: 1, minHeight: 0 }}>
        <Plot
          data={dataTraces}
          layout={{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(17, 22, 41, 0.4)',
            margin: { t: 10, b: 45, l: 55, r: 20 },
            xaxis: {
              title: 'Impulse (kPa-ms)',
              titlefont: { color: '#9ca3af', size: 11 },
              tickfont: { color: '#9ca3af', size: 10 },
              gridcolor: 'rgba(255, 255, 255, 0.05)',
              zerolinecolor: 'rgba(255, 255, 255, 0.1)',
              type: 'log',
              range: [0, 4.5], // 10^0 = 1 to 10^4.5 = 31,600
            },
            yaxis: {
              title: 'Overpressure (kPa)',
              titlefont: { color: '#9ca3af', size: 11 },
              tickfont: { color: '#9ca3af', size: 10 },
              gridcolor: 'rgba(255, 255, 255, 0.05)',
              zerolinecolor: 'rgba(255, 255, 255, 0.1)',
              type: 'log',
              range: [0, 4.5],
            },
            legend: {
              font: { color: '#9ca3af', size: 9 },
              orientation: 'h',
              y: -0.15,
            },
            showlegend: true,
            autosize: true,
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
        />
      </div>

      <div
        style={{
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          padding: '6px 10px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderLeft: '2px solid var(--primary)',
        }}
      >
        {loading ? (
          <span>Loading hyperbolic envelopes...</span>
        ) : envelopes.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            <div><strong>Active Capacity Envelopes:</strong> Derived hyperbolas <code>(P-P0)(I-I0) = Kc</code></div>
            <div style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
              {envelopes.map(e => `${e.damage_state}: ${e.confidence_level} Confidence`).join(' | ')}
            </div>
          </div>
        ) : (
          <span>No hyperbolic envelopes available for this profile.</span>
        )}
      </div>
    </div>
  );
}
