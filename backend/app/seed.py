import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, Base, engine
from app.models import Company, Site, Equipment, EmissionReading
from datetime import datetime, timedelta
import random

# Recreate DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    companies_data = [
        {"name": "Proscape", "sector": "Construction", "lat": 25.2048, "lng": 55.2708, "license_no": "LIC-PROS-001"},
        {"name": "Al Safa Industrial", "sector": "Manufacturing", "lat": 25.1000, "lng": 55.3000, "license_no": "LIC-ALSA-002"},
        {"name": "TechnoCity", "sector": "Infrastructure", "lat": 25.3463, "lng": 55.4209, "license_no": "LIC-TECH-003"}, # Sharjah
        {"name": "Ghantoot", "sector": "Construction", "lat": 24.4539, "lng": 54.3773, "license_no": "LIC-GHAN-004"}, # Abu Dhabi
        {"name": "Suntech", "sector": "Manufacturing", "lat": 25.7895, "lng": 55.9432, "license_no": "LIC-SUNT-005"}, # Ras Al Khaimah
        {"name": "Infranet Corp", "sector": "Energy", "lat": 25.4052, "lng": 55.4396, "license_no": "LIC-INFRA-006"} # Ajman
    ]
    
    emirate_mapping = {
        "Proscape": "Dubai",
        "Al Safa Industrial": "Dubai",
        "TechnoCity": "Sharjah",
        "Ghantoot": "Abu Dhabi",
        "Suntech": "Ras Al Khaimah",
        "Infranet Corp": "Ajman"
    }

    # Create Companies
    for cdata in companies_data:
        comp = Company(
            name=cdata["name"],
            sector=cdata["sector"],
            lat=cdata["lat"],
            lng=cdata["lng"],
            license_no=cdata["license_no"]
        )
        db.add(comp)
        db.commit()
        db.refresh(comp)
        
        # 1-2 Sites per company
        n_sites = random.randint(1, 2)
        for i in range(n_sites):
            # slightly jitter lat/lng for site
            s_lat = cdata["lat"] + random.uniform(-0.02, 0.02)
            s_lng = cdata["lng"] + random.uniform(-0.02, 0.02)
            
            # Trend factor for readings (some bad, some good)
            trend_bad = random.choice([True, False])
            threshold = random.uniform(100.0, 300.0)
            
            site = Site(
                company_id=comp.id,
                name=f"{comp.name} Site {i+1}",
                address=f"Street {random.randint(1,100)}, {emirate_mapping.get(comp.name, 'Dubai')}",
                lat=s_lat,
                lng=s_lng,
                status="Active",
                threshold_co2_kg=threshold
            )
            db.add(site)
            db.commit()
            db.refresh(site)
            
            # Equipment (mix of diesel and electric)
            equip_types = ["diesel_excavator", "electric_excavator", "diesel_generator", "diesel_dump_truck", "hybrid_generator"]
            n_equip = random.randint(3, 6)
            for j in range(n_equip):
                eq_type = random.choice(equip_types)
                eq = Equipment(
                    site_id=site.id,
                    machine_type=eq_type,
                    model=f"Model-{random.randint(1000,9999)}",
                    age_years=random.uniform(1.0, 10.0),
                    hours_active_7d=random.uniform(10.0, 80.0)
                )
                db.add(eq)
            db.commit()
            
            # 21 days of Emission Readings
            now = datetime.utcnow()
            for d in range(21):
                read_date = now - timedelta(days=21-d)
                # base reading relative to threshold
                base = threshold * (1.2 if trend_bad else 0.8)
                daily_co2 = base + random.uniform(-30, 30)
                reading = EmissionReading(
                    site_id=site.id,
                    co2_kg=max(0, daily_co2),
                    recorded_at=read_date
                )
                db.add(reading)
            db.commit()

    db.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed_data()
