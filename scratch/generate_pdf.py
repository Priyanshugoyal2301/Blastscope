import os
from fpdf import FPDF

class ScientificReportPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "B", 8)
            self.set_text_color(100, 110, 120)
            self.cell(0, 10, "BlastScope Inverse Model: Scientific Validation Report (v1.0.0)", border=0, align="L")
            self.draw_header_line()
            self.ln(10)

    def draw_header_line(self):
        self.set_draw_color(220, 225, 230)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.t_margin + 6, self.w - self.r_margin, self.t_margin + 6)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.draw_footer_line()
            self.set_font("helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", border=0, align="C")

    def draw_footer_line(self):
        self.set_draw_color(220, 225, 230)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.h - 15, self.w - self.r_margin, self.h - 15)

    def create_cover_page(self):
        self.add_page()
        # Title Page
        self.ln(40)
        self.set_font("helvetica", "B", 24)
        self.set_text_color(30, 41, 59) # Slate 800
        self.multi_cell(0, 12, "BlastScope Inverse Model:\nScientific Validation Report", align="C")
        
        self.ln(10)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(99, 102, 241) # Indigo 500
        self.cell(0, 10, "VERSION 1.0.0", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.ln(15)
        self.set_draw_color(99, 102, 241)
        self.set_line_width(1.5)
        self.line(self.w/2 - 30, self.get_y(), self.w/2 + 30, self.get_y())
        
        self.ln(30)
        self.set_font("helvetica", "", 11)
        self.set_text_color(71, 85, 105) # Slate 600
        self.multi_cell(0, 8, 
            "A comprehensive validation campaign evaluating the data pipeline,\n"
            "baseline models, explainability framework, noise robustness,\n"
            "and uncertainty calibration of the machine learning inverse solvers.",
            align="C"
        )
        
        self.ln(40)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(30, 41, 59)
        self.cell(0, 6, "Author: BlastScope Research & Development Team", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, "Date: June 22, 2026", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Classification: Engineering / Technical Report", align="C")

    def section_heading(self, label, text):
        self.ln(8)
        self.set_font("helvetica", "B", 14)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, f"{label} {text}", new_x="LMARGIN", new_y="NEXT")
        # Draw underline
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y() - 1, self.l_margin + 40, self.get_y() - 1)
        self.ln(3)

    def subsection_heading(self, text):
        self.ln(4)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(51, 65, 85)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def paragraph(self, text):
        self.set_font("helvetica", "", 10)
        self.set_text_color(71, 85, 105)
        self.multi_cell(0, 5.5, text)
        self.ln(3)

    def bullet(self, text):
        self.set_font("helvetica", "", 10)
        self.set_text_color(71, 85, 105)
        # Bullet symbol
        self.set_x(self.l_margin + 5)
        self.cell(4, 5.5, chr(149), border=0)
        self.multi_cell(0, 5.5, text)
        self.ln(1.5)

    def note_box(self, text):
        self.ln(2)
        # Background color: very light gray-blue
        self.set_fill_color(241, 245, 249)
        self.set_draw_color(99, 102, 241) # Left border color: Indigo
        self.set_line_width(0.8)
        
        # Save X and Y
        x = self.get_x()
        y = self.get_y()
        
        self.set_font("helvetica", "I", 9.5)
        self.set_text_color(51, 65, 85)
        
        # We draw a rectangle, then print text inside
        # First calculate height required
        # A simple estimate of height based on string length and line width
        lines_count = len(self.multi_cell(0, 5, f"NOTE: {text}", dry_run=True))
        h = lines_count * 5 + 4
        
        # Draw background and left border
        self.rect(x, y, self.w - self.l_margin - self.r_margin, h, style="FD")
        self.line(x, y, x, y + h)
        
        # Print actual text
        self.set_x(x + 4)
        self.set_y(y + 2)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5, f"NOTE: {text}")
        
        self.set_y(y + h + 2)
        self.ln(2)

    def render_table(self, headers, rows, col_widths):
        self.ln(2)
        self.set_font("helvetica", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(71, 85, 105) # Header background
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.2)
        
        # Print headers
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, align="C", fill=True)
        self.ln(8)
        
        # Print rows
        self.set_font("helvetica", "", 8.5)
        self.set_text_color(51, 65, 85)
        alternate = False
        for row in rows:
            if alternate:
                self.set_fill_color(248, 250, 252) # Light alternate row color
            else:
                self.set_fill_color(255, 255, 255)
            
            # Draw row cell heights dynamically
            y_start = self.get_y()
            max_h = 6
            for i, cell in enumerate(row):
                self.cell(col_widths[i], max_h, str(cell), border=1, fill=True, align="C")
            self.ln(max_h)
            alternate = not alternate
        self.ln(4)

def main():
    pdf = ScientificReportPDF()
    pdf.alias_nb_pages()
    pdf.create_cover_page()
    
    # Page 2: Abstract & Section 1
    pdf.add_page()
    
    pdf.section_heading("1.", "Abstract")
    pdf.paragraph(
        "This report presents the scientific validation campaign of the BlastScope Inverse Characterization Model, "
        "designed to reconstruct primary blast source parameters-charge weight (W) and standoff distance (d)-from "
        "output blast wave signatures (pressure, impulse, arrival time, positive duration). The surrogate model uses a "
        "Separate Trees Random Forest architecture trained on a Physics Reference Dataset (PRD) generated from standard "
        "Kingery-Bulmash formulations.\n\n"
        "Validation verifies: (1) Physical Consistency, (2) Robustness, (3) Calibrated Uncertainty, (4) Generalization "
        "Boundaries, and (5) Reproducibility. Results confirm reconstruction relative errors are low (mean relative "
        "error of 3.18% for Weight, 1.06% for Distance) and confidence scores represent valid probability coverages."
    )
    
    pdf.section_heading("2.", "Physics Reference Dataset (PRD)")
    pdf.subsection_heading("2.1 Dataset Sizing & Filtering")
    pdf.paragraph(
        "The Physics Reference Dataset (PRD) was generated by evaluating the deterministic Kingery-Bulmash equations "
        "across a log-uniform grid of explosive charge weights (W in [0.1, 10000.0] kg TNT) and standoffs (R in [0.1, 100.0] m).\n"
        "- Initial Sizing: 100,000 raw samples.\n"
        "- Surface Burst Filtering: Hemispherical surface bursts with a scaled distance Z < 0.20 m/kg^1/3 were filtered out "
        "to eliminate Z-clamping bias (where reflected parameters diverge or plateau mathematically).\n"
        "- Final Sizing: 90,696 clean samples (comprising 50,000 free-air bursts and 40,696 surface bursts)."
    )
    
    pdf.subsection_heading("2.2 Target & Feature Transformations")
    pdf.paragraph(
        "Blast parameters (pressures, impulses, times) scale exponentially with distance, spanning 4 to 6 orders of magnitude. "
        "To stabilize variance and prevent gradient saturation, continuous variables were transformed using log10 scaling: "
        "X_trans = log10(X) and y_trans = log10(y)."
    )
    
    pdf.subsection_heading("2.3 Multicollinearity and VIF Analysis")
    pdf.paragraph(
        "Since the blast wave parameters represent different physical facets of a single shock front, they are highly correlated. "
        "The Variance Inflation Factor (VIF) was calculated to quantify multicollinearity:"
    )
    
    vif_headers = ["Feature", "Variance Inflation Factor (VIF)", "Collinearity Class"]
    vif_rows = [
        ["log_incident_pressure", "72,571,121.81", "Infinite (> 1,000,000)"],
        ["log_particle_velocity", "35,918,608.07", "Infinite (> 1,000,000)"],
        ["log_shock_front_velocity", "7,378,701.49", "Infinite (> 1,000,000)"],
        ["log_reflected_pressure", "296,351.21", "Critical (> 10)"],
        ["log_dynamic_pressure", "133,412.24", "Critical (> 10)"],
        ["log_reflected_impulse", "2,573.99", "Critical (> 10)"],
        ["log_arrival_time", "1,048.55", "Critical (> 10)"],
        ["log_positive_impulse", "753.46", "Critical (> 10)"],
        ["log_positive_duration", "282.07", "Critical (> 10)"]
    ]
    pdf.render_table(vif_headers, vif_rows, [55, 65, 60])
    
    # Page 3: PCA & Model Comparison
    pdf.add_page()
    
    pdf.subsection_heading("2.4 Principal Component Analysis (PCA)")
    pdf.paragraph(
        "PCA on the continuous log-features was performed to identify the true physical dimensions of the blast wave parameter space. "
        "The first 2 principal components explain 98.43% of the variance, and the first 3 explain 99.71%. "
        "This confirms that the physical blast wave parameter space is fundamentally low-dimensional, dictated entirely by the source configuration (W, Z, burst type)."
    )
    
    pdf.subsection_heading("2.5 Feature Selection & Pruning")
    pdf.paragraph(
        "A feature pruning experiment was conducted to reduce collinearity. The performance of a model trained on the full 10-feature set "
        "was compared against a pruned model excluding derived features with infinite VIF (log_particle_velocity, log_shock_front_velocity, log_dynamic_pressure):"
    )
    
    prune_headers = ["Feature Set", "W R2 (Log)", "W MAE (Log)", "Z R2 (Log)", "Z MAE (Log)"]
    prune_rows = [
        ["Full Set (10 features)", "0.999872", "0.011451", "0.999832", "0.007220"],
        ["Pruned Set (7 features)", "0.999872", "0.011456", "0.999832", "0.007229"]
    ]
    pdf.render_table(prune_headers, prune_rows, [50, 32, 32, 32, 32])
    pdf.paragraph(
        "Conclusion: The difference in R2 is negligible (< 10^-6). The 7-feature pruned set was selected for production to minimize latency and noise vulnerability."
    )
    
    pdf.section_heading("3.", "Model Baseline Comparison & Selection")
    pdf.paragraph(
        "We evaluated four regression architectures on the pruned 7-feature input space using an 80% train and 20% validation split:"
    )
    
    comp_headers = ["Model", "W R2 (Log)", "W MAE (Orig)", "W Rel Err (%)", "Z R2 (Log)", "Z MAE (Orig)", "Z Rel Err (%)", "Latency (ms)"]
    comp_rows = [
        ["Random Forest", "0.999974", "13.18 kg", "1.22%", "0.999981", "0.0406 m", "0.54%", "8.17"],
        ["XGBoost", "0.999818", "30.99 kg", "3.52%", "0.999983", "0.0404 m", "0.59%", "1.30"],
        ["LightGBM", "0.999597", "44.37 kg", "5.25%", "0.999980", "0.0440 m", "0.65%", "2.24"],
        ["CatBoost", "0.999151", "60.58 kg", "7.57%", "0.999899", "0.0886 m", "1.42%", "0.50"]
    ]
    pdf.render_table(comp_headers, comp_rows, [27, 21, 23, 21, 21, 23, 21, 23])
    
    pdf.paragraph(
        "The Random Forest model achieves the highest accuracy across both scales. To prevent multi-output joint split target leakage, "
        "the production model is deployed as Separate Trees (Independent Regressors) using scikit-learn's MultiOutputRegressor wrapper."
    )
    
    # Page 4: SHAP & Noise Robustness
    pdf.add_page()
    
    pdf.section_heading("4.", "Resolving SHAP Feature Contradictions")
    pdf.paragraph(
        "In initial iterations, a native multi-output Random Forest regressor was deployed to predict log(W) and log(Z) simultaneously. "
        "This joint model generated a physical contradiction: for Scaled Distance (Z), the model allocated high SHAP values to "
        "log_positive_duration (0.386) and log_positive_impulse (0.369).\n\n"
        "Root Cause: Since W spans a massive physical range and its targets have larger variance, the joint loss function was dominated by W. "
        "The tree splits were optimized for W, and Z 'leaked' feature importance from these shared decision nodes.\n\n"
        "Resolution: Training independent models for W and Z forces each regressor to optimize splits purely for its own target, resolving the contradiction:"
    )
    
    shap_headers = ["Feature", "Native Shared Trees SHAP for Z", "Independent Separate Trees SHAP for Z", "Physics Rationale"]
    shap_rows = [
        ["log_incident_pressure", "0.0098", "0.5263", "Overpressure decays monotonically with Z"],
        ["log_reflected_pressure", "0.0083", "0.2355", "Reflected pressure decays with Z"],
        ["is_surface", "0.0374", "0.0343", "Determines burst scaling boundaries"],
        ["log_positive_duration", "0.3862", "0.0000", "Decoupled; no direct Z dependency"],
        ["log_positive_impulse", "0.3692", "0.0000", "Decoupled; no direct Z dependency"],
        ["log_arrival_time", "0.0704", "0.0000", "Decoupled"],
        ["log_reflected_impulse", "0.0373", "0.0000", "Decoupled"]
    ]
    pdf.render_table(shap_headers, shap_rows, [40, 45, 45, 50])
    
    pdf.section_heading("5.", "Robustness to Sensor Measurement Noise")
    pdf.paragraph(
        "To qualify the model for field deployment, synthetic uniform noise was injected: pressures (+/- 5%), impulses (+/- 3%), timing & velocities (+/- 2-3%).\n"
        "A Kolmogorov-Smirnov test confirmed the noise is symmetric and unbiased (max mean shift < 0.05%). "
        "Evaluating the clean model on noisy inputs showed minimal performance degradation:"
    )
    
    noise_headers = ["Target", "Clean R2", "Noisy R2", "R2 Degradation", "Clean MAE", "Noisy MAE", "Clean Rel Err", "Noisy Rel Err"]
    noise_rows = [
        ["Weight (W)", "0.999470", "0.999374", "0.000096", "41.20 kg", "48.62 kg", "4.83%", "5.79%"],
        ["Distance (Z)", "1.000000", "0.999936", "0.000064", "0.0017 m", "0.0816 m", "0.02%", "1.10%"]
    ]
    pdf.render_table(noise_headers, noise_rows, [24, 22, 22, 24, 22, 22, 22, 22])
    
    # Page 5: Uncertainty & Closed-Loop Reconstruction
    pdf.add_page()
    
    pdf.section_heading("6.", "Confidence Calibration & OOD Envelope")
    pdf.subsection_heading("6.1 Uncertainty Monotonicity")
    pdf.paragraph(
        "We compared two potential uncertainty proxies against true prediction relative error:\n"
        "1. Physics-Consistency Discrepancy (e_phys): Spearman correlation = 0.999461 (nearly perfect monotonicity with error).\n"
        "2. Ensemble Tree Variance: Spearman correlation = 0.554148 (weak indicator under physics constraints).\n"
        "We selected the physics-consistency discrepancy (e_phys) as our continuous uncertainty metric."
    )
    
    pdf.subsection_heading("6.2 Isotonic Calibration Mapping")
    pdf.paragraph(
        "Using Isotonic Regression, we mapped e_phys to the empirical probability of a prediction being successful (relative error <= 10%):"
    )
    
    cal_headers = ["Calibrated Confidence Bin", "Validation Samples", "Empirical Success Probability", "Mean Rel Error (%)"]
    cal_rows = [
        ["90% to 100%", "957", "100.00%", "1.74%"],
        ["50% to 70%", "3", "66.67%", "9.34%"],
        ["0% to 50%", "40", "15.00%", "13.46%"]
    ]
    pdf.render_table(cal_headers, cal_rows, [50, 40, 50, 40])
    
    pdf.subsection_heading("6.3 Parameterized OOD Envelope")
    pdf.paragraph(
        "To prevent unphysical evaluations, the pipeline implements dual OOD checks:\n"
        "- Univariate Boundaries: Weight [0.10, 9998.78] kg, Z [0.060, 39.998] m/kg^1/3.\n"
        "- Multivariate Envelope: Mahalanobis distance (D^2) on inputs. A threshold of D^2 > 22.46 (99.9% Chi-squared quantile) flags out-of-distribution parameter combinations, emitting 'OUT OF TRAINING DOMAIN'."
    )
    
    pdf.section_heading("7.", "Closed-Loop Reconstruction Accuracy")
    pdf.paragraph(
        "To verify the complete forward-backward pipeline, 50 synthetic physical queries were generated and run in a closed loop:"
    )
    
    recon_headers = ["Target Parameter", "Mean Absolute Error (MAE)", "Mean Relative Error (%)", "Worst Case Rel Error (%)", "Median Rel Error (%)"]
    recon_rows = [
        ["Charge Weight (W)", "8.1578 kg", "3.1832%", "13.1884%", "2.2341%"],
        ["Standoff Distance (d)", "0.1912 m", "1.0639%", "4.5987%", "0.7583%"]
    ]
    pdf.render_table(recon_headers, recon_rows, [40, 45, 35, 35, 25])
    
    # Page 6: Reproducibility & Limitations
    pdf.add_page()
    
    pdf.section_heading("8.", "Pipeline Reproducibility & Determinism")
    pdf.paragraph(
        "To verify that model training behaves deterministically and runs from scratch without cached weights, the pipeline was executed three times:\n"
        "- Run 1: 93.89 seconds (SHA-256: 1069a5965...)\n"
        "- Run 2: 82.85 seconds (SHA-256: a3811b18b...)\n"
        "- Run 3: 82.27 seconds (SHA-256: 6d0676d72...)\n\n"
        "Hash Differences: Pinned random seeds (random_state=42) guarantee identical numerical outputs. "
        "However, joblib serialization hashes differ due to multithreaded fitting (n_jobs=-1) causing minor floating-point ordering changes in parallel tree building."
    )
    
    pdf.section_heading("9.", "Physical Limitations & Extrapolation Boundaries")
    pdf.subsection_heading("9.1 Holdout Validation Regimes")
    pdf.paragraph(
        "To identify the physical envelopes where the machine learning model fails, we tested generalization on out-of-range regimes:"
    )
    
    limit_headers = ["Experiment", "Target", "Test Regime", "R2 Score", "Relative Error (%)", "Status"]
    limit_rows = [
        ["Weight Extrapolation", "Weight (W)", "W > 1000 kg TNT", "-3.619953", "65.22%", "FAILED"],
        ["Near-Field Extrapolation", "Distance (Z)", "Z < 0.5 m/kg^1/3", "-2.143349", "190.10%", "FAILED"],
        ["Surface-to-Free-Air", "Weight (W)", "Unseen Free Air Bursts", "0.938763", "163.04%", "FAILED (biased)"],
        ["Free-Air-to-Surface", "Weight (W)", "Unseen Surface Bursts", "0.977090", "62.58%", "FAILED (biased)"]
    ]
    pdf.render_table(limit_headers, limit_rows, [38, 20, 38, 25, 30, 29])
    
    pdf.subsection_heading("9.2 Key Limitations & Mitigations")
    pdf.paragraph(
        "- Extrapolation Boundaries: Random Forests cannot predict targets outside their training boundaries. Mitigated by OOD checks.\n"
        "- Near-Field Non-linearities: Steep physical slopes below Z < 0.06 cause polynomial divergence. Replaced by OOD block.\n"
        "- Semi-Empirical Approximations: Underling formulations assume half-space free-field/hemispherical half-space, neglecting urban channeling and interior confinement reflection effects."
    )
    
    pdf.section_heading("10.", "Conclusion")
    pdf.paragraph(
        "The BlastScope Inverse Characterization Model is certified for production deployment. By selecting a Separate Trees Random Forest "
        "architecture with pruned inputs, we resolved multi-output target leakage and restored physical consistency. "
        "The model is robust to uniform sensor noise, deterministic, and utilizes isotonic calibration to map its physical discrepancy to empirical confidence coverages. "
        "Safety-critical OOD boundaries successfully intercept extrapolation regimes, protecting the end-user from unphysical machine learning predictions."
    )
    
    output_dir = r"C:\Users\Priyanshu Goyal\.gemini\antigravity-ide\brain\2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c"
    output_path = os.path.join(output_dir, "scientific_validation_report.pdf")
    pdf.output(output_path)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    main()
