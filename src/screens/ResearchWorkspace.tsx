import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Scenario, BlastResults, MaterialProfile, DamageAssessment, ValidationCase, ValidationSummary } from '../types';
import BlastCurvePlot from '../components/plots/BlastCurvePlot';
import ComparisonPlot from '../components/plots/ComparisonPlot';
import ThresholdOverlayPlot from '../components/plots/ThresholdOverlayPlot';
import RadarPlot from '../components/plots/RadarPlot';
import PIPlot from '../components/plots/PIPlot';
import ExportMenu from '../components/ExportMenu';
import { BarChart3, Layers, Sliders, AlertCircle, TrendingUp, ShieldAlert, CheckSquare, RefreshCw } from 'lucide-react';

interface ResearchWorkspaceProps {
  activeScenario: Scenario | null;
  activeResults: BlastResults | null;
  profiles: MaterialProfile[];
  assessments: DamageAssessment[];
  validationSummary: ValidationSummary[];
  validationCases: ValidationCase[];
  onReloadValidation: () => Promise<void>;
}

export default function ResearchWorkspace({
  activeScenario,
  activeResults,
  profiles,
  assessments,
  validationSummary,
  validationCases,
  onReloadValidation
}: ResearchWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<'analysis' | 'comparison' | 'parametric' | 'vulnerability' | 'radar' | 'validation'>('analysis');
  
  // Single Scenario sweep data
  const [singleSweepX, setSingleSweepX] = useState<number[]>([]);
  const [singleIncidentY, setSingleIncidentY] = useState<number[]>([]);
  const [singleReflectedY, setSingleReflectedY] = useState<number[]>([]);

  // Scenario Comparison data
  const [scenariosList, setScenariosList] = useState<Scenario[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<number[]>([]);
  const [comparisonCurves, setComparisonCurves] = useState<any[]>([]);
  const [comparisonMetric, setComparisonMetric] = useState<'incident_pressure' | 'reflected_pressure' | 'positive_impulse'>('incident_pressure');

  // Parametric sweep configurations
  const [sweepVar, setSweepVar] = useState<'distance' | 'chargeWeight'>('distance');
  const [minVal, setMinVal] = useState(1);
  const [maxVal, setMaxVal] = useState(100);
  const [stepVal, setStepVal] = useState(2);
  const [sweepResults, setSweepResults] = useState<any[]>([]);

  // Selected profiles for Vulnerability Overlay
  const [selectedProfiles, setSelectedProfiles] = useState<number[]>([]);

  // Validation States
  const [sourceDist, setSourceDist] = useState<Array<{ source: string; cases: number }>>([]);
  const [isValidating, setIsValidating] = useState(false);

  // 1. Load Single Scenario Curve
  useEffect(() => {
    async function loadSingleCurve() {
      if (!activeScenario) return;
      try {
        // Run a sweep from 1 to 100 meters
        const xVal = [];
        const incY = [];
        const refY = [];
        
        for (let d = 1; d <= 100; d += 2) {
          const res = await api.blast.calculateEnvironment({
            chargeWeight: activeScenario.charge_weight,
            distance: d,
            burstType: activeScenario.burst_type,
            explosiveId: activeScenario.explosive_id
          });
          xVal.push(d);
          incY.push(res.incident_pressure);
          refY.push(res.reflected_pressure);
        }
        setSingleSweepX(xVal);
        setSingleIncidentY(incY);
        setSingleReflectedY(refY);
      } catch (e) {
        console.error('Error generating single curve:', e);
      }
    }
    loadSingleCurve();
  }, [activeScenario]);

  // 2. Load Scenarios for Comparison selection
  useEffect(() => {
    async function fetchScenarios() {
      try {
        const list = await api.scenarios.list();
        setScenariosList(list);
        if (list.length > 0 && selectedScenarios.length === 0) {
          setSelectedScenarios([list[0].id!]);
        }
      } catch (e) {
        console.error(e);
      }
    }
    fetchScenarios();
  }, [activeTab]);

  // 3. Trigger Comparison calculation when selection changes
  useEffect(() => {
    async function fetchComparison() {
      if (selectedScenarios.length === 0) return;
      try {
        const curves = await api.research.compareScenarios(selectedScenarios);
        setComparisonCurves(curves);
      } catch (e) {
        console.error(e);
      }
    }
    fetchComparison();
  }, [selectedScenarios]);

  // 4. Trigger Parametric sweep
  const runParametricSweep = async () => {
    if (!activeScenario) return;
    try {
      const results = await api.research.parametricSweep({
        baseScenarioId: activeScenario.id!,
        variableName: sweepVar,
        minValue: minVal,
        maxValue: maxVal,
        stepValue: stepVal
      });
      setSweepResults(results);
    } catch (e) {
      console.error(e);
    }
  };

  // Derive source distributions from validation cases prop
  useEffect(() => {
    if (validationCases.length > 0) {
      const counts: Record<string, number> = {};
      validationCases.forEach((c) => {
        counts[c.validation_source] = (counts[c.validation_source] || 0) + 1;
      });
      const dist = Object.keys(counts)
        .map((k) => ({ source: k, cases: counts[k] }))
        .sort((a, b) => b.cases - a.cases);
      setSourceDist(dist);
    }
  }, [validationCases]);

  const loadValidationData = async () => {
    try {
      setIsValidating(true);
      await onReloadValidation();
    } catch (e) {
      console.error('Validation reload error:', e);
    } finally {
      setIsValidating(false);
    }
  };

  const handleExportValidation = () => {
    if (!validationCases.length) return;
    const headers = [
      'validation_source', 'validation_page', 'burst_type', 'ground_truth_class', 
      'charge_weight', 'distance', 'scaled_distance', 'reference_pressure', 
      'calculated_pressure', 'pressure_rel_error', 'reference_impulse', 
      'calculated_impulse', 'impulse_rel_error'
    ];
    const csvContent = [
      headers.join(','),
      ...validationCases.map(c => headers.map(h => {
        const val = (c as any)[h];
        return typeof val === 'string' && val.includes(',') ? `"${val}"` : (val ?? '');
      }).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'blastscope_validation_cases.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleScenarioSelection = (id: number) => {
    if (selectedScenarios.includes(id)) {
      setSelectedScenarios(selectedScenarios.filter(x => x !== id));
    } else {
      setSelectedScenarios([...selectedScenarios, id]);
    }
  };

  const toggleProfileSelection = (id: number) => {
    if (selectedProfiles.includes(id)) {
      setSelectedProfiles(selectedProfiles.filter(x => x !== id));
    } else {
      setSelectedProfiles([...selectedProfiles, id]);
    }
  };

  if (!activeScenario || !activeResults) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }} className="animate-fade-in">
        Please select or save a scenario to open the Research Workspace.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }} className="animate-fade-in">
      
      {/* Navigation tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        gap: '4px'
      }}>
        {[
          { id: 'analysis', label: 'Scenario Analysis', icon: TrendingUp },
          { id: 'comparison', label: 'Scenario Comparison', icon: Layers },
          { id: 'parametric', label: 'Parametric Study', icon: Sliders },
          { id: 'vulnerability', label: 'Material Vulnerability Map', icon: BarChart3 },
          { id: 'radar', label: 'Material Vulnerability Radar', icon: ShieldAlert },
          { id: 'validation', label: 'Model Validation & Calibration', icon: CheckSquare }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 18px',
                border: 'none',
                background: isActive ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                borderBottom: isActive ? '2px solid var(--primary)' : '2px solid transparent',
                color: isActive ? '#fff' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9rem',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      <div style={{ flex: 1, minHeight: '400px' }}>
        
        {/* Tab 1: Scenario Analysis */}
        {activeTab === 'analysis' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', height: '400px' }}>
            <div className="glass-panel" style={{ padding: '16px', height: '100%' }}>
              <BlastCurvePlot 
                x={singleSweepX} 
                incidentY={singleIncidentY} 
                reflectedY={singleReflectedY} 
                title={`Blast Curve: ${activeScenario.name}`}
              />
            </div>
            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff' }}>Plot Details</h3>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                This chart displays the decay of blast incident pressure (P_so) and reflected pressure (Pr) over distances ranging from 1 to 100 meters, using calculations modeled for a <strong style={{ color: '#fff' }}>{activeScenario.charge_weight} kg</strong> burst.
              </p>
              
              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)' }}>Calculation Parameters:</span>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.8rem' }}>
                  <div>Explosive: <strong style={{ color: '#fff' }}>{activeScenario.explosive_name || 'TNT'}</strong></div>
                  <div>Burst Type: <strong style={{ color: '#fff' }}>{activeScenario.burst_type}</strong></div>
                  <div>Model Used: <strong style={{ color: '#fff' }}>{activeResults.model_used}</strong></div>
                  <div>Version: <strong style={{ color: '#fff' }}>{activeResults.model_version}</strong></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Scenario Comparison */}
        {activeTab === 'comparison' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', height: '400px' }}>
            <div className="glass-panel" style={{ padding: '16px', height: '100%' }}>
              {comparisonCurves.length === 0 ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Select scenarios on the right to compare curves.
                </div>
              ) : (
                <ComparisonPlot 
                  scenariosCurves={comparisonCurves}
                  metric={comparisonMetric}
                  metricLabel={comparisonMetric === 'positive_impulse' ? 'Impulse (kPa-ms)' : 'Pressure (kPa)'}
                />
              )}
            </div>

            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff' }}>Compare Configurations</h3>
              
              <div className="form-group">
                <label className="form-label">Compare Metric</label>
                <select 
                  className="form-input" 
                  value={comparisonMetric}
                  onChange={(e) => setComparisonMetric(e.target.value as any)}
                >
                  <option value="incident_pressure">Incident Pressure (Pso)</option>
                  <option value="reflected_pressure">Reflected Pressure (Pr)</option>
                  <option value="positive_impulse">Positive Impulse (is)</option>
                </select>
              </div>

              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '10px' }}>
                <span className="form-label" style={{ marginBottom: '8px', display: 'block' }}>Select Scenarios to Plot:</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {scenariosList.map(sc => (
                    <label key={sc.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', cursor: 'pointer' }}>
                      <input 
                        type="checkbox"
                        checked={selectedScenarios.includes(sc.id!)}
                        onChange={() => toggleScenarioSelection(sc.id!)}
                        style={{ accentColor: 'var(--primary)' }}
                      />
                      <span style={{ color: selectedScenarios.includes(sc.id!) ? '#fff' : 'var(--text-muted)' }}>
                        {sc.name} ({sc.charge_weight}kg)
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Parametric Study */}
        {activeTab === 'parametric' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', height: '400px' }}>
            <div className="glass-panel" style={{ padding: '16px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {sweepResults.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  <AlertCircle size={24} />
                  Configure range variables on the right and click "Run Sweep".
                </div>
              ) : (
                <div style={{ width: '100%', height: '100%' }}>
                  <div style={{ width: '100%', height: '100%' }}>
                    <BlastCurvePlot 
                      x={sweepResults.map(pt => pt.sweep_variable)}
                      incidentY={sweepResults.map(pt => pt.incident_pressure)}
                      reflectedY={sweepResults.map(pt => pt.reflected_pressure)}
                      title={`Parametric Sweep: ${sweepVar === 'distance' ? 'Distance Standoff' : 'Charge Weight'} Sweep`}
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff' }}>Configure Parametric Sweep</h3>
              
              <div className="form-group">
                <label className="form-label">Sweep Variable</label>
                <select 
                  className="form-input" 
                  value={sweepVar}
                  onChange={(e) => setSweepVar(e.target.value as any)}
                >
                  <option value="distance">Distance / Standoff (m)</option>
                  <option value="chargeWeight">Charge Weight (kg)</option>
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div className="form-group">
                  <label className="form-label">Min Range</label>
                  <input type="number" className="form-input" value={minVal} onChange={(e) => setMinVal(Number(e.target.value))} />
                </div>
                <div className="form-group">
                  <label className="form-label">Max Range</label>
                  <input type="number" className="form-input" value={maxVal} onChange={(e) => setMaxVal(Number(e.target.value))} />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Step Size</label>
                <input type="number" className="form-input" value={stepVal} onChange={(e) => setStepVal(Number(e.target.value))} min="0.1" />
              </div>

              <button className="btn btn-primary" onClick={runParametricSweep}>
                Run Range Sweep
              </button>
            </div>
          </div>
        )}

        {/* Tab 4: Material Vulnerability Map */}
        {activeTab === 'vulnerability' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', height: '400px' }}>
            <div className="glass-panel" style={{ padding: '16px', height: '100%' }}>
              {selectedProfiles.length === 0 ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Select material profiles on the right to overlay capacity lines.
                </div>
              ) : (
                <ThresholdOverlayPlot 
                  distancePoints={singleSweepX}
                  pressurePoints={singleReflectedY}
                  activeProfiles={profiles.filter(p => selectedProfiles.includes(p.id))}
                  metricLabel="Reflected Pressure (Pr)"
                />
              )}
            </div>

            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff' }}>Overlay Threshold Limits</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                Select targets to render horizontal failure boundaries. Overlap points with the current blast curve indicate failure distance zones.
              </p>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '10px' }}>
                {profiles.map(p => (
                  <label key={p.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', cursor: 'pointer' }}>
                    <input 
                      type="checkbox"
                      checked={selectedProfiles.includes(p.id)}
                      onChange={() => toggleProfileSelection(p.id)}
                      style={{ accentColor: 'var(--primary)' }}
                    />
                    <span style={{ color: selectedProfiles.includes(p.id) ? '#fff' : 'var(--text-muted)' }}>
                      {p.profile_name} ({p.failure_pressure} kPa)
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 5: Material Vulnerability Radar */}
        {activeTab === 'radar' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', height: '400px' }}>
            <div className="glass-panel" style={{ padding: '16px', height: '100%' }}>
              <RadarPlot assessments={assessments} />
            </div>
            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff' }}>Radar Chart Analysis</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                This radar chart plots the normalized Damage Index (DI) for each material profile. Values are scaled from 0 (Safe) to 1 (Severe/Failure boundary, corresponding to DI &ge; 4.0).
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem', borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#10b981' }}></span>
                  <span>Safe Zone (DI &lt; 1.0)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#fbbf24' }}></span>
                  <span>Minor Damage Zone (1.0 &le; DI &lt; 2.0)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#f97316' }}></span>
                  <span>Moderate Damage Zone (2.0 &le; DI &lt; 4.0)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444' }}></span>
                  <span>Severe / Failure Zone (DI &ge; 4.0)</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 6: Model Validation & Calibration */}
        {activeTab === 'validation' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
            
            {/* Top row: Metrics and PI Plot */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', minHeight: '380px' }}>
              
              {/* Metrics panel */}
              <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ fontSize: '1rem', color: '#fff', margin: 0 }}>Model Accuracy Benchmark Dashboard</h3>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button 
                      className="btn btn-secondary" 
                      onClick={handleExportValidation}
                      style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                    >
                      Export Verification Dataset
                    </button>
                    <button 
                      className="btn btn-secondary" 
                      onClick={loadValidationData} 
                      disabled={isValidating}
                      style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                      <RefreshCw size={12} className={isValidating ? 'animate-spin' : ''} />
                      {isValidating ? 'Recalculating...' : 'Refresh Benchmark'}
                    </button>
                  </div>
                </div>
                
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                  Model validation compares the physics engine calculations (Swisdak 1994) against independent reference cases from TM5-1300, UFC 3-340-02, and NSWC field tests.
                </p>

                {/* Side-by-side tables */}
                <div style={{ display: 'flex', gap: '20px', flex: 1, minHeight: 0 }}>
                  
                  {/* Dashboard table */}
                  <div style={{ flex: 2, overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.74rem', textAlign: 'left' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                          <th style={{ padding: '6px' }}>Ground Truth Class</th>
                          <th style={{ padding: '6px' }}>N</th>
                          <th style={{ padding: '6px' }}>Mean P Err</th>
                          <th style={{ padding: '6px' }}>RMSE P Err</th>
                          <th style={{ padding: '6px' }}>Max P Err</th>
                          <th style={{ padding: '6px' }}>p95 P Err</th>
                          <th style={{ padding: '6px' }}>Mean I Err</th>
                          <th style={{ padding: '6px' }}>RMSE I Err</th>
                          <th style={{ padding: '6px' }}>Max I Err</th>
                          <th style={{ padding: '6px' }}>p95 I Err</th>
                        </tr>
                      </thead>
                      <tbody>
                        {validationSummary.map((sum, index) => {
                          const isTotal = sum.ground_truth_class === 'OVERALL TOTAL';
                          return (
                            <tr 
                              key={index} 
                              style={{ 
                                borderBottom: '1px solid rgba(255,255,255,0.05)',
                                fontWeight: isTotal ? 'bold' : 'normal',
                                background: isTotal ? 'rgba(59,130,246,0.08)' : 'transparent',
                                color: isTotal ? '#fff' : 'var(--text-main)'
                              }}
                            >
                              <td style={{ padding: '6px', fontWeight: 'bold' }}>{sum.ground_truth_class}</td>
                              <td style={{ padding: '6px' }}>{sum.total_cases}</td>
                              <td style={{ padding: '6px', color: sum.avg_pressure_error > 5 ? 'var(--status-minor)' : 'var(--status-safe)' }}>
                                {sum.avg_pressure_error.toFixed(1)}%
                              </td>
                              <td style={{ padding: '6px' }}>
                                {sum.rmse_pressure_error ? `${sum.rmse_pressure_error.toFixed(1)}%` : '-'}
                              </td>
                              <td style={{ padding: '6px' }}>{sum.max_pressure_error.toFixed(1)}%</td>
                              <td style={{ padding: '6px' }}>
                                {sum.p95_pressure_error ? `${sum.p95_pressure_error.toFixed(1)}%` : '-'}
                              </td>
                              <td style={{ padding: '6px', color: sum.avg_impulse_error > 5 ? 'var(--status-minor)' : 'var(--status-safe)' }}>
                                {sum.avg_impulse_error.toFixed(1)}%
                              </td>
                              <td style={{ padding: '6px' }}>
                                {sum.rmse_impulse_error ? `${sum.rmse_impulse_error.toFixed(1)}%` : '-'}
                              </td>
                              <td style={{ padding: '6px' }}>{sum.max_impulse_error.toFixed(1)}%</td>
                              <td style={{ padding: '6px' }}>
                                {sum.p95_impulse_error ? `${sum.p95_impulse_error.toFixed(1)}%` : '-'}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  {/* Source Distribution table */}
                  <div style={{ flex: 1, overflowY: 'auto', borderLeft: '1px solid var(--border-color)', paddingLeft: '20px' }}>
                    <h4 style={{ fontSize: '0.8rem', color: '#fff', marginTop: 0, marginBottom: '8px' }}>
                      Validation Source Distribution
                    </h4>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.74rem', textAlign: 'left' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                          <th style={{ padding: '6px' }}>Source Reference</th>
                          <th style={{ padding: '6px', textAlign: 'right' }}>Cases</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sourceDist.map((item, index) => (
                          <tr key={index} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                            <td style={{ padding: '6px' }}>{item.source}</td>
                            <td style={{ padding: '6px', textAlign: 'right', fontWeight: 'bold' }}>{item.cases}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.02)', padding: '8px', borderLeft: '2px solid var(--primary)' }}>
                  <strong>Target SLA:</strong> Average error for analytical and digitized references must remain below <strong>&lt; 5%</strong> to ensure military publication alignment.
                </div>
              </div>

              {/* PI Plot panel */}
              <div className="glass-panel" style={{ padding: '16px' }}>
                <PIPlot activeResults={activeResults} profiles={profiles} />
              </div>
            </div>

            {/* Bottom Row: Detailed Cases Table */}
            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <h3 style={{ fontSize: '0.95rem', color: '#fff', margin: 0 }}>Detailed Verification Cases (N = 30)</h3>
              <div style={{ maxHeight: '250px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '6px' }}>Source Reference</th>
                      <th style={{ padding: '6px' }}>Burst</th>
                      <th style={{ padding: '6px' }}>Class</th>
                      <th style={{ padding: '6px' }}>Scaled Dist (Z)</th>
                      <th style={{ padding: '6px' }}>Ref Pressure</th>
                      <th style={{ padding: '6px' }}>Calc Pressure</th>
                      <th style={{ padding: '6px' }}>P Error</th>
                      <th style={{ padding: '6px' }}>Ref Impulse</th>
                      <th style={{ padding: '6px' }}>Calc Impulse</th>
                      <th style={{ padding: '6px' }}>I Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {validationCases.map((c) => (
                      <tr key={c.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                        <td style={{ padding: '6px' }}>{c.validation_source} ({c.validation_page})</td>
                        <td style={{ padding: '6px' }}>{c.burst_type}</td>
                        <td style={{ padding: '6px' }}>{c.ground_truth_class}</td>
                        <td style={{ padding: '6px' }}>{c.scaled_distance.toFixed(3)}</td>
                        <td style={{ padding: '6px' }}>{c.reference_pressure.toFixed(1)} kPa</td>
                        <td style={{ padding: '6px' }}>{c.calculated_pressure ? `${c.calculated_pressure.toFixed(1)} kPa` : '-'}</td>
                        <td style={{ padding: '6px', color: (c.pressure_rel_error ?? 0) > 5 ? 'var(--status-minor)' : 'var(--status-safe)' }}>
                          {c.pressure_rel_error ? `${c.pressure_rel_error.toFixed(2)}%` : '-'}
                        </td>
                        <td style={{ padding: '6px' }}>{c.reference_impulse.toFixed(1)} kPa-ms</td>
                        <td style={{ padding: '6px' }}>{c.calculated_impulse ? `${c.calculated_impulse.toFixed(1)} kPa-ms` : '-'}</td>
                        <td style={{ padding: '6px', color: (c.impulse_rel_error ?? 0) > 5 ? 'var(--status-minor)' : 'var(--status-safe)' }}>
                          {c.impulse_rel_error ? `${c.impulse_rel_error.toFixed(2)}%` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

      </div>

      {/* Export Menu Footer Panel */}
      <ExportMenu />
    </div>
  );
}
