import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import UfcExplorer from './components/UfcExplorer';
import ScenarioInput from './screens/ScenarioInput';
import BlastResultsScreen from './screens/BlastResults';
import MaterialAssessmentScreen from './screens/MaterialAssessment';
import ResearchWorkspace from './screens/ResearchWorkspace';
import ParametricStudy from './screens/ParametricStudy';
import VulnerabilityMap from './screens/VulnerabilityMap';
import PredictScreen from './screens/PredictScreen';
import Documentation from './screens/Documentation';
import ReportGenerator from './components/ReportGenerator';
import { api } from './services/api';
import { Scenario, Explosive, MaterialProfile, BlastResults, DamageAssessment, GridResult, ValidationCase, ValidationSummary } from './types';
import { BookOpen } from 'lucide-react';
 
export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'input' | 'results' | 'assessment' | 'workspace' | 'study' | 'vulnmap' | 'predict' | 'documentation'>('input');
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [explosives, setExplosives] = useState<Explosive[]>([]);
  const [profiles, setProfiles] = useState<MaterialProfile[]>([]);
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(null);
  
  const [activeResults, setActiveResults] = useState<BlastResults | null>(null);
  const [activeAssessments, setActiveAssessments] = useState<DamageAssessment[]>([]);
  const [gridResult, setGridResult] = useState<GridResult | null>(null);
  const [validationSummary, setValidationSummary] = useState<ValidationSummary[]>([]);
  const [validationCases, setValidationCases] = useState<ValidationCase[]>([]);
  const [isUfcOpen, setIsUfcOpen] = useState(false);
  const [solverStatus, setSolverStatus] = useState<'normal' | 'crashed'>('normal');

  // Listen to solver status events
  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).api && (window as any).api.onSolverStatus) {
      const unsubscribe = (window as any).api.onSolverStatus((data: { status: 'crashed' | 'recovered' }) => {
        if (data.status === 'crashed') {
          setSolverStatus('crashed');
        } else if (data.status === 'recovered') {
          setSolverStatus('normal');
        }
      });
      return unsubscribe;
    }
  }, []);

  // Load baseline seeds on startup
  useEffect(() => {
    async function loadSeeds() {
      try {
        const scList = await api.scenarios.list();
        setScenarios(scList);
        
        const expList = await api.explosives.list();
        setExplosives(expList);
        
        const profList = await api.materials.listProfiles();
        setProfiles(profList);

        // Fetch validation benchmarks on startup
        const vCases = await api.validation.runSweep();
        setValidationCases(vCases);
        const vSum = await api.validation.getSummary();
        setValidationSummary(vSum);

        if (scList.length > 0) {
          handleSelectScenario(scList[0]);
        }
      } catch (e) {
        console.error('Error loading seeds:', e);
      }
    }
    loadSeeds();
  }, []);

  const handleSelectScenario = async (sc: Scenario) => {
    setActiveScenario(sc);
    try {
      // Fetch calculation parameters environment
      const results = await api.blast.calculateEnvironment({
        chargeWeight: sc.charge_weight,
        distance: sc.distance,
        burstType: sc.burst_type,
        explosiveId: sc.explosive_id
      });
      setActiveResults(results);

      // Perform damage assessment batch
      const assessments = await api.material.assessBatch(results);
      setActiveAssessments(assessments);
    } catch (e) {
      console.error('Error loading scenario results:', e);
    }
  };

  const refreshScenarios = async () => {
    const list = await api.scenarios.list();
    setScenarios(list);
  };

  if (solverStatus === 'crashed') {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        width: '100vw',
        backgroundColor: '#F5F7FA',
        fontFamily: 'Inter, system-ui, sans-serif',
        color: '#1F2937',
        padding: '24px'
      }}>
        <div style={{
          backgroundColor: '#FFFFFF',
          padding: '40px',
          borderRadius: '8px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          maxWidth: '600px',
          width: '100%',
          borderTop: '4px solid #DC2626',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '3rem',
            color: '#DC2626',
            marginBottom: '16px'
          }}>
            ⚠️
          </div>
          <h1 id="solver-error-title" style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            marginBottom: '12px',
            color: '#1F2937'
          }}>
            Solver Process Crash Loop Detected
          </h1>
          <p id="solver-error-desc" style={{
            fontSize: '0.95rem',
            lineHeight: '1.5',
            color: '#4B5563',
            marginBottom: '24px'
          }}>
            The BlastScope physics engine solver subprocess has encountered an unrecoverable failure after 3 restart attempts. This could be due to database corruption, missing environment dependencies, or a fatal calculations error.
          </p>
          <div style={{
            backgroundColor: '#F9FAFB',
            padding: '16px',
            borderRadius: '6px',
            border: '1px solid #E5E7EB',
            textAlign: 'left',
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            color: '#374151',
            marginBottom: '24px',
            whiteSpace: 'pre-wrap'
          }}>
            Diagnostics Code: SOLVER_CRASH_LOOP_LIMIT_EXCEEDED<br />
            Status: CRITICAL<br />
            Logs: %APPDATA%/BlastScope/logs/crash.log
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              id="solver-restart-btn"
              onClick={() => {
                setSolverStatus('normal');
                if (typeof window !== 'undefined' && (window as any).api && (window as any).api.invoke) {
                  (window as any).api.invoke('test:reset-recovery-attempts').catch(() => {});
                }
                window.location.reload();
              }}
              style={{
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '4px',
                fontWeight: 600,
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              Restart Solver Process
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar 
        currentScreen={currentScreen} 
        setCurrentScreen={setCurrentScreen} 
        activeScenario={activeScenario}
        scenarios={scenarios}
        onSelectScenario={handleSelectScenario}
      />
      
      <main className="main-content">
        {/* Top Header */}
        <header style={{
          height: '64px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          background: 'var(--bg-card)',
          backdropFilter: 'blur(8px)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'Outfit', color: 'var(--primary)' }}>
              BlastScope
            </span>
            <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(37, 99, 235, 0.08)', color: 'var(--primary)', fontWeight: 600, border: '1px solid rgba(37, 99, 235, 0.15)' }}>
              RESEARCH EDITION v1.0
            </span>
            {(typeof window === 'undefined' || !(window as any).api) && (
              <span 
                id="browser-warning-badge"
                style={{ 
                  fontSize: '0.75rem', 
                  padding: '2px 8px', 
                  borderRadius: '4px', 
                  background: 'rgba(220, 38, 38, 0.08)', 
                  color: '#DC2626', 
                  fontWeight: 600, 
                  border: '1px solid rgba(220, 38, 38, 0.15)' 
                }}
              >
                Browser Demo Mode (Simulated Calculations)
              </span>
            )}
          </div>

          <button 
            className="btn btn-secondary"
            onClick={() => setIsUfcOpen(!isUfcOpen)}
            style={{ padding: '8px 14px', fontSize: '0.85rem' }}
          >
            <BookOpen size={16} />
            UFC Explorer
          </button>
        </header>

        {/* Content Screens */}
        <div className="scrollable-view">
          {currentScreen === 'input' && (
            <ScenarioInput 
              explosives={explosives} 
              activeScenario={activeScenario}
              refreshScenarios={refreshScenarios}
              onSelectScenario={handleSelectScenario}
            />
          )}

          {currentScreen === 'results' && (
            <BlastResultsScreen 
              activeScenario={activeScenario} 
              results={activeResults} 
            />
          )}

          {currentScreen === 'assessment' && (
            <MaterialAssessmentScreen 
              activeScenario={activeScenario}
              assessments={activeAssessments} 
            />
          )}

          {currentScreen === 'workspace' && (
            <ResearchWorkspace 
              activeScenario={activeScenario}
              activeResults={activeResults}
              profiles={profiles}
              assessments={activeAssessments}
              validationSummary={validationSummary}
              validationCases={validationCases}
              onReloadValidation={async () => {
                const vCases = await api.validation.runSweep();
                setValidationCases(vCases);
                const vSum = await api.validation.getSummary();
                setValidationSummary(vSum);
              }}
            />
          )}

          {currentScreen === 'study' && (
            <ParametricStudy
              explosives={explosives}
              profiles={profiles}
              gridResult={gridResult}
              setGridResult={setGridResult}
            />
          )}

          {currentScreen === 'vulnmap' && (
            <VulnerabilityMap
              gridResult={gridResult}
              profiles={profiles}
            />
          )}

          {currentScreen === 'predict' && (
            <PredictScreen />
          )}

          {currentScreen === 'documentation' && (
            <Documentation />
          )}
        </div>
      </main>

      {/* UFC Explorer Sliding Panel */}
      <UfcExplorer isOpen={isUfcOpen} onClose={() => setIsUfcOpen(false)} />

      {/* Hidden Print Report Container */}
      <ReportGenerator 
        scenario={activeScenario}
        results={activeResults}
        assessments={activeAssessments}
        validationSummary={validationSummary}
        validationCases={validationCases}
      />
    </div>
  );
}
