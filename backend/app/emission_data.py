EMISSION_FACTORS = {
    "diesel_excavator": {"co2_kg_hr": 20.5, "nox_kg_hr": 0.15, "pm25_kg_hr": 0.015, "fuel_type": "diesel"},
    "electric_excavator": {"co2_kg_hr": 0.0, "nox_kg_hr": 0.0, "pm25_kg_hr": 0.0, "fuel_type": "electric"},
    "diesel_bulldozer": {"co2_kg_hr": 25.0, "nox_kg_hr": 0.18, "pm25_kg_hr": 0.02, "fuel_type": "diesel"},
    "hybrid_bulldozer": {"co2_kg_hr": 15.0, "nox_kg_hr": 0.09, "pm25_kg_hr": 0.01, "fuel_type": "hybrid"},
    "diesel_crane": {"co2_kg_hr": 18.0, "nox_kg_hr": 0.12, "pm25_kg_hr": 0.012, "fuel_type": "diesel"},
    "electric_crane": {"co2_kg_hr": 0.0, "nox_kg_hr": 0.0, "pm25_kg_hr": 0.0, "fuel_type": "electric"},
    "diesel_generator": {"co2_kg_hr": 30.0, "nox_kg_hr": 0.25, "pm25_kg_hr": 0.025, "fuel_type": "diesel"},
    "hybrid_generator": {"co2_kg_hr": 12.0, "nox_kg_hr": 0.08, "pm25_kg_hr": 0.005, "fuel_type": "hybrid"},
    "diesel_dump_truck": {"co2_kg_hr": 22.0, "nox_kg_hr": 0.16, "pm25_kg_hr": 0.018, "fuel_type": "diesel"},
    "electric_dump_truck": {"co2_kg_hr": 0.0, "nox_kg_hr": 0.0, "pm25_kg_hr": 0.0, "fuel_type": "electric"},
    "diesel_concrete_mixer": {"co2_kg_hr": 19.5, "nox_kg_hr": 0.14, "pm25_kg_hr": 0.014, "fuel_type": "diesel"},
    "electric_concrete_mixer": {"co2_kg_hr": 0.0, "nox_kg_hr": 0.0, "pm25_kg_hr": 0.0, "fuel_type": "electric"},
}

REPLACEMENT_MAP = {
    "diesel_excavator": "electric_excavator",
    "diesel_bulldozer": "hybrid_bulldozer",
    "diesel_crane": "electric_crane",
    "diesel_generator": "hybrid_generator",
    "diesel_dump_truck": "electric_dump_truck",
    "diesel_concrete_mixer": "electric_concrete_mixer"
}

def calculate_emissions(machine_type: str, hours_active: float):
    factor = EMISSION_FACTORS.get(machine_type)
    if not factor:
        return None
    return {
        "co2_kg": factor["co2_kg_hr"] * hours_active,
        "nox_kg": factor["nox_kg_hr"] * hours_active,
        "pm25_kg": factor["pm25_kg_hr"] * hours_active
    }

def get_replacement_recommendation(machine_type: str, hours_active: float):
    if machine_type not in REPLACEMENT_MAP:
        return None
    
    cleaner_type = REPLACEMENT_MAP[machine_type]
    current_emissions = calculate_emissions(machine_type, hours_active)
    cleaner_emissions = calculate_emissions(cleaner_type, hours_active)
    
    if not current_emissions or not cleaner_emissions:
        return None
    
    current_co2 = current_emissions["co2_kg"]
    cleaner_co2 = cleaner_emissions["co2_kg"]
    
    co2_savings = current_co2 - cleaner_co2
    co2_reduction_pct = (co2_savings / current_co2 * 100) if current_co2 > 0 else 0.0
    
    return {
        "recommended_alternative": cleaner_type,
        "co2_savings_kg": co2_savings,
        "co2_reduction_pct": co2_reduction_pct
    }
