import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import UfcExplorer from './components/UfcExplorer';
import ScenarioInput from './screens/ScenarioInput';
import BlastResultsScreen from './screens/BlastResults';
import MaterialAssessmentScreen from './screens/MaterialAssessment';
import ResearchWorkspace from './screens/ResearchWorkspace';
import { api } from './services/api';
import { Scenario, Explosive, MaterialProfile, BlastResults, DamageAssessment } from './types';
import { BookOpen } from 'lucide-react';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'input' | 'results' | 'assessment' | 'workspace'>('input');
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [explosives, setExplosives] = useState<Explosive[]>([]);
  const [profiles, setProfiles] = useState<MaterialProfile[]>([]);
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(null);
  
  const [activeResults, setActiveResults] = useState<BlastResults | null>(null);
  const [activeAssessments, setActiveAssessments] = useState<DamageAssessment[]>([]);
  const [isUfcOpen, setIsUfcOpen] = useState(false);

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
          background: 'rgba(11, 14, 26, 0.4)',
          backdropFilter: 'blur(8px)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'Outfit', background: 'linear-gradient(45deg, #6366f1, #d946ef)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              BlastScope
            </span>
            <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', fontWeight: 600, border: '1px solid rgba(99, 102, 241, 0.2)' }}>
              RESEARCH EDITION v1.0
            </span>
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
            />
          )}
        </div>
      </main>

      {/* UFC Explorer Sliding Panel */}
      <UfcExplorer isOpen={isUfcOpen} onClose={() => setIsUfcOpen(false)} />
    </div>
  );
}
