# 🌍 EcoShield Pollution Monitor

EcoShield is a full-stack web application designed for comprehensive environmental monitoring, risk assessment, and emission management. It utilizes machine learning (ML) and Bayesian statistical models to predict localized pollution risks and visualize them on an interactive geographic map. By offering real-time analytics and predictive insights, EcoShield helps stakeholders manage emissions, analyze environmental impact, and make data-driven decisions.

Currently optimized for regions in the UAE (including Dubai and Abu Dhabi), the system projects live environmental data onto interactive vector maps and generates PDF reports on the fly.

## 🚀 Key Features

*   **Real-time Environmental Dashboard:** A dynamic Single Page Application (SPA) providing a comprehensive view of pollution metrics and environmental signals.
*   **Geospatial Visualization:** Live mapping of pollution sensors and risk hotspots using interactive maps. The map intelligently converts Lat/Lng coordinate data to SVG vectors.
*   **Advanced Risk Assessment Engine:**
    *   **Machine Learning Models:** Leverages ML to compute and predict site-specific environmental risks.
    *   **Bayesian Risk Analysis:** Employs Bayesian inference for accurate probability modeling of pollution events.
*   **Emission Recommendations:** Automatically provides mitigation and replacement recommendations based on recorded emission data.
*   **Automated Reporting:** Generates downloadable PDF reports detailing site risks, historical emissions, and compliance metrics.

## 🛠️ Technology Stack

**Backend:**
*   **Framework:** FastAPI (Python)
*   **Database:** SQLite with SQLAlchemy ORM
*   **Data Science & ML:** Scikit-Learn, SciPy
*   **PDF Generation:** ReportLab

**Frontend:**
*   **Architecture:** HTML, CSS, Vanilla JavaScript
*   **Tooling:** Python scripts (`build_spa.py`) to stitch together isolated HTML templates into a cohesive Single Page Application.
*   **Maps:** SVG-based interactive map visualization (`ecoshield_geo_map.html`).

## 📁 Project Structure

```
EcoShield/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models.py            # SQLAlchemy database models
│   │   ├── schemas.py           # Pydantic schemas for data validation
│   │   ├── database.py          # DB connection setup
│   │   ├── risk_engine.py       # Core logic for computing site risks
│   │   ├── bayesian_risk.py     # Bayesian statistical models for risk estimation
│   │   ├── ml_risk.py           # ML predictive models
│   │   ├── emission_data.py     # Emission analysis and recommendations
│   │   └── seed.py              # Database seeding script for sample data
│   └── requirements.txt         # Backend Python dependencies
├── stitch_ecoshield_pollution_monitor/
│   └── ...                      # Frontend modular HTML/JS components and pages
├── build_spa.py                 # Script to build frontend SPA from components
├── update_maps.py               # Map configuration script
├── ecoshield_geo_map.html       # Primary geospatial visualization file
├── index.html                   # Entry point for the frontend SPA
└── README.md                    # Project documentation
```

## ⚙️ Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Shreya5473/EcoSchield.git
cd EcoSchield
```

### 2. Setup the Backend
Navigate to the backend directory, create a virtual environment, and install dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

Initialize and seed the database with sample data:
```bash
python -m app.seed
```

Run the FastAPI development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The backend API will now be running at `http://localhost:8000`. You can view the interactive Swagger API documentation at `http://localhost:8000/docs`.

### 3. Setup the Frontend
The frontend does not require a complex Node.js build process. It can be served using any basic static file server.
In a new terminal window, navigate to the root of the project:
```bash
cd EcoSchield
```
*(Optional)* If you have made changes to the frontend components in `stitch_ecoshield_pollution_monitor/`, rebuild the SPA:
```bash
python build_spa.py
```
Serve the frontend using Python's built-in HTTP server:
```bash
python3 -m http.server 3000
```
Open your browser and navigate to `http://localhost:3000` to view the EcoShield Dashboard.

## 📡 API Documentation
The backend leverages FastAPI's automated OpenAPI generation. Once the backend is running, navigate to `/docs` on your local server to interact with the API endpoints.

Core endpoints include:
*   `GET /`: API Health Check
*   `GET /sites`: Retrieve all registered monitoring sites
*   `POST /risk-analysis`: Trigger ML and Bayesian risk calculations for a specific site
*   `GET /reports/{site_id}`: Download a generated PDF report

## 📄 License
This project is proprietary and built for demonstrating full-stack capabilities in environmental monitoring and AI integration. Please refer to the `LICENSE` file for more details.
