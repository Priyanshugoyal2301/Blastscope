import os
import sys
import argparse
import numpy as np
import pandas as pd
import contextlib

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.blast_engine.services.blast_calculator import BlastCalculatorService

@contextlib.contextmanager
def suppress_stderr():
    """Context manager to suppress sys.stderr output (clamping warnings)."""
    with open(os.devnull, "w") as fnull:
        old_stderr = sys.stderr
        sys.stderr = fnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def log_uniform(low, high, size):
    """Generates samples from a log-uniform distribution."""
    return np.exp(np.random.uniform(np.log(low), np.log(high), size))

def generate_samples(n_samples, seed=42):
    """
    Generates clean and noisy datasets using the forward physics solver.
    """
    np.random.seed(seed)
    
    # 50% Surface, 50% Free Air
    n_surface = n_samples // 2
    n_free_air = n_samples - n_surface
    
    records = []
    
    print(f"Generating {n_samples} samples (50% Surface, 50% Free Air)...")
    
    # Setup runs
    configs = [
        ("Surface", n_surface),
        ("Free Air", n_free_air)
    ]
    
    # Suppress validity warnings from forward solver to avoid stderr flood
    with suppress_stderr():
        for burst_type, count in configs:
            # Sample log-uniformly
            weights = log_uniform(0.1, 10000.0, count)
            scaled_dists = log_uniform(0.06, 40.0, count)
            
            for i in range(count):
                W = float(weights[i])
                Z = float(scaled_dists[i])
                
                # Derive physical distance: R = Z * W^(1/3)
                R = Z * (W ** (1.0 / 3.0))
                
                # Run the authoritative forward solver (TNT equivalence: factors = 1.0)
                try:
                    calc = BlastCalculatorService.calculate_environment(
                        charge_weight=W,
                        distance=R,
                        burst_type=burst_type,
                        pressure_factor=1.0,
                        impulse_factor=1.0,
                        general_factor=1.0,
                        model="Kingery-Bulmash"
                    )
                    
                    records.append({
                        "burst_type": burst_type,
                        "weight": W,
                        "scaled_distance": Z,
                        "distance": R,
                        "incident_pressure": calc["incident_pressure"],
                        "reflected_pressure": calc["reflected_pressure"],
                        "dynamic_pressure": calc["dynamic_pressure"],
                        "positive_impulse": calc["positive_impulse"],
                        "reflected_impulse": calc["reflected_impulse"],
                        "arrival_time": calc["arrival_time"],
                        "positive_duration": calc["positive_duration"],
                        "shock_front_velocity": calc["shock_front_velocity"],
                        "particle_velocity": calc["particle_velocity"]
                    })
                except Exception as e:
                    # Skip rare failed calculations (should not happen within Z range)
                    continue
                
                # Simple progress logging
                if len(records) % 10000 == 0:
                    # We can print to stdout as it's not redirected
                    sys.stdout.write(f"Processed {len(records)}/{n_samples} samples...\n")
                    sys.stdout.flush()

    df = pd.DataFrame(records)
    return df

def inject_sensor_noise(df, seed=42):
    """
    Injects realistic relative sensor noise:
      - Pressure (incident, reflected, dynamic): ±5%
      - Impulse (incident, reflected): ±3%
      - Arrival Time: ±2%
      - Positive Duration: ±2%
      - Velocity (shock, particle): ±3%
    """
    np.random.seed(seed + 1000)
    df_noisy = df.copy()
    
    noise_config = {
        "incident_pressure": 0.05,
        "reflected_pressure": 0.05,
        "dynamic_pressure": 0.05,
        "positive_impulse": 0.03,
        "reflected_impulse": 0.03,
        "arrival_time": 0.02,
        "positive_duration": 0.02,
        "shock_front_velocity": 0.03,
        "particle_velocity": 0.03
    }
    
    for col, max_noise in noise_config.items():
        if col in df_noisy.columns:
            # Generate uniform noise between -max_noise and +max_noise
            noise = np.random.uniform(-max_noise, max_noise, size=len(df_noisy))
            df_noisy[col] = df_noisy[col] * (1.0 + noise)
            
    return df_noisy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Physics Reference Dataset for Inverse Blast Characterization")
    parser.add_argument("--samples", type=int, default=100000, help="Number of samples to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--out-clean", type=str, default="inverse_dataset_v1.csv", help="Clean dataset filename")
    parser.add_argument("--out-noisy", type=str, default="inverse_dataset_noisy.csv", help="Noisy dataset filename")
    
    args = parser.parse_args()
    
    # 1. Generate clean dataset
    df_clean = generate_samples(args.samples, args.seed)
    df_clean.to_csv(args.out_clean, index=False)
    print(f"Clean dataset saved to: {args.out_clean} ({len(df_clean)} samples)")
    
    # 2. Generate noisy dataset
    df_noisy = inject_sensor_noise(df_clean, args.seed)
    df_noisy.to_csv(args.out_noisy, index=False)
    print(f"Noisy dataset saved to: {args.out_noisy} ({len(df_noisy)} samples)")
