from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sector = Column(String)
    license_no = Column(String, unique=True, index=True)
    lat = Column(Float)
    lng = Column(Float)

    sites = relationship("Site", back_populates="company")
    fines = relationship("Fine", back_populates="company")

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String, index=True)
    address = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String)
    threshold_co2_kg = Column(Float)

    company = relationship("Company", back_populates="sites")
    equipment = relationship("Equipment", back_populates="site")
    emission_readings = relationship("EmissionReading", back_populates="site")
    fines = relationship("Fine", back_populates="site")

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    machine_type = Column(String)
    model = Column(String)
    age_years = Column(Float)
    hours_active_7d = Column(Float)

    site = relationship("Site", back_populates="equipment")

class EmissionReading(Base):
    __tablename__ = "emission_readings"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    co2_kg = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="emission_readings")

class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    site_id = Column(Integer, ForeignKey("sites.id"))
    reason = Column(String)
    amount_aed = Column(Float)
    status = Column(String)
    issued_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="fines")
    site = relationship("Site", back_populates="fines")
