"""
Tests: test_ml_pipeline.py
Validates ML synthetic data generation, training, inference, and fallback behavior.
"""

import os
import shutil
import tempfile
import pytest
from src.ml_pipeline import AnomalyDetector


@pytest.fixture
def temp_ml_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_dataset_generation(temp_ml_dir):
    det = AnomalyDetector(model_dir=temp_ml_dir)
    df = det.generate_synthetic_dataset(n_samples=500, anomaly_ratio=0.10, random_seed=42)

    assert len(df) == 500
    assert "is_anomaly" in df.columns
    assert "delta_v_mv" in df.columns
    # Check that both classes exist
    assert 1 in df["is_anomaly"].values
    assert 0 in df["is_anomaly"].values


def test_training_and_inference(temp_ml_dir):
    det = AnomalyDetector(model_dir=temp_ml_dir)
    df = det.generate_synthetic_dataset(n_samples=600, anomaly_ratio=0.10, random_seed=42)
    metrics = det.train(df)

    assert metrics["f1_score"] >= 0.50
    assert os.path.exists(det.model_path)
    assert os.path.exists(det.scaler_path)
    assert det.is_loaded is True

    # Test inference on a healthy sample
    normal_sample = {
        "delta_v_mv": 5.0,
        "v_max": 3.82,
        "v_min": 3.815,
        "mean_v": 3.817,
        "t_max": 28.0,
        "delta_t": 0.5,
        "current_a": 2.0
    }
    pred_normal = det.predict(normal_sample)
    assert pred_normal["model_active"] is True
    assert pred_normal["is_anomaly"] is False

    # Test inference on an anomalous sample (massive spread and heat)
    anom_sample = {
        "delta_v_mv": 95.0,
        "v_max": 4.10,
        "v_min": 3.20,
        "mean_v": 3.65,
        "t_max": 68.0,
        "delta_t": 16.0,
        "current_a": 12.0
    }
    pred_anom = det.predict(anom_sample)
    assert pred_anom["model_active"] is True
    assert pred_anom["is_anomaly"] is True


def test_fallback_when_model_missing():
    # Model in non-existent directory
    det = AnomalyDetector(model_dir="non_existent_folder_xyz")
    assert det.is_loaded is False

    sample = {"delta_v_mv": 10.0}
    res = det.predict(sample)
    assert res["model_active"] is False
    assert "fallback" in res["status"].lower()
