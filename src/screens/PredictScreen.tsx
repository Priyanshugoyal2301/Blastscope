import React, { useState } from 'react';
import { api } from '../services/api';
import { Scale, Compass, MapPin, Gauge, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function PredictScreen() {
  const [burstType, setBurstType] = useState<'Surface' | 'Free Air'>('Surface');
  const [unitSystem, setUnitSystem] = useState<'Metric' | 'Imperial'>('Metric');
  
  // Inputs
  const [pso, setPso] = useState<string>('150.0');
  const [pr, setPr] = useState<string>('450.0');
  const [is, setIs] = useState<string>('200.0');
  const [ir, setIr] = useState<string>('700.0');
  const [ta, setTa] = useState<string>('2.5');
  const [to, setTo] = useState<string>('4.0');

  // Outputs
  const [results, setResults] = useState<{
    weight: number;
    scaledDistance: number;
    distance: number;
    confidence: number;
    modelUsed: string;
    ood?: boolean;
  } | null>(null);

  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Conversion Helpers
  // 1 psi = 6.894757 kPa
  // 1 m = 3.28084 ft
  // 1 kg = 2.20462 lb
  // 1 m/kg^(1/3) = 2.52079 ft/lb^(1/3)
  
  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);

    // Convert inputs to metric for the backend
    const factorPressure = unitSystem === 'Imperial' ? 6.894757 : 1.0;
    
    const pso_kPa = parseFloat(pso) > 0 ? parseFloat(pso) * factorPressure : 0.0;
    const pr_kPa = parseFloat(pr) > 0 ? parseFloat(pr) * factorPressure : 0.0;
    const is_kPa_ms = parseFloat(is) > 0 ? parseFloat(is) * factorPressure : 0.0;
    const ir_kPa_ms = parseFloat(ir) > 0 ? parseFloat(ir) * factorPressure : 0.0;
    const ta_ms = parseFloat(ta) > 0 ? parseFloat(ta) : 0.0;
    const to_ms = parseFloat(to) > 0 ? parseFloat(to) : 0.0;

    if (pso_kPa === 0 && pr_kPa === 0 && is_kPa_ms === 0 && ir_kPa_ms === 0 && ta_ms === 0 && to_ms === 0) {
      setErrorMsg("Please enter at least one non-zero blast wave parameter to estimate.");
      setLoading(false);
      return;
    }

    try {
      const res = await api.inverse.predict({
        burstType,
        incident_pressure: pso_kPa,
        reflected_pressure: pr_kPa,
        positive_impulse: is_kPa_ms,
        reflected_impulse: ir_kPa_ms,
        arrival_time: ta_ms,
        positive_duration: to_ms
      });

      setResults({
        weight: res.weight,
        scaledDistance: res.scaled_distance,
        distance: res.distance,
        confidence: res.confidence,
        modelUsed: res.model_used,
        ood: (res as any).ood
      });
    } catch (err: any) {
      setErrorMsg(err.message || "Model inference failed. Ensure model file is generated.");
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'var(--status-safe)';
    if (score >= 70) return 'var(--status-minor)';
    return 'var(--status-severe)';
  };

  // Convert outputs for display based on selected unit system
  const displayWeight = results 
    ? (unitSystem === 'Imperial' ? results.weight * 2.20462 : results.weight)
    : 0;
  
  const displayScaledDist = results 
    ? (unitSystem === 'Imperial' ? results.scaledDistance * 2.52079 : results.scaledDistance)
    : 0;

  const displayDistance = results 
    ? (unitSystem === 'Imperial' ? results.distance / 0.3048 : results.distance)
    : 0;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', height: '100%' }} className="animate-fade-in">
      {/* Inputs Form Panel */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>Sensor Readings Input</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Enter measured blast parameters to characterize threat</span>
        </div>

        <form onSubmit={handlePredict} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Burst Type</label>
              <select 
                className="form-input" 
                value={burstType} 
                onChange={(e) => setBurstType(e.target.value as any)}
              >
                <option value="Surface">Surface Burst</option>
                <option value="Free Air">Free Air Burst</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Unit System</label>
              <select 
                className="form-input" 
                value={unitSystem} 
                onChange={(e) => setUnitSystem(e.target.value as any)}
              >
                <option value="Metric">Metric (kPa, kPa-ms, ms)</option>
                <option value="Imperial">Imperial (psi, psi-ms, ms)</option>
              </select>
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-color)', margin: '4px 0' }}></div>

          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>Measured Pressures</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Incident Overpressure Pso ({unitSystem === 'Imperial' ? 'psi' : 'kPa'})</label>
              <input 
                type="number" 
                className="form-input" 
                value={pso} 
                onChange={(e) => setPso(e.target.value)} 
                min="0"
                step="any"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Reflected Pressure Pr ({unitSystem === 'Imperial' ? 'psi' : 'kPa'})</label>
              <input 
                type="number" 
                className="form-input" 
                value={pr} 
                onChange={(e) => setPr(e.target.value)} 
                min="0"
                step="any"
              />
            </div>
          </div>

          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>Measured Impulses</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Incident Impulse Is ({unitSystem === 'Imperial' ? 'psi-ms' : 'kPa-ms'})</label>
              <input 
                type="number" 
                className="form-input" 
                value={is} 
                onChange={(e) => setIs(e.target.value)} 
                min="0"
                step="any"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Reflected Impulse Ir ({unitSystem === 'Imperial' ? 'psi-ms' : 'kPa-ms'})</label>
              <input 
                type="number" 
                className="form-input" 
                value={ir} 
                onChange={(e) => setIr(e.target.value)} 
                min="0"
                step="any"
              />
            </div>
          </div>

          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>Timing Parameters</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Arrival Time Ta (ms)</label>
              <input 
                type="number" 
                className="form-input" 
                value={ta} 
                onChange={(e) => setTa(e.target.value)} 
                min="0"
                step="any"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Positive Duration To (ms)</label>
              <input 
                type="number" 
                className="form-input" 
                value={to} 
                onChange={(e) => setTo(e.target.value)} 
                min="0"
                step="any"
              />
            </div>
          </div>

          {errorMsg && (
            <div style={{ display: 'flex', gap: '8px', background: 'rgba(239, 68, 68, 0.12)', color: 'var(--status-failure)', padding: '12px', borderRadius: '4px', fontSize: '0.82rem', alignItems: 'center', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <AlertTriangle size={16} />
              {errorMsg}
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '12px', height: '42px', fontSize: '0.95rem' }}
            disabled={loading}
          >
            {loading ? "Reconstructing Blast parameters..." : "Characterize Threat (Inverse Solver)"}
          </button>
        </form>
      </div>

      {/* Outputs / Results Panel */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>Estimated Threat Parameters</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Inverse reconstruction results from Physics Reference Dataset ML model</span>
        </div>

        {!results ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', padding: '40px', gap: '12px' }}>
            <Compass size={48} style={{ color: 'var(--border-color)', strokeWidth: 1.5 }} />
            <div>
              Enter sensor values and click <strong>Characterize Threat</strong> to reconstruct charge size and standoff distance.
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', flex: 1 }}>
            {results.ood && (
              <div style={{
                display: 'flex',
                gap: '12px',
                background: 'rgba(217, 119, 6, 0.1)',
                color: '#D97706',
                padding: '16px',
                borderRadius: '6px',
                border: '1px solid rgba(217, 119, 6, 0.25)',
                fontSize: '0.85rem',
                lineHeight: '1.4',
                alignItems: 'flex-start'
              }}>
                <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong style={{ display: 'block', marginBottom: '4px', fontSize: '0.9rem' }}>⚠️ OUT OF TRAINING DOMAIN / LOW CONFIDENCE</strong>
                  The input sensor parameters fall outside the validated physical training envelope of the machine learning model. Tree-based predictions under extrapolation boundaries are subject to significant error.
                </div>
              </div>
            )}
            
            {/* Top Cards for main targets */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              
              {/* Charge Weight Card */}
              <div style={{ background: 'rgba(37, 99, 235, 0.02)', border: '1px solid var(--border-color)', borderRadius: '3px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ background: 'rgba(37, 99, 235, 0.08)', color: 'var(--primary)', padding: '12px', borderRadius: '50%' }}>
                  <Scale size={24} />
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Charge Weight (W)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', margin: '4px 0' }}>
                    {displayWeight.toFixed(2)} <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{unitSystem === 'Imperial' ? 'lb TNT' : 'kg TNT'}</span>
                  </div>
                </div>
              </div>

              {/* Scaled Distance Card */}
              <div style={{ background: 'rgba(37, 99, 235, 0.02)', border: '1px solid var(--border-color)', borderRadius: '3px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ background: 'rgba(37, 99, 235, 0.08)', color: 'var(--primary)', padding: '12px', borderRadius: '50%' }}>
                  <Compass size={24} />
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Scaled Distance (Z)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', margin: '4px 0' }}>
                    {displayScaledDist.toFixed(3)} <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{unitSystem === 'Imperial' ? 'ft/lb¹/³' : 'm/kg¹/³'}</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Derived Physical Distance */}
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)', borderRadius: '3px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ background: 'rgba(75, 85, 99, 0.08)', color: 'var(--accent)', padding: '12px', borderRadius: '50%' }}>
                <MapPin size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Physical Distance (R)</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', margin: '4px 0' }}>
                  {displayDistance.toFixed(2)} <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{unitSystem === 'Imperial' ? 'feet' : 'meters'}</span>
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Derived using physics relationship: R = Z × W^(1/3)
                </span>
              </div>
            </div>

            {/* Confidence Score Bar */}
            <div style={{ border: '1px solid var(--border-color)', borderRadius: '3px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  <Gauge size={16} />
                  Physics Consistency Score
                </span>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, color: getConfidenceColor(results.confidence) }}>
                  {results.confidence.toFixed(1)}%
                </span>
              </div>

              {/* Progress bar container */}
              <div style={{ height: '8px', background: 'var(--bg-main)', borderRadius: '4px', overflow: 'hidden' }}>
                <div 
                  style={{ 
                    height: '100%', 
                    width: `${results.confidence}%`, 
                    backgroundColor: getConfidenceColor(results.confidence),
                    transition: 'width 0.5s ease-out'
                  }}
                ></div>
              </div>

              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                Calculated by passing the predicted W and Z back into the validated forward physics solver and calculating the error discrepancy against your input values. A higher score represents perfect alignment with Kingery-Bulmash/Swisdak governing equations.
              </span>
            </div>

            {/* Model Rationale Info */}
            <div style={{ marginTop: 'auto', display: 'flex', gap: '10px', background: 'rgba(37, 99, 235, 0.04)', padding: '12px', borderRadius: '4px', border: '1px solid rgba(37, 99, 235, 0.1)', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              <ShieldCheck size={20} style={{ color: 'var(--primary)', flexShrink: 0 }} />
              <div>
                <strong>Reconstruction engine</strong>: Powered by <strong>{results.modelUsed}</strong>. Trained on 100,000 samples from the validated offline-first BlastScope forward solver. Non-unique features like Dynamic Pressure (Q), shock velocity, and particle velocity have been mathematically pruned to improve numerical stability.
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
