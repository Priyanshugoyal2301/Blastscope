import { Flame, ShieldAlert, BarChart3, Database, Clock } from 'lucide-react';
import { Scenario } from '../types';

interface SidebarProps {
  currentScreen: 'input' | 'results' | 'assessment' | 'workspace';
  setCurrentScreen: (screen: 'input' | 'results' | 'assessment' | 'workspace') => void;
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
  const navItems = [
    { id: 'input', label: 'Scenario Input', icon: Database },
    { id: 'results', label: 'Blast Results', icon: Flame },
    { id: 'assessment', label: 'Material Assessment', icon: ShieldAlert },
    { id: 'workspace', label: 'Research Workspace', icon: BarChart3 },
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
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff' }}>BlastScope</h2>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Offline Physics Platform</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentScreen(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                background: isActive ? 'rgba(99, 102, 241, 0.12)' : 'transparent',
                color: isActive ? '#818cf8' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
            >
              <Icon size={18} />
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
                  borderColor: isSelected ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                  background: isSelected ? 'rgba(99, 102, 241, 0.05)' : 'rgba(255, 255, 255, 0.01)',
                  color: isSelected ? '#fff' : 'var(--text-muted)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ fontWeight: 600, fontSize: '0.82rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
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
    </aside>
  );
}
