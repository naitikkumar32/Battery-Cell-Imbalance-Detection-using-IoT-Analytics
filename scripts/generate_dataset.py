"""
Script: generate_dataset.py
Generates a reproducible dataset of battery cell operations for machine learning training.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ml_pipeline import AnomalyDetector


def main():
    print("=" * 60)
    print("Generating Synthetic Battery Dataset for ML Training...")
    print("=" * 60)

    detector = AnomalyDetector()
    dataset_dir = "datasets"
    os.makedirs(dataset_dir, exist_ok=True)
    dataset_path = os.path.join(dataset_dir, "battery_telemetry_dataset.csv")

    df = detector.generate_synthetic_dataset(n_samples=6000, anomaly_ratio=0.10, random_seed=42)
    df.to_csv(dataset_path, index=False)

    print(f"[OK] Generated {len(df)} samples ({df['is_anomaly'].sum()} anomalies).")
    print(f"[OK] Saved dataset to: {os.path.abspath(dataset_path)}\n")


if __name__ == "__main__":
    main()
