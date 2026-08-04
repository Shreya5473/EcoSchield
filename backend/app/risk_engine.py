from .bayesian_risk import bayesian_site_score
from .ml_risk import ml_risk_probability

def compute_site_risk(readings: list, threshold: float, ml_features: dict):
    # Bayesian Component
    bayes_result = bayesian_site_score(readings, threshold)
    n_readings = bayes_result["n_readings"]
    bayes_prob = bayes_result["bayesian_risk_prob"]
    
    # ML Component
    ml_prob = ml_risk_probability(ml_features)
    
    # Weighting: Bayesian weight grows with more readings
    bayes_weight = min(0.8, 0.3 + 0.05 * n_readings)
    ml_weight = 1.0 - bayes_weight
    
    final_score = (bayes_prob * bayes_weight) + (ml_prob * ml_weight)
    
    # Tier logic
    if final_score >= 0.70:
        risk_tier = "critical"
    elif final_score >= 0.40:
        risk_tier = "elevated"
    else:
        risk_tier = "nominal"
        
    return {
        "final_risk_score": final_score,
        "risk_tier": risk_tier,
        "breakdown": {
            "bayesian_prob": bayes_prob, "credible_interval_95": bayes_result["credible_interval_95"],
            "bayesian_weight": bayes_weight,
            "ml_prob": ml_prob,
            "ml_weight": ml_weight,
            "n_readings": n_readings
        }
    }
