import Plot from 'react-plotly.js';
import { MaterialProfile } from '../../types';

interface ThresholdOverlayPlotProps {
  distancePoints: number[];
  pressurePoints: number[];
  activeProfiles: MaterialProfile[];
  metricLabel: string;
}

export default function ThresholdOverlayPlot({
  distancePoints,
  pressurePoints,
  activeProfiles,
  metricLabel
}: ThresholdOverlayPlotProps) {
  
  // Find min and max distance for drawing threshold boundaries
  const minX = distancePoints.length > 0 ? Math.min(...distancePoints) : 1;
  const maxX = distancePoints.length > 0 ? Math.max(...distancePoints) : 100;

  // 1. Environmental Blast Curve
  const dataTraces: any[] = [
    {
      x: distancePoints,
      y: pressurePoints,
      type: 'scatter',
      mode: 'lines',
      name: 'Current Blast Curve',
      line: { color: '#6366f1', width: 4.5, shadow: { color: '#6366f1', width: 10 } }
    }
  ];

  // 2. Add Horizontal Threshold capacity boundaries for selected profiles
  const profileColors = ['#f43f5e', '#fb7185', '#fbbf24', '#34d399', '#60a5fa', '#a78bfa'];
  
  activeProfiles.forEach((prof, index) => {
    const color = profileColors[index % profileColors.length];
    
    // We'll show the 'Failure Pressure' and 'Moderate Pressure' as benchmark lines
    if (prof.failure_pressure) {
      dataTraces.push({
        x: [minX, maxX],
        y: [prof.failure_pressure, prof.failure_pressure],
        type: 'scatter',
        mode: 'lines',
        name: `${prof.profile_name} Failure Limit (${prof.failure_pressure} kPa)`,
        line: { color: color, dash: 'dash', width: 1.5 }
      });
    }

    if (prof.moderate_pressure) {
      dataTraces.push({
        x: [minX, maxX],
        y: [prof.moderate_pressure, prof.moderate_pressure],
        type: 'scatter',
        mode: 'lines',
        name: `${prof.profile_name} Moderate Limit (${prof.moderate_pressure} kPa)`,
        line: { color: color, dash: 'dot', width: 1.2 }
      });
    }
  });

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Plot
        data={dataTraces}
        layout={{
          title: {
            text: 'Material Vulnerability Map (Threshold Overlay Intersections)',
            font: { color: '#1f2937', family: 'Outfit', size: 16 }
          },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: '#ffffff',
          margin: { t: 50, b: 50, l: 60, r: 20 },
          xaxis: {
            title: 'Standoff Distance R (m)',
            titlefont: { color: '#4b5563' },
            tickfont: { color: '#4b5563' },
            gridcolor: '#e5e7eb',
            zerolinecolor: '#d1d5db'
          },
          yaxis: {
            title: `${metricLabel} (kPa)`,
            titlefont: { color: '#4b5563' },
            tickfont: { color: '#4b5563' },
            gridcolor: '#e5e7eb',
            zerolinecolor: '#d1d5db',
            type: 'log'
          },
          legend: {
            font: { color: '#4b5563', size: 10 },
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
