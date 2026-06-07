import { useState, useCallback } from 'react';
import { Explosive, MaterialProfile, SweepPoint, GridResult, StudyType, STUDY_LIMITS } from '../types';
import { api } from '../services/api';
import { Play, AlertTriangle, Zap, BarChart2, Layers } from 'lucide-react';
import SweepPlot from '../components/plots/SweepPlot';
import RiskContourPanel from '../components/RiskContourPanel';

interface ParametricStudyProps {
  explosives: Explosive[];
  profiles: MaterialProfile[];
}

const STUDY_ICONS: Record<StudyType, React.ReactNode> = {
  distance: <BarChart2 size={14} />,
  charge: <Zap size={14} />,
  explosive: <Layers size={14} />,
  grid: <BarChart2 size={14} />,
};

const STUDY_LABELS: Record<StudyType, string> = {
  distance: 'Distance Sweep',
  charge: 'Charge Sweep',
  explosive: 'Explosive Comparison',
  grid: 'Grid Study',
};

function parseRange(input: string): number[] {
  // "10,25,50,100" or "10:100:10" (start:end:step)
  if (input.includes(':')) {
    const [startStr, endStr, stepStr] = input.split(':').map(s => parseFloat(s.trim()));
    const arr: number[] = [];
    for (let v = startStr; v <= endStr + 1e-9; v += stepStr) {
      arr.push(Math.round(v * 1000) / 1000);
    }
    return arr;
  }
  return input.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n) && n > 0);
}

function pointCount(studyType: StudyType, distancesM: number[], chargesKg: number[], explosiveIds: number[], profileIds: number[]): number {
  if (studyType === 'distance') return distancesM.length * profileIds.length;
  if (studyType === 'charge') return chargesKg.length * profileIds.length;
  if (studyType === 'explosive') return explosiveIds.length * distancesM.length * profileIds.length;
  if (studyType === 'grid') return chargesKg.length * distancesM.length * profileIds.length;
  return 0;
}

export default function ParametricStudy({ explosives, profiles }: ParametricStudyProps) {
  const [studyType, setStudyType] = useState<StudyType>('distance');
  const [explosiveId, setExplosiveId] = useState<number>(explosives[0]?.id ?? 1);
  const [explosiveIds, setExplosiveIds] = useState<number[]>([explosives[0]?.id ?? 1]);
  const [chargeKg, setChargeKg] = useState<string>('100');
  const [chargesKgStr, setChargesKgStr] = useState<string>('10:200:10');
  const [distanceMStr, setDistanceMStr] = useState<string>('25');
  const [distancesMStr, setDistancesMStr] = useState<string>('5:100:5');
  const [profileIds, setProfileIds] = useState<number[]>(profiles.slice(0, 3).map(p => p.id));
  const [burstType, setBurstType] = useState<'Surface' | 'Air' | 'Free Air'>('Surface');

  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sweepPoints, setSweepPoints] = useState<SweepPoint[]>([]);
  const [gridResult, setGridResult] = useState<GridResult | null>(null);
  const [confirming, setConfirming] = useState(false);

  const chargesKg = parseRange(chargesKgStr);
  const distancesM = parseRange(distancesMStr);
  const nPoints = pointCount(studyType, distancesM, chargesKg, explosiveIds, profileIds);

  const limitStatus = nPoints <= STUDY_LIMITS.IMMEDIATE ? 'ok'
    : nPoints <= STUDY_LIMITS.SOFT ? 'warn'
    : nPoints <= STUDY_LIMITS.HARD ? 'confirm'
    : 'blocked';

  const toggleProfile = (id: number) => {
    setProfileIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };
  const toggleExplosive = (id: number) => {
    setExplosiveIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const runStudy = useCallback(async () => {
    if (limitStatus === 'blocked') return;
    if (limitStatus === 'confirm' && !confirming) { setConfirming(true); return; }
    setConfirming(false);
    setRunning(true);
    setError(null);
    try {
      if (studyType === 'distance') {
        const pts = await api.studies.distanceSweep({
          explosive_id: explosiveId,
          charge_kg: parseFloat(chargeKg),
          distances_m: distancesM,
          profile_ids: profileIds,
          burst_type: burstType,
        });
        setSweepPoints(pts);
        setGridResult(null);
      } else if (studyType === 'charge') {
        const pts = await api.studies.chargeSweep({
          explosive_id: explosiveId,
          charges_kg: chargesKg,
          distance_m: parseFloat(distanceMStr),
          profile_ids: profileIds,
          burst_type: burstType,
        });
        setSweepPoints(pts);
        setGridResult(null);
      } else if (studyType === 'explosive') {
        const pts = await api.studies.explosiveComparison({
          explosive_ids: explosiveIds,
          charge_kg: parseFloat(chargeKg),
          distances_m: distancesM,
          profile_ids: profileIds,
          burst_type: burstType,
        });
        setSweepPoints(pts);
        setGridResult(null);
      } else if (studyType === 'grid') {
        const result = await api.studies.runGrid({
          explosive_id: explosiveId,
          charges_kg: chargesKg,
          distances_m: distancesM,
          profile_ids: profileIds,
          burst_type: burstType,
        });
        setGridResult(result);
        setSweepPoints(result.points);
      }
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setRunning(false);
    }
  }, [studyType, explosiveId, explosiveIds, chargeKg, chargesKg, distanceMStr, distancesM, profileIds, burstType, limitStatus, confirming]);

  const handleExport = async () => {
    if (!sweepPoints.length) return;
    try {
      let savePath: string | undefined;
      if (window.api) {
        // Electron: open save dialog
        savePath = await (window as any).electronAPI?.showSaveDialog?.({
          defaultPath: `blastscope_${sweepPoints[0]?.study_id}.csv`,
          filters: [{ name: 'CSV', extensions: ['csv'] }],
        });
      }
      await api.studies.exportCSV(sweepPoints, savePath);
    } catch (e: any) {
      setError(e?.message ?? 'Export failed');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }} className="animate-fade-in">
      {/* Study Type Selector */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <h2 style={{ fontSize: '1.1rem', color: '#fff', marginBottom: '16px' }}>Parametric Study Configuration</h2>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {(['distance', 'charge', 'explosive', 'grid'] as StudyType[]).map(st => (
            <button
              key={st}
              onClick={() => setStudyType(st)}
              style={{
                padding: '8px 14px', borderRadius: '6px', border: '1px solid',
                borderColor: studyType === st ? 'var(--accent)' : 'var(--border-color)',
                background: studyType === st ? 'rgba(99,102,241,0.15)' : 'transparent',
                color: studyType === st ? 'var(--accent)' : 'var(--text-muted)',
                cursor: 'pointer', fontSize: '0.82rem', fontWeight: 600,
                display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.2s',
              }}
            >
              {STUDY_ICONS[st]} {STUDY_LABELS[st]}
            </button>
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* Left column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* Explosive selector */}
            {studyType === 'explosive' ? (
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                  Explosives (select multiple)
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {explosives.map(e => (
                    <button
                      key={e.id}
                      onClick={() => toggleExplosive(e.id)}
                      style={{
                        padding: '4px 10px', borderRadius: '4px', border: '1px solid',
                        borderColor: explosiveIds.includes(e.id) ? '#f97316' : 'var(--border-color)',
                        background: explosiveIds.includes(e.id) ? 'rgba(249,115,22,0.15)' : 'transparent',
                        color: explosiveIds.includes(e.id) ? '#f97316' : 'var(--text-muted)',
                        cursor: 'pointer', fontSize: '0.78rem', transition: 'all 0.2s',
                      }}
                    >
                      {e.name}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Explosive</label>
                <select
                  value={explosiveId}
                  onChange={e => setExplosiveId(Number(e.target.value))}
                  className="form-select"
                  style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.82rem' }}
                >
                  {explosives.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
                </select>
              </div>
            )}

            {/* Charge input */}
            {(studyType === 'distance' || studyType === 'explosive') ? (
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Charge Weight (kg)</label>
                <input
                  type="number" value={chargeKg} onChange={e => setChargeKg(e.target.value)} min="0.1"
                  style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.82rem', boxSizing: 'border-box' }}
                />
              </div>
            ) : (
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                  Charges (kg) — comma list or <code style={{ color: '#a5b4fc', fontSize: '0.75rem' }}>start:end:step</code>
                </label>
                <input
                  type="text" value={chargesKgStr} onChange={e => setChargesKgStr(e.target.value)} placeholder="10:200:10"
                  style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.82rem', boxSizing: 'border-box' }}
                />
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '4px 0 0' }}>{chargesKg.length} values · {chargesKg[0]?.toFixed(0)}–{chargesKg[chargesKg.length - 1]?.toFixed(0)} kg</p>
              </div>
            )}

            {/* Distance input */}
            {(studyType === 'charge') ? (
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Fixed Distance (m)</label>
                <input
                  type="number" value={distanceMStr} onChange={e => setDistanceMStr(e.target.value)} min="1"
                  style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.82rem', boxSizing: 'border-box' }}
                />
              </div>
            ) : (
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                  Distances (m) — comma list or <code style={{ color: '#a5b4fc', fontSize: '0.75rem' }}>start:end:step</code>
                </label>
                <input
                  type="text" value={distancesMStr} onChange={e => setDistancesMStr(e.target.value)} placeholder="5:100:5"
                  style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.82rem', boxSizing: 'border-box' }}
                />
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '4px 0 0' }}>{distancesM.length} values · {distancesM[0]?.toFixed(0)}–{distancesM[distancesM.length - 1]?.toFixed(0)} m</p>
              </div>
            )}

            {/* Burst type */}
            <div>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Burst Type</label>
              <select
                value={burstType}
                onChange={e => setBurstType(e.target.value as any)}
                style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.82rem' }}
              >
                <option value="Surface">Surface Burst</option>
                <option value="Air">Air Burst</option>
                <option value="Free Air">Free Air Burst</option>
              </select>
            </div>
          </div>

          {/* Right column — material profile selection */}
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
              Material Profiles ({profileIds.length} selected)
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '240px', overflowY: 'auto' }}>
              {profiles.map(p => (
                <button
                  key={p.id}
                  onClick={() => toggleProfile(p.id)}
                  style={{
                    padding: '8px 12px', borderRadius: '6px', border: '1px solid',
                    borderColor: profileIds.includes(p.id) ? 'var(--accent)' : 'var(--border-color)',
                    background: profileIds.includes(p.id) ? 'rgba(99,102,241,0.12)' : 'transparent',
                    color: profileIds.includes(p.id) ? '#e2e8f0' : 'var(--text-muted)',
                    cursor: 'pointer', textAlign: 'left', fontSize: '0.78rem', transition: 'all 0.2s',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  }}
                >
                  <span>{p.profile_name}</span>
                  <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>{p.family}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Point count + limit warnings */}
        <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Estimated points: <strong style={{ color: limitStatus === 'blocked' ? '#ef4444' : limitStatus === 'confirm' ? '#f97316' : limitStatus === 'warn' ? '#fbbf24' : '#10b981' }}>{nPoints.toLocaleString()}</strong>
          </span>

          {limitStatus === 'warn' && (
            <span style={{ fontSize: '0.72rem', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={12} /> Large study — may take a few seconds
            </span>
          )}
          {limitStatus === 'confirm' && !confirming && (
            <span style={{ fontSize: '0.72rem', color: '#f97316', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={12} /> Very large study (&gt;5,000 points). Click Run again to confirm.
            </span>
          )}
          {limitStatus === 'blocked' && (
            <span style={{ fontSize: '0.72rem', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={12} /> Exceeds 10,000 point hard limit. Reduce range or profiles.
            </span>
          )}

          <button
            onClick={runStudy}
            disabled={running || limitStatus === 'blocked' || profileIds.length === 0}
            style={{
              marginLeft: 'auto', padding: '9px 22px', borderRadius: '7px',
              background: confirming ? 'linear-gradient(135deg, #f97316, #ef4444)' : 'linear-gradient(135deg, var(--accent), #7c3aed)',
              color: '#fff', border: 'none', cursor: running || limitStatus === 'blocked' ? 'not-allowed' : 'pointer',
              fontSize: '0.82rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px',
              opacity: running || limitStatus === 'blocked' ? 0.5 : 1, transition: 'all 0.2s',
            }}
          >
            <Play size={14} />
            {running ? 'Running…' : confirming ? 'Confirm Large Study' : 'Run Study'}
          </button>

          {sweepPoints.length > 0 && (
            <button
              onClick={handleExport}
              style={{
                padding: '9px 16px', borderRadius: '7px', border: '1px solid var(--border-color)',
                background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer',
                fontSize: '0.78rem', fontWeight: 600, transition: 'all 0.2s',
              }}
            >
              Export CSV
            </button>
          )}
        </div>

        {error && (
          <div style={{ marginTop: '12px', padding: '10px 14px', borderRadius: '6px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', fontSize: '0.78rem' }}>
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {sweepPoints.length > 0 && (
        <>
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '0.95rem', color: '#fff', margin: 0 }}>
                {STUDY_LABELS[studyType]} Results
              </h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {sweepPoints.length.toLocaleString()} data points · study_id: <code style={{ color: '#a5b4fc', fontSize: '0.7rem' }}>{sweepPoints[0]?.study_id}</code>
              </span>
            </div>
            <SweepPlot
              points={sweepPoints}
              xAxis={studyType === 'charge' ? 'charge_kg' : 'distance_m'}
              yAxis="peak_pressure_kPa"
              groupBy={studyType === 'explosive' ? 'explosive_name' : 'profile_name'}
            />
          </div>

          <SweepPlot
            points={sweepPoints}
            xAxis={studyType === 'charge' ? 'charge_kg' : 'distance_m'}
            yAxis="severity_score"
            groupBy={studyType === 'explosive' ? 'explosive_name' : 'profile_name'}
            title="Severity Score vs Distance"
          />

          {gridResult && (
            <RiskContourPanel
              rankings={gridResult.summary}
              chargeKg={gridResult.charges_kg[gridResult.charges_kg.length - 1]}
              explosiveName={gridResult.explosive_name}
            />
          )}
        </>
      )}
    </div>
  );
}
