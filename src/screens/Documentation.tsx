import { useState } from 'react';
import { Book, ShieldAlert, Cpu, Activity, Landmark, Layers, HelpCircle, FileText } from 'lucide-react';

type DocTab = 'getting-started' | 'physics' | 'materials' | 'pi-envelopes' | 'validation' | 'parametric' | 'exports' | 'references';

const TAB_LABELS: Record<DocTab, string> = {
  'getting-started': 'Getting Started',
  'physics': 'Blast Physics',
  'materials': 'Material Models',
  'pi-envelopes': 'P-I Envelopes',
  'validation': 'Validation',
  'parametric': 'Parametric Studies',
  'exports': 'Exporting Results',
  'references': 'References'
};

const TAB_ICONS: Record<DocTab, React.ReactNode> = {
  'getting-started': <HelpCircle size={15} />,
  'physics': <Activity size={15} />,
  'materials': <ShieldAlert size={15} />,
  'pi-envelopes': <Layers size={15} />,
  'validation': <Landmark size={15} />,
  'parametric': <Cpu size={15} />,
  'exports': <FileText size={15} />,
  'references': <Book size={15} />
};

export default function Documentation() {
  const [activeTab, setActiveTab] = useState<DocTab>('getting-started');

  return (
    <div style={{ display: 'flex', gap: '20px', height: '100%' }} className="animate-fade-in">
      {/* Doc Sidebar Navigation */}
      <div style={{ width: '220px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {(Object.keys(TAB_LABELS) as DocTab[]).map(tab => {
          const isActive = activeTab === tab;
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '10px 14px',
                border: '1px solid',
                borderColor: isActive ? 'var(--primary)' : 'transparent',
                borderRadius: '6px',
                background: isActive ? 'rgba(37, 99, 235, 0.08)' : 'transparent',
                color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                textAlign: 'left',
                fontSize: '0.85rem',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {TAB_ICONS[tab]}
              {TAB_LABELS[tab]}
            </button>
          );
        })}
      </div>

      {/* Doc Content Area */}
      <div className="glass-panel" style={{ flex: 1, padding: '24px', overflowY: 'auto', background: 'var(--bg-card)' }}>
        {activeTab === 'getting-started' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              1. Getting Started
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '12px' }}>
              Welcome to the **BlastScope** Research Platform. BlastScope is an advanced desktop engineering tool 
              designed to simulate blast wave dynamics, evaluate material responses under explosive loading, 
              and perform comparative validation studies.
            </p>
            <h3 style={{ fontSize: '1.05rem', color: 'var(--text-main)', margin: '18px 0 8px' }}>Core Workflow:</h3>
            <ol style={{ paddingLeft: '20px', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.7' }}>
              <li>Configure and save a threat **Scenario** (charge weight, standoff distance, and burst type).</li>
              <li>Examine pressure, duration, and impulse outcomes under the **Blast Results** tab.</li>
              <li>Perform **Material Assessments** to view safety ratings, governing modes, and damage mechanics.</li>
              <li>Use the **Research Workspace** to overlay capacity curves, inspect radar polar plots, and calibrate models against experimental benchmarks.</li>
              <li>Run multi-point **Parametric Studies** to map vulnerability gradients across multiple target types.</li>
            </ol>
          </div>
        )}

        {activeTab === 'physics' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              2. Blast Physics & Wave Formulation
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '14px' }}>
              BlastScope models free-field wave parameters using standard semi-empirical equations (Swisdak, 1994), 
              representing Kingery-Bulmash (1984) graphical datasets.
            </p>

            <h3 style={{ fontSize: '1.05rem', color: 'var(--text-main)', margin: '14px 0 6px' }}>TNT Equivalency</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '12px' }}>
              Non-TNT solid high-explosives are scaled using pressure and impulse equivalence factors:
            </p>
            <div style={{ padding: '10px 14px', background: 'rgba(0,0,0,0.03)', borderLeft: '3px solid var(--primary)', borderRadius: '4px', margin: '10px 0', fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: 'var(--text-main)' }}>
              W_p = W_actual * pressure_equivalency<br />
              W_i = W_actual * impulse_equivalency
            </div>

            <h3 style={{ fontSize: '1.05rem', color: 'var(--text-main)', margin: '14px 0 6px' }}>Scaled Distance (Standoff)</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '12px' }}>
              Calculations are computed relative to scaled standoff coordinates Z_p (pressure) and Z_i (impulse):
            </p>
            <div style={{ padding: '10px 14px', background: 'rgba(0,0,0,0.03)', borderLeft: '3px solid var(--primary)', borderRadius: '4px', margin: '10px 0', fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: 'var(--text-main)' }}>
              Z_p = R / W_p^(1/3)<br />
              Z_i = R / W_i^(1/3)
            </div>

            <h3 style={{ fontSize: '1.05rem', color: 'var(--text-main)', margin: '14px 0 6px' }}>Dynamic Pressure</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              Calculated using the peak incident pressure P_so and the ratio of specific heats of air:
            </p>
            <div style={{ padding: '10px 14px', background: 'rgba(0,0,0,0.03)', borderLeft: '3px solid var(--primary)', borderRadius: '4px', margin: '10px 0', fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: 'var(--text-main)' }}>
              Q_0 = (5/2) * P_so^2 / (7 * P_atm + P_so)
            </div>
          </div>
        )}

        {activeTab === 'materials' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              3. Material Response Models
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '14px' }}>
              BlastScope evaluates five structural material classes. The Damage Index (DI) represents the peak demand 
              ratio relative to dynamic yield boundaries:
            </p>

            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left', marginBottom: '14px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
                  <th style={{ padding: '8px' }}>Family</th>
                  <th style={{ padding: '8px' }}>Governing Failure Mechanism</th>
                  <th style={{ padding: '8px' }}>Mechanical Limit</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>Glass</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Fracture / Interlayer tearing</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Tensile flexural limit</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>Masonry</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Three-hinge flexural collapse</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Flexural tension / bond failure</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>Concrete (RC)</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Rear-face concrete spalling</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Concrete dynamic tensile spall</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>UHPC</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Steel micro-fiber pullout</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Localized high shear capacity</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>Steel</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Ductile yielding / boundary tear</td>
                  <td style={{ padding: '8px', color: 'var(--text-muted)' }}>Plastic membrane tension limit</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'pi-envelopes' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              4. Pressure-Impulse (P-I) Envelopes
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '12px' }}>
              A Pressure-Impulse (P-I) diagram represents dynamic damage boundaries. 
              The solver constructs progressive capacity curves (Minor, Moderate, Severe, and Failure) 
              using the hyperbolic equation:
            </p>
            <div style={{ padding: '10px 14px', background: 'rgba(0,0,0,0.03)', borderLeft: '3px solid var(--primary)', borderRadius: '4px', margin: '10px 0', fontFamily: 'JetBrains Mono', fontSize: '0.85rem', color: 'var(--text-main)' }}>
              (P - P_0) * (I - I_0) = K_c
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              Where:
              <ul style={{ paddingLeft: '20px', marginTop: '6px' }}>
                <li><strong>P_0</strong>: Pressure asymptote (quasi-static resistance limit).</li>
                <li><strong>I_0</strong>: Impulse asymptote (impulsive short-duration limit).</li>
                <li><strong>K_c</strong>: Constant governing the dynamic transition curve.</li>
              </ul>
            </p>
          </div>
        )}

        {activeTab === 'validation' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              5. Validation Methodology
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '12px' }}>
              To ensure research-grade alignment, the blast calculation engine is validated against a static matrix 
              of **30 validation cases** compiled directly from:
            </p>
            <ul style={{ paddingLeft: '20px', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.7', marginBottom: '12px' }}>
              <li><strong>UFC 3-340-02 Chapter 2</strong> blast charts (Figures 2-7, 2-15).</li>
              <li><strong>ConWep</strong> analytical outputs.</li>
              <li><strong>NSWC (Naval Surface Warfare Center)</strong> field trial reports.</li>
            </ul>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              Metrics tracked include Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and 95th Percentile 
              Absolute Error. Accuracy targets demand under **5% average error** for digitized references.
            </p>
          </div>
        )}

        {activeTab === 'parametric' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              6. Parametric Studies & point Limits
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '12px' }}>
              Researchers can run sweeps to examine structural response trends over distance standoff and charge weights:
            </p>
            <ul style={{ paddingLeft: '20px', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.7', marginBottom: '12px' }}>
              <li><strong>Distance Sweep</strong>: Vary standoff coordinates for a fixed charge.</li>
              <li><strong>Charge Sweep</strong>: Vary explosive weight for a fixed standoff.</li>
              <li><strong>Explosive Comparison</strong>: Compare pressure/severity contours across agents (ANFO, C4, RDX).</li>
              <li><strong>Grid Study</strong>: Generate 2D threat contours mapping damage index gradients.</li>
            </ul>
            <h3 style={{ fontSize: '1.05rem', color: 'var(--text-main)', margin: '14px 0 6px' }}>Safety Controls</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              To ensure Electron remains highly responsive, point counts are capped:
              <ul style={{ paddingLeft: '20px', marginTop: '6px' }}>
                <li><strong>0 to 2,000 points</strong>: Runs immediately.</li>
                <li><strong>2,001 to 5,000 points</strong>: Warns user of potential sweep latency.</li>
                <li><strong>5,001 to 10,000 points</strong>: Requires explicit confirmation in the UI.</li>
                <li><strong>&gt;10,000 points</strong>: Blocked to prevent UI freezes.</li>
              </ul>
            </p>
          </div>
        )}

        {activeTab === 'exports' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              7. Exporting Results
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '12px' }}>
              BlastScope supports standard exporting targets for publication:
            </p>
            <ul style={{ paddingLeft: '20px', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.7' }}>
              <li><strong>CSV Exports</strong>: Available on sweep runs. Opens a native save file dialog to write structured text.</li>
              <li><strong>JSON Datasets</strong>: Verification cases can be exported under the calibration tabs.</li>
              <li><strong>Research Reports (PDF)</strong>: Compiles inputs, calculations, material assessments, and citations into a print-friendly format using the system PDF generator.</li>
            </ul>
          </div>
        )}

        {activeTab === 'references' && (
          <div>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              8. Bibliographic References
            </h2>
            <ul style={{ paddingLeft: '20px', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.8' }}>
              <li>
                <strong>UFC 3-340-02 (2008)</strong>: *Structures to Resist the Effects of Accidental Explosions*, Unified Facilities Criteria, US Department of Defense.
              </li>
              <li>
                <strong>Swisdak, M. M. (1994)</strong>: *Simplified Kingery-Bulmash Equations*, Naval Surface Warfare Center, Report NSWCDD/TR-93/161.
              </li>
              <li>
                <strong>Kingery, C. N., & Bulmash, G. (1984)</strong>: *Airblast Parameters from TNT Spherical Air Burst and Hemispherical Surface Burst*, Technical Report BRL-TR-2555.
              </li>
              <li>
                <strong>TM5-1300 (1990)</strong>: *Design of Structures to Resist the Effects of Accidental Explosions*, US Department of the Army.
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
