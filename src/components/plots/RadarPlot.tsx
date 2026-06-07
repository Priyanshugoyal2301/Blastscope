import Plot from 'react-plotly.js';
import { DamageAssessment } from '../../types';

interface RadarPlotProps {
  assessments: DamageAssessment[];
}

export default function RadarPlot({ assessments }: RadarPlotProps) {
  const getDamageColor = (level: string) => {
    switch (level) {
      case 'Safe': return '#10b981'; // Green
      case 'Minor': return '#fbbf24'; // Yellow
      case 'Moderate': return '#f97316'; // Orange
      case 'Severe':
      case 'Failure': return '#ef4444'; // Red
      default: return '#10b981';
    }
  };

  const theta = assessments.map(a => a.profile_name);
  const r = assessments.map(a => Math.min(a.damage_index / 4.0, 1.0));
  const markerColors = assessments.map(a => getDamageColor(a.damage_level));
  
  const text = assessments.map(a => 
    `<b>${a.profile_name}</b><br>` +
    `Damage Index: ${a.damage_index.toFixed(2)}<br>` +
    `Failure Category: ${a.failure_category}<br>` +
    `Governing Mode: ${a.controlling_mode}<br>` +
    `Damage Level: ${a.damage_level}`
  );

  // Close the loop for the polar scatter plots
  const closedTheta = [...theta];
  const closedR = [...r];
  const closedMarkerColors = [...markerColors];
  const closedText = [...text];

  if (assessments.length > 0) {
    closedTheta.push(theta[0]);
    closedR.push(r[0]);
    closedMarkerColors.push(markerColors[0]);
    closedText.push(text[0]);
  }

  const dataTraces: any[] = [
    // 1. Threshold concentric circles
    {
      type: 'scatterpolar',
      r: Array(closedTheta.length).fill(0.25),
      theta: closedTheta,
      mode: 'lines',
      name: 'Minor Damage Boundary (DI = 1.0)',
      line: { color: '#fbbf24', dash: 'dash', width: 1.2 },
      hoverinfo: 'none',
      showlegend: true
    },
    {
      type: 'scatterpolar',
      r: Array(closedTheta.length).fill(0.5),
      theta: closedTheta,
      mode: 'lines',
      name: 'Moderate Damage Boundary (DI = 2.0)',
      line: { color: '#f97316', dash: 'dash', width: 1.2 },
      hoverinfo: 'none',
      showlegend: true
    },
    {
      type: 'scatterpolar',
      r: Array(closedTheta.length).fill(1.0),
      theta: closedTheta,
      mode: 'lines',
      name: 'Severe Damage Boundary (DI = 4.0)',
      line: { color: '#ef4444', dash: 'dash', width: 1.5 },
      hoverinfo: 'none',
      showlegend: true
    },
    // 2. Main shaded vulnerability polygon
    {
      type: 'scatterpolar',
      r: closedR,
      theta: closedTheta,
      fill: 'toself',
      fillcolor: 'rgba(99, 102, 241, 0.25)',
      mode: 'lines+markers',
      name: 'Scenario Damage Index',
      line: {
        color: '#6366f1',
        width: 2.5
      },
      marker: {
        color: closedMarkerColors,
        size: 9,
        line: {
          color: '#111827',
          width: 1.5
        }
      },
      hoverinfo: 'text',
      text: closedText,
      showlegend: true
    }
  ];

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Plot
        data={dataTraces}
        layout={{
          title: {
            text: 'Material Vulnerability Radar (Normalized DI)',
            font: { color: '#ffffff', family: 'Outfit', size: 16 }
          },
          paper_bgcolor: 'rgba(0,0,0,0)',
          margin: { t: 50, b: 30, l: 30, r: 30 },
          polar: {
            radialaxis: {
              visible: true,
              range: [0, 1.0],
              tickvals: [0, 0.25, 0.5, 0.75, 1.0],
              ticktext: ['Safe (0)', 'Minor (1)', 'Mod (2)', '3', 'Severe (4+)'],
              tickfont: { color: '#9ca3af', size: 8 },
              gridcolor: 'rgba(255, 255, 255, 0.05)',
              linecolor: 'rgba(255, 255, 255, 0.1)'
            },
            angularaxis: {
              tickfont: { color: '#ffffff', size: 10, family: 'Outfit' },
              gridcolor: 'rgba(255, 255, 255, 0.05)',
              linecolor: 'rgba(255, 255, 255, 0.1)',
              direction: 'clockwise'
            },
            bgcolor: 'rgba(17, 22, 41, 0.4)'
          },
          legend: {
            font: { color: '#9ca3af', size: 9 },
            orientation: 'h',
            y: -0.15
          },
          autosize: true
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}
