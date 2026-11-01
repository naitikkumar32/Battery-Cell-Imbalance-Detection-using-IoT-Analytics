"""
Module: ml_pipeline.py
Machine Learning anomaly detection pipeline for battery cell imbalance and thermal degradation.

Algorithm: Isolation Forest (Scikit-Learn)
Features:
- delta_v_mv: Voltage spread in millivolts
- v_max: Maximum cell voltage
- v_min: Minimum cell voltage
- mean_v: Average cell voltage
- t_max: Maximum cell temperature
- delta_t: Thermal gradient across cells
- current_a: Pack current

Provides:
- Synthetic dataset generation with reproducible seeds
- Preprocessing and feature scaling
- Model training, persistence, and loading
- Performance evaluation metrics (Precision, Recall, F1-Score, Confusion Matrix)
- Robust inference with graceful fallback
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support


FEATURE_COLUMNS = [
    "delta_v_mv",
    "v_max",
    "v_min",
    "mean_v",
    "t_max",
    "delta_t",
    "current_a"
]


class AnomalyDetector:
    def __init__(
        self,
        model_dir: str = "models",
        model_file: str = "isolation_forest_model.joblib",
        scaler_file: str = "scaler.joblib",
        contamination: float = 0.05
    ):
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, model_file)
        self.scaler_path = os.path.join(model_dir, scaler_file)
        self.contamination = contamination

        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_loaded = False

        self.load_model()

    def generate_synthetic_dataset(
        self,
        n_samples: int = 5000,
        anomaly_ratio: float = 0.08,
        random_seed: int = 42
    ) -> pd.DataFrame:
        """
        Generates a physically realistic dataset of battery operation containing
        both nominal balanced samples and anomalous imbalance/thermal events.
        """
        np.random.seed(random_seed)
        n_anomalies = int(n_samples * anomaly_ratio)
        n_normal = n_samples - n_anomalies

        # 1. Normal operating points
        # Nominal lithium cell: 3.6V to 4.15V, very low spread (2 to 15 mV)
        normal_mean_v = np.random.uniform(3.60, 4.10, n_normal)
        normal_spread_mv = np.random.exponential(scale=5.0, size=n_normal) + 2.0
        normal_spread_mv = np.clip(normal_spread_mv, 1.0, 18.0) # below 20mV warning
        normal_delta_v = normal_spread_mv / 1000.0

        normal_v_max = normal_mean_v + (normal_delta_v / 2.0)
        normal_v_min = normal_mean_v - (normal_delta_v / 2.0)

        normal_t_max = np.random.normal(loc=30.0, scale=3.0, size=n_normal)
        normal_t_max = np.clip(normal_t_max, 20.0, 42.0) # below 45C
        normal_delta_t = np.random.exponential(scale=1.0, size=n_normal)
        normal_delta_t = np.clip(normal_delta_t, 0.1, 4.5)

        normal_current = np.random.normal(loc=2.5, scale=0.8, size=n_normal)
        normal_current = np.clip(normal_current, 0.0, 15.0)

        df_normal = pd.DataFrame({
            "delta_v_mv": normal_spread_mv,
            "v_max": normal_v_max,
            "v_min": normal_v_min,
            "mean_v": normal_mean_v,
            "t_max": normal_t_max,
            "delta_t": normal_delta_t,
            "current_a": normal_current,
            "is_anomaly": 0 # Ground truth: 0 = Normal
        })

        # 2. Anomalous points (Severe imbalance, thermal spike, or deep discharge)
        anom_mean_v = np.random.uniform(3.10, 4.15, n_anomalies)
        # High spread: 25 to 120 mV
        anom_spread_mv = np.random.uniform(25.0, 120.0, n_anomalies)
        anom_delta_v = anom_spread_mv / 1000.0

        anom_v_max = anom_mean_v + (anom_delta_v / 2.0)
        anom_v_min = anom_mean_v - (anom_delta_v / 2.0)

        # Some samples exhibit thermal anomalies
        anom_t_max = np.random.choice([
            np.random.normal(32.0, 3.0),
            np.random.uniform(46.0, 75.0)
        ], size=n_anomalies)
        anom_delta_t = np.random.uniform(5.5, 18.0, n_anomalies)
        anom_current = np.random.uniform(1.0, 20.0, n_anomalies)

        df_anomalies = pd.DataFrame({
            "delta_v_mv": anom_spread_mv,
            "v_max": anom_v_max,
            "v_min": anom_v_min,
            "mean_v": anom_mean_v,
            "t_max": anom_t_max,
            "delta_t": anom_delta_t,
            "current_a": anom_current,
            "is_anomaly": 1 # Ground truth: 1 = Anomaly
        })

        df_combined = pd.concat([df_normal, df_anomalies], ignore_index=True)
        # Shuffle dataset
        df_shuffled = df_combined.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
        return df_shuffled

    def train(self, df_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Trains Isolation Forest model and fits StandardScaler.
        Evaluates on held-out test split.
        """
        if df_data is None:
            df_data = self.generate_synthetic_dataset(n_samples=6000, anomaly_ratio=0.10)

        os.makedirs(self.model_dir, exist_ok=True)

        # Train/Test split: 80% train, 20% test
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df_data, test_size=0.20, random_state=42, stratify=df_data["is_anomaly"])

        # Train primarily on normal data for semi-supervised / unsupervised anomaly detection
        x_train_raw = train_df[train_df["is_anomaly"] == 0][FEATURE_COLUMNS]

        self.scaler = StandardScaler()
        x_train_scaled = self.scaler.fit_transform(x_train_raw)

        self.model = IsolationForest(
            n_estimators=150,
            contamination=self.contamination,
            max_samples="auto",
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(x_train_scaled)

        # Evaluate on test set
        x_test_raw = test_df[FEATURE_COLUMNS]
        y_test_true = test_df["is_anomaly"].values

        x_test_scaled = self.scaler.transform(x_test_raw)
        raw_preds = self.model.predict(x_test_scaled)
        # Isolation Forest outputs 1 for inlier (normal), -1 for outlier (anomaly)
        # Convert to binary: 0 = normal, 1 = anomaly
        y_test_pred = np.where(raw_preds == -1, 1, 0)

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test_true, y_test_pred, average="binary", zero_division=0
        )
        cm = confusion_matrix(y_test_true, y_test_pred).tolist()

        # Save model and scaler
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        self.is_loaded = True

        metrics = {
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "confusion_matrix": cm,
            "features_used": FEATURE_COLUMNS,
            "model_path": self.model_path,
            "scaler_path": self.scaler_path
        }
        return metrics

    def load_model(self) -> bool:
        """Loads trained Isolation Forest and scaler if available."""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_loaded = True
                return True
            except Exception:
                self.is_loaded = False
        self.is_loaded = False
        return False

    def predict(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs inference on a single reading feature dictionary.
        Returns:
          {
            "is_anomaly": bool,
            "anomaly_score": float, # Continuous score: higher means more anomalous
            "status": "ANOMALY" | "NORMAL",
            "model_active": bool
          }
        """
        if not self.is_loaded or self.model is None or self.scaler is None:
            # Fallback when model is not trained/loaded
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "status": "NORMAL (RULE-BASED FALLBACK)",
                "model_active": False,
                "error": "ML model not loaded; using rule-based fallback."
            }

        try:
            # Extract feature vector
            vector = []
            for col in FEATURE_COLUMNS:
                val = feature_dict.get(col)
                if val is None:
                    # Missing feature
                    return {
                        "is_anomaly": False,
                        "anomaly_score": 0.0,
                        "status": "UNKNOWN (FEATURE MISSING)",
                        "model_active": True,
                        "error": f"Missing required feature '{col}'"
                    }
                vector.append(float(val))

            arr = np.array([vector])
            arr_scaled = self.scaler.transform(arr)

            pred_raw = self.model.predict(arr_scaled)[0] # 1 = inlier, -1 = outlier
            # decision_function: lower score = more abnormal
            dec_score = self.model.decision_function(arr_scaled)[0]
            # Invert and normalize score so higher score (0 to 1+) means higher abnormality
            normalized_anomaly_score = round(float(-dec_score), 4)

            is_anomaly = bool(pred_raw == -1)

            return {
                "is_anomaly": is_anomaly,
                "anomaly_score": normalized_anomaly_score,
                "status": "ANOMALOUS" if is_anomaly else "NORMAL",
                "model_active": True,
                "error": None
            }
        except Exception as e:
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "status": "ERROR (FALLBACK)",
                "model_active": False,
                "error": str(e)
            }
