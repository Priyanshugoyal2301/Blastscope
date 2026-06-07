import Plot from 'react-plotly.js';

interface BlastCurvePlotProps {
  x: number[];
  incidentY: number[];
  reflectedY: number[];
  title?: string;
}

export default function BlastCurvePlot({ x, incidentY, reflectedY, title }: BlastCurvePlotProps) {
  // Generate bounds
  const incU10 = incidentY.map(y => y * 1.10);
  const incL10 = incidentY.map(y => y * 0.90);
  const incU5 = incidentY.map(y => y * 1.05);
  const incL5 = incidentY.map(y => y * 0.95);

  const refU10 = reflectedY.map(y => y * 1.10);
  const refL10 = reflectedY.map(y => y * 0.90);
  const refU5 = reflectedY.map(y => y * 1.05);
  const refL5 = reflectedY.map(y => y * 0.95);

  const dataTraces: any[] = [];

  if (x.length > 0) {
    // Incident 10% envelope
    dataTraces.push({
      x: x,
      y: incU10,
      type: 'scatter',
      mode: 'lines',
      line: { color: 'transparent' },
      showlegend: false,
      hoverinfo: 'skip'
    });
    dataTraces.push({
      x: x,
      y: incL10,
      type: 'scatter',
      mode: 'lines',
      fill: 'tonexty',
      fillcolor: 'rgba(99, 102, 241, 0.05)',
      line: { color: 'transparent' },
      name: 'Incident ±10% Margin',
      hoverinfo: 'skip'
    });

    // Incident 5% envelope
    dataTraces.push({
      x: x,
      y: incU5,
      type: 'scatter',
      mode: 'lines',
      line: { color: 'transparent' },
      showlegend: false,
      hoverinfo: 'skip'
    });
    dataTraces.push({
      x: x,
      y: incL5,
      type: 'scatter',
      mode: 'lines',
      fill: 'tonexty',
      fillcolor: 'rgba(99, 102, 241, 0.12)',
      line: { color: 'transparent' },
      name: 'Incident ±5% Margin',
      hoverinfo: 'skip'
    });

    // Reflected 10% envelope
    dataTraces.push({
      x: x,
      y: refU10,
      type: 'scatter',
      mode: 'lines',
      line: { color: 'transparent' },
      showlegend: false,
      hoverinfo: 'skip'
    });
    dataTraces.push({
      x: x,
      y: refL10,
      type: 'scatter',
      mode: 'lines',
      fill: 'tonexty',
      fillcolor: 'rgba(217, 70, 239, 0.04)',
      line: { color: 'transparent' },
      name: 'Reflected ±10% Margin',
      hoverinfo: 'skip'
    });

    // Reflected 5% envelope
    dataTraces.push({
      x: x,
      y: refU5,
      type: 'scatter',
      mode: 'lines',
      line: { color: 'transparent' },
      showlegend: false,
      hoverinfo: 'skip'
    });
    dataTraces.push({
      x: x,
      y: refL5,
      type: 'scatter',
      mode: 'lines',
      fill: 'tonexty',
      fillcolor: 'rgba(217, 70, 239, 0.10)',
      line: { color: 'transparent' },
      name: 'Reflected ±5% Margin',
      hoverinfo: 'skip'
    });
  }

  // Central curves
  dataTraces.push({
    x: x,
    y: incidentY,
    type: 'scatter',
    mode: 'lines',
    name: 'Incident Pressure (Pso)',
    line: { color: '#6366f1', width: 3 }
  });

  dataTraces.push({
    x: x,
    y: reflectedY,
    type: 'scatter',
    mode: 'lines',
    name: 'Reflected Pressure (Pr)',
    line: { color: '#d946ef', width: 3 }
  });

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Plot
        data={dataTraces}
        layout={{
          title: {
            text: title || 'Blast Overpressure vs. Distance',
            font: { color: '#ffffff', family: 'Inter', size: 14 }
          },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(17, 22, 41, 0.4)',
          margin: { t: 40, b: 50, l: 60, r: 20 },
          xaxis: {
            title: 'Standoff Distance R (m)',
            titlefont: { color: '#9ca3af', size: 11 },
            tickfont: { color: '#9ca3af', size: 10 },
            gridcolor: 'rgba(255, 255, 255, 0.05)',
            zerolinecolor: 'rgba(255, 255, 255, 0.1)'
          },
          yaxis: {
            title: 'Overpressure (kPa)',
            titlefont: { color: '#9ca3af', size: 11 },
            tickfont: { color: '#9ca3af', size: 10 },
            gridcolor: 'rgba(255, 255, 255, 0.05)',
            zerolinecolor: 'rgba(255, 255, 255, 0.1)',
            type: 'log' // Standard log scale for blast pressure decays
          },
          legend: {
            font: { color: '#9ca3af', size: 9 },
            orientation: 'h',
            y: -0.25
          },
          autosize: true
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}
