import math

def bayesian_site_score(readings: list, threshold: float):
    """
    Beta-Binomial adaptive risk model per site.
    readings is a list of numeric CO2 kg values (each an independent trial).
    threshold is the numeric site threshold_co2_kg.
    """
    # Start with Beta(2,2) (weakly informative prior)
    alpha = 2
    beta = 2
    
    # Update per reading
    for reading in readings:
        if reading > threshold:
            alpha += 1
        else:
            beta += 1
            
    # Expose the posterior mean plus a 95% credible interval (normal approximation)
    n = alpha + beta
    mean = alpha / n
    variance = (alpha * beta) / (n ** 2 * (n + 1))
    std_dev = math.sqrt(variance)
    
    # 95% CI normal approximation (z = 1.96)
    margin_error = 1.96 * std_dev
    ci_lower = max(0.0, mean - margin_error)
    ci_upper = min(1.0, mean + margin_error)
    
    return {
        "bayesian_risk_prob": mean,
        "credible_interval_95": (ci_lower, ci_upper),
        "n_readings": len(readings)
    }
