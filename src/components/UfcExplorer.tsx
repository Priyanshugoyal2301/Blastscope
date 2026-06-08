import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { UfcReference } from '../types';
import { X, Search, Book, Bookmark } from 'lucide-react';

interface UfcExplorerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function UfcExplorer({ isOpen, onClose }: UfcExplorerProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UfcReference[]>([]);
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const copyCitation = (ref: UfcReference, format: 'APA' | 'IEEE' | 'Chicago') => {
    let citation = '';
    if (format === 'APA') {
      citation = `Department of Defense. (2008). Unified Facilities Criteria: Structures to Resist the Effects of Accidental Explosions (UFC 3-340-02). Washington, DC: Department of Defense. (Figure: ${ref.figure_number}, p. ${ref.source_page}).`;
    } else if (format === 'IEEE') {
      citation = `Unified Facilities Criteria: Structures to Resist the Effects of Accidental Explosions, UFC 3-340-02, Dept. of Defense, Washington, DC, 2008, Fig. ${ref.figure_number}, p. ${ref.source_page}.`;
    } else {
      // Chicago
      citation = `U.S. Department of Defense. Unified Facilities Criteria: Structures to Resist the Effects of Accidental Explosions (UFC 3-340-02). Washington, DC: Department of Defense, 2008. Figure ${ref.figure_number}, page ${ref.source_page}.`;
    }
    navigator.clipboard.writeText(citation);
    setCopiedId(ref.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  useEffect(() => {
    async function fetchReferences() {
      try {
        const refList = await api.ufc.search(query);
        setResults(refList);
      } catch (e) {
        console.error('Error fetching UFC refs:', e);
      }
    }
    
    if (isOpen) {
      fetchReferences();
    }
  }, [query, isOpen]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'absolute',
      top: 0,
      right: 0,
      width: '400px',
      height: '100vh',
      background: 'var(--bg-sidebar)',
      borderLeft: '1px solid var(--border-color)',
      boxShadow: '-10px 0 30px rgba(0,0,0,0.5)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 100,
      animation: 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
    }}>
      {/* Drawer Header */}
      <div style={{
        padding: '20px',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Book size={20} className="text-primary" style={{ color: 'var(--primary)' }} />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>UFC Explorer</h2>
        </div>
        <button 
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>
      </div>

      {/* Dynamic Search Box */}
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search UFC Chapter 2 (e.g. Figure 2-7, surface)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ width: '100%', paddingLeft: '36px' }}
          />
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-muted)' }} />
        </div>
      </div>

      {/* Figures Scroll Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {results.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0', fontSize: '0.9rem' }}>
            No matching UFC figures found. Try 'incident' or '2-15'.
          </div>
        ) : (
          results.map((ref) => (
            <div 
              key={ref.id} 
              className="glass-panel" 
              style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', display: 'flex', flexDirection: 'column', gap: '8px' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="badge badge-minor" style={{ fontSize: '0.65rem' }}>
                  {ref.figure_number}
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Bookmark size={10} />
                  Page {ref.source_page}
                </span>
              </div>
              
              <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff', marginTop: '4px' }}>
                {ref.title}
              </h3>
              
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                {ref.description}
              </p>

              {ref.keywords && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px' }}>
                  {ref.keywords.split(',').map((kw, i) => (
                    <span 
                      key={i} 
                      style={{ 
                        fontSize: '0.62rem', 
                        padding: '2px 6px', 
                        borderRadius: '4px', 
                        background: 'rgba(255,255,255,0.05)', 
                        color: 'var(--text-muted)' 
                      }}
                    >
                      {kw.trim()}
                    </span>
                  ))}
                </div>
              )}

              <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '8px', marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Copy Citation:</span>
                <div style={{ display: 'flex', gap: '6px' }}>
                  {['APA', 'IEEE', 'Chicago'].map((format) => (
                    <button
                      key={format}
                      onClick={() => copyCitation(ref, format as any)}
                      style={{
                        padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--border-color)',
                        background: 'rgba(255,255,255,0.03)', color: 'var(--text-main)', fontSize: '0.65rem',
                        cursor: 'pointer', transition: 'all 0.15s'
                      }}
                    >
                      {copiedId === ref.id ? 'Copied!' : format}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }
      `}</style>
    </div>
  );
}
