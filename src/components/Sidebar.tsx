import { Flame, ShieldAlert, BarChart3, Database, Clock, TrendingUp, Map, HelpCircle, Compass } from 'lucide-react';
import { Scenario } from '../types';
import { api } from '../services/api';
import { useState } from 'react';

interface SidebarProps {
  currentScreen: 'input' | 'results' | 'assessment' | 'workspace' | 'study' | 'vulnmap' | 'predict' | 'documentation';
  setCurrentScreen: (screen: 'input' | 'results' | 'assessment' | 'workspace' | 'study' | 'vulnmap' | 'predict' | 'documentation') => void;
  activeScenario: Scenario | null;
  scenarios: Scenario[];
  onSelectScenario: (sc: Scenario) => void;
}

export default function Sidebar({
  currentScreen,
  setCurrentScreen,
  activeScenario,
  scenarios,
  onSelectScenario
}: SidebarProps) {
  const [dbStatus, setDbStatus] = useState<string | null>(null);

  const handleExportDB = async () => {
    try {
      setDbStatus('Exporting...');
      const res = await api.database.export();
      if (res.success) {
        setDbStatus('Exported successfully!');
      } else if (res.canceled) {
        setDbStatus(null);
      } else {
        setDbStatus(`Error: ${res.error}`);
      }
      setTimeout(() => setDbStatus(null), 3000);
    } catch (e: any) {
      setDbStatus(`Error: ${e.message}`);
      setTimeout(() => setDbStatus(null), 3000);
    }
  };

  const handleImportDB = async () => {
    try {
      setDbStatus('Importing...');
      const res = await api.database.import();
      if (res.success) {
        setDbStatus('Imported! Reloading...');
        setTimeout(() => window.location.reload(), 1500);
      } else if (res.canceled) {
        setDbStatus(null);
      } else {
        setDbStatus(`Error: ${res.error}`);
        setTimeout(() => setDbStatus(null), 3000);
      }
    } catch (e: any) {
      setDbStatus(`Error: ${e.message}`);
      setTimeout(() => setDbStatus(null), 3000);
    }
  };

  const navItems = [
    { id: 'input',          label: 'Scenario Input',          icon: Database,     section: 'core' },
    { id: 'results',        label: 'Blast Results',            icon: Flame,        section: 'core' },
    { id: 'assessment',     label: 'Material Assessment',      icon: ShieldAlert,  section: 'core' },
    { id: 'workspace',      label: 'Research Workspace',       icon: BarChart3,    section: 'core' },
    { id: 'predict',        label: 'Threat Prediction',        icon: Compass,      section: 'core' },
    { id: 'study',          label: 'Parametric Study',         icon: TrendingUp,   section: 'study' },
    { id: 'vulnmap',        label: 'Vulnerability Map',        icon: Map,          section: 'study' },
    { id: 'documentation',  label: 'Documentation',            icon: HelpCircle,   section: 'help' }
  ] as const;

  return (
    <aside style={{
      width: '260px',
      background: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      flexShrink: 0
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '24px',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, var(--primary), var(--accent))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 'bold',
          color: '#fff',
          fontFamily: 'Outfit'
        }}>
          BS
        </div>
        <div>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>BlastScope</h2>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Offline Physics Platform</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {/* Core section */}
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', padding: '4px 14px 6px', opacity: 0.6 }}>Analysis</div>
        {navItems.filter(i => i.section === 'core').map((item) => {
          const Icon = item.icon;
          const isActive = currentScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentScreen(item.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '12px',
                width: '100%', padding: '10px 14px', borderRadius: '8px',
                border: 'none',
                background: isActive ? 'rgba(37, 99, 235, 0.08)' : 'transparent',
                color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 500, fontSize: '0.9rem',
                cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s',
                borderLeft: isActive ? '2px solid var(--primary)' : '2px solid transparent',
              }}
            >
              <Icon size={17} />
              {item.label}
            </button>
          );
        })}

        {/* Studies section */}
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', padding: '10px 14px 6px', opacity: 0.6 }}>Parametric Studies</div>
        {navItems.filter(i => i.section === 'study').map((item) => {
          const Icon = item.icon;
          const isActive = currentScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentScreen(item.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '12px',
                width: '100%', padding: '10px 14px', borderRadius: '8px',
                border: 'none',
                background: isActive ? 'rgba(22, 163, 74, 0.08)' : 'transparent',
                color: isActive ? 'var(--status-safe)' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 500, fontSize: '0.9rem',
                cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s',
                borderLeft: isActive ? '2px solid var(--status-safe)' : '2px solid transparent',
              }}
            >
              <Icon size={17} />
              {item.label}
            </button>
          );
        })}
        {/* Help/Doc section */}
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', padding: '10px 14px 6px', opacity: 0.6 }}>Reference & Help</div>
        {navItems.filter(i => i.section === 'help').map((item) => {
          const Icon = item.icon;
          const isActive = currentScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentScreen(item.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '12px',
                width: '100%', padding: '10px 14px', borderRadius: '8px',
                border: 'none',
                background: isActive ? 'rgba(37, 99, 235, 0.08)' : 'transparent',
                color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 500, fontSize: '0.9rem',
                cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s',
                borderLeft: isActive ? '2px solid var(--primary)' : '2px solid transparent',
              }}
            >
              <Icon size={17} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Saved Scenarios List */}
      <div style={{
        flex: 1,
        borderTop: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '16px 20px 8px 20px',
          fontSize: '0.75rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Clock size={12} />
          Saved Scenarios ({scenarios.length})
        </div>

        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '0 12px 16px 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px'
        }}>
          {scenarios.map((sc) => {
            const isSelected = activeScenario?.id === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => onSelectScenario(sc)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px',
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  border: '1px solid',
                  borderColor: isSelected ? 'var(--primary)' : 'transparent',
                  background: isSelected ? 'rgba(37, 99, 235, 0.06)' : 'rgba(0, 0, 0, 0.02)',
                  color: isSelected ? 'var(--text-main)' : 'var(--text-muted)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ fontWeight: 600, fontSize: '0.82rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: isSelected ? 'var(--text-main)' : 'var(--text-muted)' }}>
                  {sc.name}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', gap: '8px' }}>
                  <span>{sc.charge_weight} kg {sc.explosive_name || 'TNT'}</span>
                  <span>•</span>
                  <span>{sc.distance} m</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Database Actions Footer */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', opacity: 0.6 }}>
          Database Settings
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <button
            onClick={handleExportDB}
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '6px 8px', justifyContent: 'center' }}
            title="Export runtime database backup"
          >
            Export DB
          </button>
          <button
            onClick={handleImportDB}
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '6px 8px', justifyContent: 'center' }}
            title="Import/Replace database file"
          >
            Import DB
          </button>
        </div>
        {dbStatus && (
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '4px' }}>
            {dbStatus}
          </div>
        )}
      </div>
    </aside>
  );
}
