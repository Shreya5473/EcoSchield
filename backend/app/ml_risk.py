import numpy as np
import pandas as pd
import xgboost as xgb

def _build_training_data():
    """
    Generate synthetic data for training the XGBoost classifier.
    
    NOTE: This _build_training_data() function should be swapped for a real historical
    database query later when historical production data is available. 
    Nothing else in this file should need to change when that happens.
    """
    np.random.seed(42)
    n_samples = 800
    
    # Features
    avg_co2_per_equipment_hr = np.random.uniform(5.0, 40.0, n_samples)
    pct_diesel_equipment = np.random.uniform(0.0, 1.0, n_samples)
    avg_equipment_age_yrs = np.random.uniform(1.0, 15.0, n_samples)
    total_hours_active_7d = np.random.uniform(10.0, 200.0, n_samples)
    n_overdue_replacements = np.random.randint(0, 10, n_samples)
    
    df = pd.DataFrame({
        "avg_co2_per_equipment_hr": avg_co2_per_equipment_hr,
        "pct_diesel_equipment": pct_diesel_equipment,
        "avg_equipment_age_yrs": avg_equipment_age_yrs,
        "total_hours_active_7d": total_hours_active_7d,
        "n_overdue_replacements": n_overdue_replacements
    })
    
    # Ground truth score using weighted sum + noise
    weights = {
        "avg_co2_per_equipment_hr": 0.4,
        "pct_diesel_equipment": 0.3,
        "avg_equipment_age_yrs": 0.15,
        "total_hours_active_7d": 0.05,
        "n_overdue_replacements": 0.1
    }
    
    # Normalize features for raw score
    raw_score = (
        (df["avg_co2_per_equipment_hr"] / 40.0) * weights["avg_co2_per_equipment_hr"] +
        df["pct_diesel_equipment"] * weights["pct_diesel_equipment"] +
        (df["avg_equipment_age_yrs"] / 15.0) * weights["avg_equipment_age_yrs"] +
        (df["total_hours_active_7d"] / 200.0) * weights["total_hours_active_7d"] +
        (df["n_overdue_replacements"] / 10.0) * weights["n_overdue_replacements"]
    )
    
    # Add noise
    noise = np.random.normal(0, 0.05, n_samples)
    final_score = raw_score + noise
    
    # Threshold into binary labels (e.g. top 30% are high risk)
    threshold = np.percentile(final_score, 70)
    df["label"] = (final_score > threshold).astype(int)
    
    return df

# Global model instance initialized at process startup
_ml_model = None

def _initialize_model():
    global _ml_model
    df = _build_training_data()
    X = df.drop(columns=["label"])
    y = df["label"]
    
    # Train XGBoost classifier
    _ml_model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        # use_label_encoder is deprecated and can be omitted
        eval_metric='logloss',
        random_state=42
    )
    _ml_model.fit(X, y)

# Train the model at startup
_initialize_model()

def ml_risk_probability(features_dict: dict) -> float:
    """
    Returns the predicted probability of high risk for a given site.
    features_dict must contain:
    - avg_co2_per_equipment_hr
    - pct_diesel_equipment
    - avg_equipment_age_yrs
    - total_hours_active_7d
    - n_overdue_replacements
    """
    if _ml_model is None:
        raise RuntimeError("ML model has not been initialized.")
        
    df = pd.DataFrame([features_dict])
    
    # Ensure correct feature order matching training
    feature_cols = [
        "avg_co2_per_equipment_hr", 
        "pct_diesel_equipment", 
        "avg_equipment_age_yrs", 
        "total_hours_active_7d", 
        "n_overdue_replacements"
    ]
    df = df[feature_cols]
    
    # Return probability of positive class (label 1)
    prob = _ml_model.predict_proba(df)[0][1]
    return float(prob)
