import Plot from 'react-plotly.js';

interface ScenarioCurve {
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
}

interface ComparisonPlotProps {
  scenariosCurves: ScenarioCurve[];
  metric: 'incident_pressure' | 'reflected_pressure' | 'positive_impulse';
  metricLabel: string;
}

export default function ComparisonPlot({ scenariosCurves, metric, metricLabel }: ComparisonPlotProps) {
  const colors = ['#6366f1', '#10b981', '#f59e0b', '#d946ef', '#3b82f6'];

  const traces = scenariosCurves.map((sc, index) => ({
    x: sc.curve.map(pt => pt.distance),
    y: sc.curve.map(pt => pt[metric]),
    type: 'scatter' as const,
    mode: 'lines' as const,
    name: `${sc.scenarioName} (${sc.chargeWeight}kg ${sc.explosiveName})`,
    line: { color: colors[index % colors.length], width: 2.5 }
  }));

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Plot
        data={traces}
        layout={{
          title: {
            text: `Comparative ${metricLabel} Curves`,
            font: { color: '#1f2937', family: 'Outfit', size: 16 }
          },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: '#ffffff',
          margin: { t: 50, b: 50, l: 60, r: 20 },
          xaxis: {
            title: 'Distance (m)',
            titlefont: { color: '#4b5563' },
            tickfont: { color: '#4b5563' },
            gridcolor: '#e5e7eb',
            zerolinecolor: '#d1d5db'
          },
          yaxis: {
            title: `${metricLabel}`,
            titlefont: { color: '#4b5563' },
            tickfont: { color: '#4b5563' },
            gridcolor: '#e5e7eb',
            zerolinecolor: '#d1d5db',
            type: 'log'
          },
          legend: {
            font: { color: '#4b5563' },
            orientation: 'h',
            y: -0.2
          },
          autosize: true
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}
