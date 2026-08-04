# 🌍 EcoShield Environmental Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)

**EcoShield** is an advanced, full-stack environmental monitoring and risk management platform. Built for enterprise-scale sustainability tracking, it leverages machine learning (ML), Bayesian statistical models, and real-time geospatial analytics to predict localized pollution risks, enforce compliance, and optimize emission reduction strategies.

Currently tailored for the UAE (with active mock feeds across Dubai, Abu Dhabi, and other emirates), EcoShield projects live sensor data onto interactive vector maps, generates automated compliance reports, and offers deep-dive analytics into site-level environmental impacts.

---

## 🚀 Key Features

*   **Real-time Environmental Dashboard (Earth Pulse):** A dynamic Single Page Application (SPA) offering an interactive globe visualization of global pollution indices and regional signals.
*   **Compliance Leaderboard & Analytics (NEW):** 
    *   Ranks industrial sites by criticality using real-time AI risk assessments.
    *   Visualizes Smoke AQI trends, Predictive Risk Probabilities, and Fleet Carbon Emission Forecasts using dynamic Chart.js integrations.
*   **Geospatial Visualization (Geo Map):** Live mapping of pollution sensors and risk hotspots. The map intelligently scales and converts geographic coordinates (Lat/Lng) to precision SVG vectors.
*   **Advanced Risk Assessment Engine:**
    *   **Machine Learning Models:** Leverages ML algorithms (Scikit-Learn/XGBoost) to compute and forecast site-specific environmental risks based on equipment age, usage, and fuel types.
    *   **Bayesian Risk Analysis:** Employs Bayesian inference to model accurate probabilities of pollution events.
*   **AI Audit Summaries & Recommendations:** Automatically analyzes equipment data to provide eco-replacement recommendations and calculates potential CO2 reduction percentages.
*   **Automated Reporting:** Generates downloadable, on-the-fly PDF reports detailing site risks, historical emissions, and compliance violations.

---

## 🛠️ Technology Stack

**Backend (API & AI):**
*   **Framework:** FastAPI (Python)
*   **Database:** SQLite with SQLAlchemy ORM
*   **Data Science & ML:** Scikit-Learn, SciPy, XGBoost, Pandas, Numpy
*   **Document Generation:** ReportLab (PDFs)

**Frontend (SPA):**
*   **Architecture:** HTML5, Vanilla JavaScript, CSS3
*   **Styling:** Tailwind CSS (configured for custom dark mode themes)
*   **Data Visualization:** Chart.js, Three.js (for 3D globe rendering)
*   **Tooling:** Python build scripts (`build_spa.py`) used to stitch modular HTML templates into the final cohesive web application.

---

## 📁 Project Structure

```text
EcoShield/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models.py            # SQLAlchemy database models
│   │   ├── schemas.py           # Pydantic validation schemas
│   │   ├── database.py          # SQLite connection and session management
│   │   ├── risk_engine.py       # Core logic for risk threshold computations
│   │   ├── bayesian_risk.py     # Bayesian statistical modeling
│   │   ├── ml_risk.py           # ML feature engineering and predictive models
│   │   ├── emission_data.py     # Emission analytics and eco-recommendations
│   │   └── seed.py              # Database seeder for initializing mock data
│   └── requirements.txt         # Backend Python dependencies
├── stitch_ecoshield_pollution_monitor/
│   ├── index.html               # Main frontend SPA entry point
│   ├── shared/                  # Shared CSS, JS, and configuration assets
│   └── ...                      # Modular UI components (Leaderboard, GeoMap, etc.)
├── build_spa.py                 # Custom script to build the frontend SPA
├── README.md                    # Project documentation
└── LICENSE                      # License information
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Shreya5473/EcoSchield.git
cd EcoSchield
```

### 2. Setup the Backend API
Navigate to the backend directory, create a virtual environment, and install the required dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Initialize and seed the database with sample monitoring data:
```bash
python -m app.seed
```

Start the FastAPI development server:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API will be accessible at `http://127.0.0.1:8000`. 
**Note:** You can view the interactive Swagger API documentation at `http://127.0.0.1:8000/docs`.

### 3. Setup the Frontend Dashboard
The frontend does not require a complex Node.js build process. It can be served using Python's built-in static file server.

Open a new terminal window and navigate to the frontend directory:
```bash
cd EcoSchield/stitch_ecoshield_pollution_monitor
```

Start the HTTP server:
```bash
python3 -m http.server 8080
```
Open your web browser and navigate to `http://127.0.0.1:8080` to view the EcoShield Dashboard.

---

## 📡 Core API Endpoints

The backend provides a comprehensive RESTful API. Below are some of the critical endpoints powering the platform:

*   **`GET /api/companies`**: Retrieve all registered companies and their aggregated risk tiers.
*   **`GET /api/companies/{company_id}/sites`**: Get all monitoring sites belonging to a specific company.
*   **`GET /api/sites/{site_id}`**: Fetch detailed sensor data, equipment breakdown, and risk analysis for a site.
*   **`GET /api/leaderboard`**: Retrieve the ranked compliance leaderboard data across all tracked entities.
*   **`GET /api/leaderboard/metrics`**: Fetch aggregated arrays for AQI, risk probability, and emission forecasts to power frontend charting.
*   **`POST /api/ai-summary`**: Dynamically generate AI-driven audit insights based on site conditions.
*   **`GET /api/sites/{site_id}/report.pdf`**: Generate and download a comprehensive compliance PDF report.

---

## 🛡️ License & Disclaimer
This project was built to demonstrate full-stack capabilities combining modern web architecture with artificial intelligence and environmental monitoring. Please refer to the `LICENSE` file for distribution and usage rights.
