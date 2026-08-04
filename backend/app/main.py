from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models, schemas
from .risk_engine import compute_site_risk
from .emission_data import get_replacement_recommendation
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from datetime import datetime
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EcoShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "EcoShield Backend API is running successfully. Please visit /docs for Swagger UI documentation."}

def lat_lng_to_xy(lat: float, lng: float):
    # Simple linear projection to fit the frontend SVG viewBox
    # Dubai: lat=25.2, lng=55.27 => x=780, y=270
    # Abu Dhabi: lat=24.45, lng=54.37 => x=530, y=540
    # dy/dlat = (270 - 540) / (25.2 - 24.45) = -270 / 0.75 = -360
    # y = -360 * lat + d => 270 = -360 * 25.2 + d => d = 9342
    # y = -360 * lat + 9342
    # dx/dlng = (780 - 530) / (55.27 - 54.37) = 250 / 0.9 = 277.7
    # x = 277.7 * lng + c => 780 = 277.7 * 55.27 + c => c = -14568
    # x = 277.7 * lng - 14568
    x = int(277.7 * lng - 14568)
    y = int(-360 * lat + 9342)
    return x, y

def get_emirate_from_address(address: str, default_emirate="Dubai"):
    emirates = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]
    for e in emirates:
        if e in address:
            return e
    return default_emirate

def evaluate_site_risk(db: Session, site: models.Site):
    # Gather readings
    readings = [r.co2_kg for r in site.emission_readings]
    
    # Gather ML features
    equipments = site.equipment
    n_equip = len(equipments)
    if n_equip > 0:
        diesel_count = sum(1 for e in equipments if "diesel" in e.machine_type)
        pct_diesel = diesel_count / n_equip
        avg_age = sum(e.age_years for e in equipments) / n_equip
        total_hours = sum(e.hours_active_7d for e in equipments)
        
        # approximate avg_co2_per_equipment_hr (using threshold as baseline here for mock)
        avg_co2 = sum(r.co2_kg for r in site.emission_readings[-7:]) / (total_hours + 1) if site.emission_readings else 0
        n_overdue = sum(1 for e in equipments if e.age_years > 8)
    else:
        pct_diesel = 0.0
        avg_age = 0.0
        total_hours = 0.0
        avg_co2 = 0.0
        n_overdue = 0
        
    ml_features = {
        "avg_co2_per_equipment_hr": avg_co2,
        "pct_diesel_equipment": pct_diesel,
        "avg_equipment_age_yrs": avg_age,
        "total_hours_active_7d": total_hours,
        "n_overdue_replacements": n_overdue
    }
    
    return compute_site_risk(readings, site.threshold_co2_kg, ml_features)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/companies")
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    results = []
    
    for comp in companies:
        worst_tier = "nominal"
        worst_score = 0
        emirate = "Dubai"
        
        if comp.sites:
            emirate = get_emirate_from_address(comp.sites[0].address, default_emirate="Dubai")
            for site in comp.sites:
                risk_data = evaluate_site_risk(db, site)
                if risk_data["final_risk_score"] > worst_score:
                    worst_score = risk_data["final_risk_score"]
                    worst_tier = risk_data["risk_tier"]
        
        x, y = lat_lng_to_xy(comp.lat, comp.lng)
        
        results.append({
            "id": comp.id,
            "name": comp.name,
            "emirate": emirate,
            "lat": comp.lat,
            "lng": comp.lng,
            "x": x,
            "y": y,
            "risk": worst_tier,
            "sector": comp.sector,
            "risk_score": worst_score
        })
    return results

@app.get("/api/companies/{company_id}/sites")
def get_company_sites(company_id: int, db: Session = Depends(get_db)):
    sites = db.query(models.Site).filter(models.Site.company_id == company_id).all()
    res = []
    for site in sites:
        risk_data = evaluate_site_risk(db, site)
        x, y = lat_lng_to_xy(site.lat, site.lng)
        res.append({
            "id": site.id,
            "name": site.name,
            "address": site.address,
            "x": x,
            "y": y,
            "risk_score": risk_data["final_risk_score"],
            "risk_tier": risk_data["risk_tier"]
        })
    return res

@app.get("/api/sites/{site_id}")
def get_site_details(site_id: int, db: Session = Depends(get_db)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    risk_data = evaluate_site_risk(db, site)
    
    equipments = []
    for eq in site.equipment:
        rec = get_replacement_recommendation(eq.machine_type, eq.hours_active_7d)
        equipments.append({
            "id": eq.id,
            "machine_type": eq.machine_type,
            "model": eq.model,
            "age_years": eq.age_years,
            "hours_active_7d": eq.hours_active_7d,
            "replacement_rec": rec
        })
        
    emissions = [{"co2_kg": r.co2_kg, "recorded_at": r.recorded_at} for r in site.emission_readings]
    
    return {
        "id": site.id,
        "name": site.name,
        "address": site.address,
        "threshold_co2_kg": site.threshold_co2_kg,
        "risk_breakdown": risk_data,
        "equipment": equipments,
        "emissions": emissions
    }

@app.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    sites = db.query(models.Site).all()
    res = []
    for site in sites:
        risk_data = evaluate_site_risk(db, site)
        res.append({
            "site_id": site.id,
            "site_name": site.name,
            "company_name": site.company.name,
            "risk_score": risk_data["final_risk_score"],
            "risk_tier": risk_data["risk_tier"]
        })
    res.sort(key=lambda x: x["risk_score"], reverse=True)
    return res

@app.post("/api/sites/{site_id}/fine")
def issue_fine(site_id: int, fine: schemas.FineCreate, db: Session = Depends(get_db)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    new_fine = models.Fine(
        company_id=site.company_id,
        site_id=site.id,
        reason=fine.reason,
        amount_aed=fine.amount_aed,
        status="Issued",
        issued_at=datetime.utcnow()
    )
    db.add(new_fine)
    db.commit()
    db.refresh(new_fine)
    return new_fine

@app.get("/api/companies/{company_id}/fines")
def get_fines(company_id: int, db: Session = Depends(get_db)):
    fines = db.query(models.Fine).filter(models.Fine.company_id == company_id).all()
    return fines

@app.get("/api/sites/{site_id}/report.pdf")
def generate_report(site_id: int, db: Session = Depends(get_db)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    risk_data = evaluate_site_risk(db, site)
    
    file_path = f"/tmp/report_site_{site_id}.pdf"
    c = canvas.Canvas(file_path)
    c.drawString(100, 800, f"EcoShield Site Report: {site.name}")
    c.drawString(100, 780, f"Address: {site.address}")
    c.drawString(100, 760, f"Risk Tier: {risk_data['risk_tier'].upper()} (Score: {risk_data['final_risk_score']:.2f})")
    
    y = 730
    c.drawString(100, y, "Equipment & Replacement Recommendations:")
    y -= 20
    for eq in site.equipment:
        c.drawString(110, y, f"- {eq.machine_type} ({eq.hours_active_7d} hrs/7d)")
        rec = get_replacement_recommendation(eq.machine_type, eq.hours_active_7d)
        if rec:
            y -= 15
            c.drawString(130, y, f"Rec: Swap to {rec['recommended_alternative']} for {rec['co2_reduction_pct']:.1f}% savings")
        y -= 20
        if y < 100:
            c.showPage()
            y = 800
            
    c.save()
    return FileResponse(file_path, filename=f"{site.name}_report.pdf")

@app.post("/api/ai-summary")
def get_ai_summary(req: schemas.AiSummaryRequest, db: Session = Depends(get_db)):
    site_obj = db.query(models.Site).filter(models.Site.name.ilike(f"%{req.site}%")).first()
    
    ml_bayes_text = ""
    if site_obj:
        risk_data = evaluate_site_risk(db, site_obj)
        ml_prob = risk_data["breakdown"]["ml_prob"]
        bayes_prob = risk_data["breakdown"]["bayesian_prob"]
        ml_bayes_text = (
            f"Advanced ML predicts a {ml_prob:.1%} high-risk probability, "
            f"while our Bayesian model indicates {bayes_prob:.1%} based on historical readings. "
        )

    top_machine = req.machines[0] if req.machines else {}
    machine_name = top_machine.get("name", "Tier-2 excavator")
    machine_risk = top_machine.get("risk", "97%")
    
    summary = (
        f"{req.site} is emitting significantly high NOx and PM2.5, driven primarily by an aging "
        f"{machine_name} (Risk: {machine_risk}). "
        f"{ml_bayes_text}"
        f"Adopting the {req.flaggedReplacements} flagged replacements would cut site carbon footprint and avoid future fines."
    )
    return {"summary": summary}
