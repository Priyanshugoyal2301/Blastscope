declare module 'react-plotly.js' {
  import * as React from 'react';
  
  export interface PlotParams {
    data: any[];
    layout: any;
    useResizeHandler?: boolean;
    style?: React.CSSProperties;
    onInitialized?: (figure: any, graphDiv: any) => void;
    onUpdate?: (figure: any, graphDiv: any) => void;
    className?: string;
  }
  
  export default class Plot extends React.Component<PlotParams> {}
}
