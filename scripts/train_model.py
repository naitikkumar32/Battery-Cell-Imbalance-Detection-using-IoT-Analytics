"""
Script: train_model.py
Trains the Isolation Forest model, evaluates on test data, and persists artifacts.
"""

import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ml_pipeline import AnomalyDetector


def main():
    print("=" * 60)
    print("Training Isolation Forest Model for Cell Imbalance Detection...")
    print("=" * 60)

    dataset_path = "datasets/battery_telemetry_dataset.csv"
    detector = AnomalyDetector()

    if os.path.exists(dataset_path):
        print(f"Loading existing dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)
    else:
        print("Dataset not found. Generating fresh dataset...")
        df = detector.generate_synthetic_dataset(n_samples=6000, anomaly_ratio=0.10)
        os.makedirs("datasets", exist_ok=True)
        df.to_csv(dataset_path, index=False)

    metrics = detector.train(df)

    print("\n--- Training Evaluation Metrics ---")
    print(f"Training Samples:   {metrics['train_samples']}")
    print(f"Testing Samples:    {metrics['test_samples']}")
    print(f"Precision:          {metrics['precision']:.4f}")
    print(f"Recall:             {metrics['recall']:.4f}")
    print(f"F1-Score:           {metrics['f1_score']:.4f}")
    print(f"Confusion Matrix:   {metrics['confusion_matrix']}")
    print(f"Saved Model:        {os.path.abspath(metrics['model_path'])}")
    print(f"Saved Scaler:       {os.path.abspath(metrics['scaler_path'])}")
    print("=" * 60)
    print("Model training completed successfully.\n")


if __name__ == "__main__":
    main()
