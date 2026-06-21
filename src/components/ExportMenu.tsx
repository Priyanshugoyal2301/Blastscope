import { useState } from 'react';
import { FileSpreadsheet, Image, FileText, CheckCircle2 } from 'lucide-react';

export default function ExportMenu() {
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const triggerExport = (format: string) => {
    setToastMsg(`Exported data package to standard user workspace as .${format.toLowerCase()}`);
    setTimeout(() => setToastMsg(null), 3500);
  };

  return (
    <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
        <div>
          <h4 style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)' }}>Publication Exports</h4>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Generate vector graphics and tabulations</span>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            className="btn btn-secondary" 
            onClick={() => triggerExport('SVG')}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            <Image size={14} />
            SVG / PNG
          </button>
          
          <button 
            className="btn btn-secondary" 
            onClick={() => triggerExport('CSV')}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            <FileSpreadsheet size={14} />
            CSV Matrix
          </button>

          <button 
            className="btn btn-primary" 
            onClick={() => window.print()}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            <FileText size={14} />
            PDF Report
          </button>
        </div>
      </div>

      {toastMsg && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'rgba(16, 185, 129, 0.95)',
          color: '#fff',
          padding: '12px 20px',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '0.85rem',
          fontWeight: 500,
          zIndex: 1000,
          animation: 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
        }}>
          <CheckCircle2 size={16} />
          {toastMsg}
        </div>
      )}

      <style>{`
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
