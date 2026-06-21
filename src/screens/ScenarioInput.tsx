import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Explosive, Scenario, ResearchNote } from '../types';
import { Save, Plus, AlertCircle, ClipboardList } from 'lucide-react';

interface ScenarioInputProps {
  explosives: Explosive[];
  activeScenario: Scenario | null;
  refreshScenarios: () => Promise<void>;
  onSelectScenario: (sc: Scenario) => void;
}

export default function ScenarioInput({
  explosives,
  activeScenario,
  refreshScenarios,
  onSelectScenario
}: ScenarioInputProps) {
  const [name, setName] = useState('');
  const [explosiveId, setExplosiveId] = useState<number>(1);
  const [chargeWeight, setChargeWeight] = useState<number>(100);
  const [distance, setDistance] = useState<number>(20);
  const [burstType, setBurstType] = useState<'Free Air' | 'Air' | 'Surface'>('Surface');
  const [unitSystem, setUnitSystem] = useState<'Metric' | 'Imperial'>('Metric');
  
  const [notesList, setNotesList] = useState<ResearchNote[]>([]);
  const [newNote, setNewNote] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Load properties from active scenario if it changes
  useEffect(() => {
    if (activeScenario) {
      setName(activeScenario.name);
      setExplosiveId(activeScenario.explosive_id);
      setChargeWeight(activeScenario.charge_weight);
      setDistance(activeScenario.distance);
      setBurstType(activeScenario.burst_type);
      setUnitSystem(activeScenario.unit_system);
      loadNotes(activeScenario.id!);
    } else {
      setName('');
      setNewNote('');
      setNotesList([]);
    }
  }, [activeScenario]);

  async function loadNotes(scenarioId: number) {
    try {
      const list = await api.scenarios.listNotes(scenarioId);
      setNotesList(list);
    } catch (e) {
      console.error('Error loading notes:', e);
    }
  }

  const handleSaveScenario = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!name.trim()) {
      setErrorMsg("Scenario Name is required");
      return;
    }

    try {
      const saveRes = await api.scenarios.save({
        id: activeScenario?.id,
        name,
        explosiveId,
        chargeWeight,
        distance,
        burstType,
        unitSystem
      });

      setSuccessMsg("Scenario saved and cached calculations computed successfully.");
      await refreshScenarios();
      
      // Select the saved scenario
      const updatedList = await api.scenarios.list();
      const match = updatedList.find(s => s.id === saveRes.scenarioId);
      if (match) {
        onSelectScenario(match);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "An error occurred while saving.");
    }
  };

  const handleCreateNew = () => {
    onSelectScenario(null as any); // Clear active scenario selection
    setName(`Scenario ${new Date().toLocaleTimeString()}`);
    setExplosiveId(explosives.length > 0 ? explosives[0].id : 1);
    setChargeWeight(100);
    setDistance(20);
    setBurstType('Surface');
    setUnitSystem('Metric');
    setNotesList([]);
    setNewNote('');
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeScenario || !newNote.trim()) return;

    try {
      await api.scenarios.saveNote(activeScenario.id!, newNote);
      setNewNote('');
      loadNotes(activeScenario.id!);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', height: '100%' }} className="animate-fade-in">
      {/* Form Card */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>Configure Scenario</h2>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Define physical environment boundaries</span>
          </div>

          <button className="btn btn-secondary" onClick={handleCreateNew} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
            <Plus size={14} />
            New
          </button>
        </div>

        <form onSubmit={handleSaveScenario} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div className="form-group">
            <label className="form-label">Scenario Name</label>
            <input 
              type="text" 
              className="form-input" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              placeholder="e.g. Concrete Slab Test A"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Explosive Type</label>
              <select 
                className="form-input" 
                value={explosiveId} 
                onChange={(e) => setExplosiveId(Number(e.target.value))}
              >
                {explosives.map(e => (
                  <option key={e.id} value={e.id}>{e.name} (P-eq: {e.pressure_equivalency}, I-eq: {e.impulse_equivalency})</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Charge Weight (kg)</label>
              <input 
                type="number" 
                className="form-input" 
                value={chargeWeight} 
                onChange={(e) => setChargeWeight(Number(e.target.value))} 
                min="0.1" 
                step="any"
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Distance (m)</label>
              <input 
                type="number" 
                className="form-input" 
                value={distance} 
                onChange={(e) => setDistance(Number(e.target.value))} 
                min="0.1" 
                step="any"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Burst Type</label>
              <select 
                className="form-input" 
                value={burstType} 
                onChange={(e) => setBurstType(e.target.value as any)}
              >
                <option value="Free Air">Free Air Burst</option>
                <option value="Air">Air Burst</option>
                <option value="Surface">Surface Burst</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Units System</label>
            <div style={{ display: 'flex', gap: '12px' }}>
              <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.88rem' }}>
                <input 
                  type="radio" 
                  name="unit_system" 
                  checked={unitSystem === 'Metric'} 
                  onChange={() => setUnitSystem('Metric')}
                  style={{ accentColor: 'var(--primary)' }}
                />
                Metric (kg, m, kPa)
              </label>
              <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.88rem' }}>
                <input 
                  type="radio" 
                  name="unit_system" 
                  checked={unitSystem === 'Imperial'} 
                  onChange={() => setUnitSystem('Imperial')}
                  style={{ accentColor: 'var(--primary)' }}
                />
                Imperial (lb, ft, psi)
              </label>
            </div>
          </div>

          {errorMsg && (
            <div style={{ display: 'flex', gap: '8px', background: 'rgba(239, 68, 68, 0.12)', color: 'var(--status-failure)', padding: '12px', borderRadius: '8px', fontSize: '0.82rem', alignItems: 'center', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <AlertCircle size={16} />
              {errorMsg}
            </div>
          )}

          {successMsg && (
            <div style={{ display: 'flex', gap: '8px', background: 'rgba(16, 185, 129, 0.12)', color: 'var(--status-safe)', padding: '12px', borderRadius: '8px', fontSize: '0.82rem', alignItems: 'center', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <CheckCircle size={16} style={{ color: 'var(--status-safe)' }} />
              {successMsg}
            </div>
          )}

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '8px' }}>
            <Save size={18} />
            Compute & Save Scenario
          </button>
        </form>
      </div>

      {/* Research Notes Card */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>Research Notebook</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Annotate experimental configurations</span>
        </div>

        {!activeScenario ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', padding: '20px' }}>
            Save or select a scenario from the sidebar to start writing notebooks.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflow: 'hidden' }}>
            {/* Add note form */}
            <form onSubmit={handleAddNote} style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Type research note or validation citation..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                style={{ flex: 1 }}
              />
              <button type="submit" className="btn btn-secondary" style={{ padding: '8px 16px' }}>
                <Plus size={16} />
                Add
              </button>
            </form>

            {/* Note items scroll */}
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px', paddingRight: '4px' }}>
              {notesList.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', textAlign: 'center', padding: '40px 0' }}>
                  No notebook entries for this scenario. Add one above!
                </div>
              ) : (
                notesList.map((n) => (
                  <div key={n.id} style={{ padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      <ClipboardList size={12} />
                      <span>{new Date(n.created_at).toLocaleString()}</span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.4' }}>
                      {n.note}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Inline helper because import failed
function CheckCircle({ size, style }: { size: number; style?: React.CSSProperties }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={style}>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  );
}
