# PRD za HealthEquiRoute.

Početna arhitektura će biti modularni monolit, što će omogućiti brzu implementaciju MVP-a.

---

## 1. High-Level Architecture Design

### Preporučeni Arhitekturni Obrazac: **Modular Monolith → Microservices Ready**

Za ovaj projekat preporučujem **modularni monolit** kao početnu arhitekturu sa jasnom separacijom koja omogućava buduću migraciju na mikroservise. Evo zašto:

| Kriterijum | Monolith | Microservices | **Modular Monolith** ✓ |
|------------|----------|---------------|------------------------|
| Brzina razvoja (MVP) | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| Operativna kompleksnost | Niska | Visoka | Niska |
| Skalabilnost | Ograničena | Odlična | Dobra (vertikalna + horizontalna za kritične module) |
| Tim veličina potrebna | Mali | Veliki | Mali-srednji |
| NHS Compliance audit | Lakši | Kompleksniji | Lakši |

---

### C4 Model - System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SYSTEMS                                        │
├─────────────┬─────────────┬─────────────┬─────────────────┬─────────────────────────┤
│ NHS Digital │  ONS Data   │  Ordnance   │  GP Practice    │   Google Cloud AI       │
│ (QOF, HES)  │(Census,IMD) │   Survey    │    Systems      │  (Gemini API, Vertex)   │
└──────┬──────┴──────┬──────┴──────┬──────┴────────┬────────┴─────────┬───────────────┘
       │             │             │               │                  │
       ▼             ▼             ▼               ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           HealthEquiRoute Platform                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                            API Gateway / BFF                                │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│       │              │                │                  │                │         │
│       ▼              ▼                ▼                  ▼                ▼         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   Data   │  │   DEX    │  │  VRP Router  │  │   AI/ML      │  │  LLM Chat   │  │
│  │  Module  │──│  Engine  │──│ Optimization │──│ Intelligence │──│   Assistant │  │
│  │(Ingest & │  │(Decision)│  │  (OR-Tools)  │  │ (Prediction) │  │(Gemini API) │  │
│  │Transform)│  │          │  │              │  │              │  │             │  │
│  └──────────┘  └──────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
│       │              │                │                  │                │         │
│       └──────────────┴────────────────┴──────────────────┴────────────────┘         │
│                                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │              Shared Data Layer (Cloud SQL PostgreSQL + PostGIS)             │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
       │                    │                      │                    │
       ▼                    ▼                      ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐
│ Strategic       │  │ Operations      │  │ Field Worker    │  │ AI Chat      │
│ Planner         │  │ Manager         │  │ (Mobile)        │  │ Interface    │
│ (Web Dashboard) │  │ (Web App)       │  │ (PWA/App)       │  │ (Insights)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └──────────────┘
```

---

### Predloženi Tech Stack

| Layer | Tehnologija | Obrazloženje |
|-------|-------------|--------------|
| **Backend API** | Python (FastAPI) | Odličan za ML/AI integraciju, async, auto-dokumentacija |
| **DEX Engine** | Python + NumPy/Pandas | Prirodan izbor za decision logic, laka integracija sa Data Science |
| **VRP Router** | Google OR-Tools | Industrijki standard za vehicle routing, open-source |
| **ML/AI Models** | scikit-learn + TensorFlow | Predictive analytics, risk stratification |
| **LLM Integration** | Kimi-K2 Thinking Turbo API | Natural language insights, policy recommendations |
| **Database** | PostgreSQL + PostGIS | Geospatial podrška, NHS-compliant |
| **Cache** | Redis | Session management, route caching |
| **Frontend** | Vite + React + TypeScript | Brz development, hot reload, modern tooling |
| **Maps** | MapLibre GL JS (open-source) | Heatmaps, custom styling, no vendor lock-in |
| **Mobile** | PWA | Offline capability, cross-platform |
| **Authentication** | JWT + Google OAuth 2.0 | Local accounts + Google Sign-In |
| **Infrastructure** | Hetzner (Docker) | EU hosting, GDPR compliant, cost-effective |
| **Message Queue** | Celery + Redis | Async job processing za route generation i ML inference |
| **Deployment** | Docker Compose + Nginx | Simple deployment, easy scaling |

---

## 2. Database Schema Design

Evo detaljnog ER dijagrama i schema:

```sql
-- ============================================
-- HEALTHEQUIROUTE DATABASE SCHEMA v1.0
-- ============================================

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- GEOGRAPHIC & REFERENCE DATA
-- ============================================

-- LSOA (Lower Layer Super Output Area) - Core geographic unit
CREATE TABLE lsoa (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lsoa_code VARCHAR(20) UNIQUE NOT NULL,  -- e.g., E01000001
    lsoa_name VARCHAR(255) NOT NULL,
    local_authority_code VARCHAR(10),
    local_authority_name VARCHAR(255),
    icb_code VARCHAR(10),  -- Integrated Care Board
    icb_name VARCHAR(255),
    geometry GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,  -- British National Grid
    centroid GEOMETRY(POINT, 4326),
    area_hectares DECIMAL(12, 4),
    population_2021 INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lsoa_geometry ON lsoa USING GIST (geometry);
CREATE INDEX idx_lsoa_code ON lsoa(lsoa_code);
CREATE INDEX idx_lsoa_icb ON lsoa(icb_code);

-- ============================================
-- DEPRIVATION & SOCIAL DATA (IMD)
-- ============================================

CREATE TABLE imd_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lsoa_id UUID REFERENCES lsoa(id) ON DELETE CASCADE,
    data_year INTEGER NOT NULL,  -- 2019 (latest IMD)
    
    -- Overall IMD
    imd_rank INTEGER,  -- 1 = most deprived
    imd_decile SMALLINT CHECK (imd_decile BETWEEN 1 AND 10),
    imd_score DECIMAL(8, 4),
    
    -- Domain Scores (for detailed analysis)
    income_score DECIMAL(8, 4),
    employment_score DECIMAL(8, 4),
    education_score DECIMAL(8, 4),
    health_score DECIMAL(8, 4),
    crime_score DECIMAL(8, 4),
    housing_score DECIMAL(8, 4),
    environment_score DECIMAL(8, 4),
    
    -- Derived flags
    is_core20 BOOLEAN GENERATED ALWAYS AS (imd_decile <= 2) STORED,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(lsoa_id, data_year)
);

CREATE INDEX idx_imd_lsoa ON imd_data(lsoa_id);
CREATE INDEX idx_imd_decile ON imd_data(imd_decile);
CREATE INDEX idx_imd_core20 ON imd_data(is_core20) WHERE is_core20 = TRUE;

-- ============================================
-- DEMOGRAPHIC DATA (Census 2021)
-- ============================================

CREATE TABLE demographic_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lsoa_id UUID REFERENCES lsoa(id) ON DELETE CASCADE,
    data_year INTEGER NOT NULL,  -- 2021
    
    -- Population breakdown
    total_population INTEGER,
    population_0_17 INTEGER,
    population_18_64 INTEGER,
    population_65_plus INTEGER,
    
    -- Ethnicity (ONS categories)
    pct_white DECIMAL(5, 2),
    pct_asian DECIMAL(5, 2),
    pct_black DECIMAL(5, 2),
    pct_mixed DECIMAL(5, 2),
    pct_other DECIMAL(5, 2),
    pct_minority DECIMAL(5, 2) GENERATED ALWAYS AS (100 - COALESCE(pct_white, 0)) STORED,
    
    -- Language
    pct_english_not_main DECIMAL(5, 2),
    pct_no_english DECIMAL(5, 2),
    
    -- Household
    pct_no_car_household DECIMAL(5, 2),
    pct_single_parent DECIMAL(5, 2),
    pct_lone_pensioner DECIMAL(5, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(lsoa_id, data_year)
);

CREATE INDEX idx_demo_lsoa ON demographic_data(lsoa_id);

-- ============================================
-- CLINICAL / HEALTH DATA (QOF)
-- ============================================

CREATE TABLE clinical_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lsoa_id UUID REFERENCES lsoa(id) ON DELETE CASCADE,
    gp_practice_code VARCHAR(10),
    data_period VARCHAR(20),  -- e.g., "2023-Q4"
    
    -- Disease prevalence (per 1000 population)
    diabetes_prevalence DECIMAL(6, 2),
    hypertension_prevalence DECIMAL(6, 2),
    copd_prevalence DECIMAL(6, 2),
    asthma_prevalence DECIMAL(6, 2),
    chd_prevalence DECIMAL(6, 2),  -- Coronary Heart Disease
    stroke_prevalence DECIMAL(6, 2),
    cancer_prevalence DECIMAL(6, 2),
    mental_health_prevalence DECIMAL(6, 2),
    dementia_prevalence DECIMAL(6, 2),
    
    -- Utilization metrics
    emergency_admissions_rate DECIMAL(8, 2),
    a_and_e_attendance_rate DECIMAL(8, 2),
    
    -- Derived: Composite clinical risk score (calculated)
    clinical_risk_score DECIMAL(5, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_clinical_lsoa ON clinical_data(lsoa_id);
CREATE INDEX idx_clinical_period ON clinical_data(data_period);

-- ============================================
-- ACCESSIBILITY DATA
-- ============================================

CREATE TABLE accessibility_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lsoa_id UUID REFERENCES lsoa(id) ON DELETE CASCADE,
    
    -- Travel times (minutes)
    time_to_nearest_gp INTEGER,
    time_to_nearest_hospital INTEGER,
    time_to_nearest_pharmacy INTEGER,
    
    -- Public transport accessibility
    public_transport_accessibility_score DECIMAL(5, 2),  -- 0-100
    
    -- Distance (km)
    distance_to_nearest_gp DECIMAL(8, 2),
    distance_to_nearest_hospital DECIMAL(8, 2),
    
    -- Derived category
    access_category VARCHAR(20) GENERATED ALWAYS AS (
        CASE 
            WHEN time_to_nearest_gp > 30 OR distance_to_nearest_hospital > 20 THEN 'POOR'
            WHEN time_to_nearest_gp > 15 OR distance_to_nearest_hospital > 10 THEN 'MODERATE'
            ELSE 'GOOD'
        END
    ) STORED,
    
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_access_lsoa ON accessibility_data(lsoa_id);

-- ============================================
-- DEX ENGINE RESULTS
-- ============================================

CREATE TABLE dex_priority_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lsoa_id UUID REFERENCES lsoa(id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL,
    model_version VARCHAR(20) NOT NULL,  -- e.g., "v1.2"
    
    -- Component scores (0-100)
    clinical_risk_score DECIMAL(5, 2) NOT NULL,
    social_vulnerability_score DECIMAL(5, 2) NOT NULL,
    accessibility_score DECIMAL(5, 2) NOT NULL,
    
    -- Final priority
    priority_score DECIMAL(5, 2) NOT NULL,  -- 0-100
    priority_label VARCHAR(20) NOT NULL,  -- URGENT, HIGH, MEDIUM, ROUTINE
    
    -- Explainability
    explanation_text TEXT NOT NULL,
    contributing_factors JSONB,  -- Detailed breakdown
    
    -- Flags
    requires_translator BOOLEAN DEFAULT FALSE,
    requires_specialist BOOLEAN DEFAULT FALSE,
    min_visit_time_minutes INTEGER DEFAULT 15,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,  -- User who triggered recalculation
    
    UNIQUE(lsoa_id, calculation_date, model_version)
);

CREATE INDEX idx_dex_lsoa ON dex_priority_scores(lsoa_id);
CREATE INDEX idx_dex_priority ON dex_priority_scores(priority_score DESC);
CREATE INDEX idx_dex_label ON dex_priority_scores(priority_label);
CREATE INDEX idx_dex_date ON dex_priority_scores(calculation_date);

-- ============================================
-- DEX MODEL CONFIGURATION
-- ============================================

CREATE TABLE dex_model_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version VARCHAR(20) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    
    -- Weight configuration
    clinical_weight DECIMAL(4, 2) DEFAULT 0.40,
    social_weight DECIMAL(4, 2) DEFAULT 0.35,
    accessibility_weight DECIMAL(4, 2) DEFAULT 0.25,
    
    -- Rule definitions (stored as JSON for flexibility)
    fuzzy_rules JSONB NOT NULL,
    aggregation_rules JSONB NOT NULL,
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,
    approved_at TIMESTAMPTZ,
    approved_by UUID,
    
    CONSTRAINT weights_sum_to_one CHECK (
        clinical_weight + social_weight + accessibility_weight BETWEEN 0.99 AND 1.01
    )
);

-- ============================================
-- ORGANIZATIONS & TEAMS
-- ============================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(50) NOT NULL,  -- NHS_TRUST, ICB, LOCAL_AUTHORITY, PCN
    ods_code VARCHAR(10) UNIQUE,  -- NHS ODS Code
    coverage_area GEOMETRY(MULTIPOLYGON, 4326),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    team_type VARCHAR(50),  -- DISTRICT_NURSING, HEALTH_VISITING, COMMUNITY_MATRON
    base_location GEOMETRY(POINT, 4326),
    working_hours JSONB,  -- {"mon": {"start": "08:00", "end": "18:00"}, ...}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL if using NHS SSO
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- ADMIN, PLANNER, MANAGER, FIELD_WORKER
    organization_id UUID REFERENCES organizations(id),
    team_id UUID REFERENCES teams(id),
    
    -- NHS Identity
    nhs_smartcard_id VARCHAR(50),
    
    -- Preferences
    preferences JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- RESOURCES (Vehicles/Workers)
-- ============================================

CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,  -- VEHICLE, NURSE, HEALTH_VISITOR
    name VARCHAR(255) NOT NULL,
    
    -- Capacity
    max_visits_per_day INTEGER DEFAULT 15,
    skills JSONB DEFAULT '[]',  -- ["DIABETES_SPECIALIST", "PAEDIATRIC", "TRANSLATOR_URDU"]
    
    -- Location
    start_location GEOMETRY(POINT, 4326),
    end_location GEOMETRY(POINT, 4326),  -- NULL = return to start
    
    -- Availability
    working_hours JSONB,
    is_available BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- VISIT LOCATIONS (Points to visit)
-- ============================================

CREATE TABLE visit_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lsoa_id UUID REFERENCES lsoa(id),
    organization_id UUID REFERENCES organizations(id),
    
    -- Location details
    name VARCHAR(255),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    postcode VARCHAR(10) NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL,
    
    -- Visit requirements
    location_type VARCHAR(50),  -- PATIENT_HOME, COMMUNITY_CENTER, CARE_HOME
    required_skills JSONB DEFAULT '[]',
    estimated_duration_minutes INTEGER DEFAULT 30,
    time_windows JSONB,  -- [{"start": "09:00", "end": "12:00"}]
    
    -- Priority (from DEX or manual override)
    priority_override INTEGER,  -- NULL = use DEX score
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_visit_loc_geo ON visit_locations USING GIST (location);
CREATE INDEX idx_visit_loc_lsoa ON visit_locations(lsoa_id);

-- ============================================
-- ROUTES & SCHEDULES
-- ============================================

CREATE TABLE route_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id),
    team_id UUID REFERENCES teams(id),
    plan_date DATE NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'DRAFT',  -- DRAFT, OPTIMIZED, APPROVED, IN_PROGRESS, COMPLETED
    
    -- Optimization parameters used
    optimization_config JSONB,
    
    -- Results summary
    total_resources INTEGER,
    total_visits INTEGER,
    total_distance_km DECIMAL(10, 2),
    total_duration_minutes INTEGER,
    equity_coverage_score DECIMAL(5, 2),  -- % of Core20 covered
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    optimized_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id)
);

CREATE INDEX idx_route_plan_date ON route_plans(plan_date);
CREATE INDEX idx_route_plan_org ON route_plans(organization_id);

CREATE TABLE route_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_plan_id UUID REFERENCES route_plans(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES resources(id),
    
    -- Route geometry
    route_geometry GEOMETRY(LINESTRING, 4326),
    
    -- Summary
    sequence_count INTEGER,
    total_distance_km DECIMAL(10, 2),
    total_duration_minutes INTEGER,
    estimated_start_time TIME,
    estimated_end_time TIME,
    
    -- DEX metrics
    total_priority_score DECIMAL(10, 2),
    core20_visits_count INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE route_stops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_assignment_id UUID REFERENCES route_assignments(id) ON DELETE CASCADE,
    visit_location_id UUID REFERENCES visit_locations(id),
    
    -- Sequence
    stop_sequence INTEGER NOT NULL,
    
    -- Timing
    estimated_arrival TIME,
    estimated_departure TIME,
    
    -- Priority info (denormalized for quick access)
    priority_score DECIMAL(5, 2),
    priority_label VARCHAR(20),
    
    -- Actual execution
    actual_arrival TIMESTAMPTZ,
    actual_departure TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, COMPLETED, SKIPPED, RESCHEDULED
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_route_stops_assignment ON route_stops(route_assignment_id);
CREATE INDEX idx_route_stops_sequence ON route_stops(route_assignment_id, stop_sequence);

-- ============================================
-- AUDIT LOG (for NHS Compliance)
-- ============================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);

-- ============================================
-- MATERIALIZED VIEWS FOR DASHBOARDS
-- ============================================

CREATE MATERIALIZED VIEW mv_lsoa_dashboard AS
SELECT 
    l.id AS lsoa_id,
    l.lsoa_code,
    l.lsoa_name,
    l.icb_name,
    l.centroid,
    l.population_2021,
    
    -- IMD
    i.imd_decile,
    i.imd_score,
    i.is_core20,
    
    -- Demographics
    d.pct_minority,
    d.pct_no_car_household,
    d.pct_no_english,
    
    -- Clinical
    c.diabetes_prevalence,
    c.clinical_risk_score,
    
    -- Accessibility
    a.access_category,
    a.time_to_nearest_gp,
    
    -- DEX Priority (latest)
    p.priority_score,
    p.priority_label,
    p.explanation_text
    
FROM lsoa l
LEFT JOIN imd_data i ON l.id = i.lsoa_id
LEFT JOIN demographic_data d ON l.id = d.lsoa_id
LEFT JOIN clinical_data c ON l.id = c.lsoa_id
LEFT JOIN accessibility_data a ON l.id = a.lsoa_id
LEFT JOIN LATERAL (
    SELECT * FROM dex_priority_scores 
    WHERE lsoa_id = l.id 
    ORDER BY calculation_date DESC 
    LIMIT 1
) p ON TRUE;

CREATE INDEX idx_mv_lsoa_priority ON mv_lsoa_dashboard(priority_score DESC);
CREATE INDEX idx_mv_lsoa_core20 ON mv_lsoa_dashboard(is_core20);
```

---

## 3. Component Architecture

Detaljna struktura komponenti za **MVP Web Application** (mobile kasnije):

```
healthequiroute/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── Makefile
│
├── backend/                          # Python FastAPI Backend
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic/                      # Database migrations
│   │   ├── versions/
│   │   └── alembic.ini
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── config.py                 # Settings management
│   │   │
│   │   ├── api/                      # API Layer
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # Dependency injection
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # Main router aggregator
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py       # JWT + Google OAuth
│   │   │   │   │   ├── lsoa.py       # Geographic data endpoints
│   │   │   │   │   ├── priorities.py # DEX scores endpoints
│   │   │   │   │   ├── routes.py     # Route planning endpoints
│   │   │   │   │   ├── dashboard.py  # Dashboard data endpoints
│   │   │   │   │   ├── admin.py      # Admin configuration
│   │   │   │   │   ├── reports.py    # Impact reporting
│   │   │   │   │   ├── ml.py         # ML predictions API
│   │   │   │   │   ├── chat.py       # AI Chat Assistant
│   │   │   │   │   └── insights.py   # Gemini-powered insights
│   │   │   │   └── schemas/
│   │   │   │       ├── lsoa.py
│   │   │   │       ├── priority.py
│   │   │   │       ├── route.py
│   │   │   │       ├── ml.py
│   │   │   │       └── chat.py
│   │   │
│   │   ├── core/                     # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # Auth, JWT, permissions, Google OAuth
│   │   │   ├── exceptions.py         # Custom exceptions
│   │   │   └── events.py             # Event handlers
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── lsoa.py
│   │   │   ├── clinical.py
│   │   │   ├── priority.py
│   │   │   ├── route.py
│   │   │   ├── user.py
│   │   │   ├── audit.py
│   │   │   └── ml.py                 # ML models, predictions, chat
│   │   │
│   │   ├── services/                 # Business services
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── data_ingestion/       # Data import services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── synthetic_generator.py  # Synthetic data for Pilot
│   │   │   │   ├── imd_importer.py
│   │   │   │   ├── census_importer.py
│   │   │   │   ├── qof_importer.py
│   │   │   │   └── geography_importer.py
│   │   │   │
│   │   │   ├── dex_engine/           # DEX decision engine
│   │   │   │   ├── __init__.py
│   │   │   │   ├── engine.py         # Main DEX calculator
│   │   │   │   ├── fuzzifier.py      # Numeric → Category mapping
│   │   │   │   ├── rules.py          # Aggregation rules
│   │   │   │   ├── explainer.py      # Text explanation generator
│   │   │   │   └── config_loader.py  # Load rules from DB
│   │   │   │
│   │   │   ├── routing/              # VRP optimization
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vrp_solver.py     # Google OR-Tools VRP solver
│   │   │   │   ├── clustering.py     # Location clustering
│   │   │   │   ├── optimizer.py      # Route optimization orchestrator
│   │   │   │   └── distance_matrix.py # Travel time calculations
│   │   │   │
│   │   │   ├── ml/                   # Machine Learning services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health_predictor.py     # RandomForest health outcomes
│   │   │   │   ├── demand_forecaster.py    # Time-series forecasting
│   │   │   │   ├── model_registry.py       # Model versioning & loading
│   │   │   │   └── feature_engineering.py  # Feature extraction
│   │   │   │
│   │   │   ├── llm/                  # LLM & AI services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── gemini_insights.py      # Gemini API client
│   │   │   │   ├── context_builder.py      # RAG context builder
│   │   │   │   └── prompt_templates.py     # Prompt engineering
│   │   │   │
│   │   │   └── reporting/            # Analytics & reporting
│   │   │       ├── __init__.py
│   │   │       ├── equity_report.py
│   │   │       └── kpi_calculator.py
│   │   │
│   │   ├── repositories/             # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── lsoa_repo.py
│   │   │   ├── priority_repo.py
│   │   │   ├── route_repo.py
│   │   │   └── ml_repo.py
│   │   │
│   │   └── workers/                  # Background jobs (Celery)
│   │       ├── __init__.py
│   │       ├── celery_app.py
│   │       └── tasks/
│   │           ├── recalculate_priorities.py
│   │           ├── generate_routes.py
│   │           ├── train_ml_models.py      # ML training pipeline
│   │           └── data_sync.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       │   ├── test_dex_engine.py
│       │   ├── test_vrp_solver.py
│       │   ├── test_ml_predictor.py
│       │   └── test_llm_insights.py
│       └── integration/
│           ├── test_api_routes.py
│           └── test_ml_pipeline.py
│
├── frontend/                         # Vite + React + TypeScript
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   │
│   ├── src/
│   │   ├── main.tsx                  # Vite entry point
│   │   ├── App.tsx                   # Main app component
│   │   │
│   │   ├── api/                      # API client layer
│   │   │   ├── client.ts             # Axios instance
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── lsoa.ts
│   │   │   │   ├── priorities.ts
│   │   │   │   ├── routes.ts
│   │   │   │   ├── ml.ts             # ML predictions API
│   │   │   │   ├── chat.ts           # Chat Assistant API
│   │   │   │   └── insights.ts       # AI insights API
│   │   │   └── types/
│   │   │       ├── lsoa.ts
│   │   │       ├── route.ts
│   │   │       └── ml.ts
│   │   │
│   │   ├── components/
│   │   │   ├── common/               # Reusable components
│   │   │   │   ├── Button/
│   │   │   │   ├── Card/
│   │   │   │   ├── Modal/
│   │   │   │   └── Layout/
│   │   │   │
│   │   │   ├── auth/                 # Authentication
│   │   │   │   ├── GoogleSignIn.tsx
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   │
│   │   │   ├── maps/                 # Map visualization
│   │   │   │   ├── MapContainer.tsx
│   │   │   │   ├── HeatmapLayer.tsx
│   │   │   │   ├── RouteLayer.tsx
│   │   │   │   └── LSOAPolygons.tsx
│   │   │   │
│   │   │   ├── dashboard/            # Dashboard components
│   │   │   │   ├── PriorityPanel.tsx
│   │   │   │   ├── EquityMetrics.tsx
│   │   │   │   ├── KPICards.tsx
│   │   │   │   └── MLInsightsPanel.tsx    # AI predictions display
│   │   │   │
│   │   │   ├── routing/              # Route planning
│   │   │   │   ├── RouteOptimizer.tsx
│   │   │   │   ├── ResourceList.tsx
│   │   │   │   └── RouteTimeline.tsx
│   │   │   │
│   │   │   └── ai/                   # AI features
│   │   │       ├── ChatWidget.tsx    # Gemini chat assistant
│   │   │       └── InsightsPanel.tsx
│   │   │
│   │   ├── pages/                    # Page components (React Router)
│   │   │   ├── DashboardPage.tsx     # Strategic Planning Dashboard
│   │   │   ├── RoutesPage.tsx        # Operations Manager view
│   │   │   ├── AdminPage.tsx         # Admin panel
│   │   │   └── LoginPage.tsx
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useMap.ts
│   │   │   ├── usePriorities.ts
│   │   │   ├── useRoutes.ts
│   │   │   ├── useMLPredictions.ts
│   │   │   └── useAuth.ts
│   │   │
│   │   ├── store/                    # State management (Zustand)
│   │   │   ├── index.ts
│   │   │   ├── authStore.ts
│   │   │   ├── mapStore.ts
│   │   │   ├── routeStore.ts
│   │   │   └── chatStore.ts
│   │   │
│   │   └── styles/
│   │       ├── globals.css
│   │       └── tailwind.css
│   │
│   ├── public/
│   │   └── assets/
│   │
│   └── tests/
│       └── e2e/
│           └── dashboard.spec.ts
│
├── infrastructure/                   # Infrastructure as Code (Terraform)
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── modules/
│   │   │   ├── vpc/
│   │   │   ├── cloudsql/             # Cloud SQL PostgreSQL + PostGIS
│   │   │   ├── cloudrun/             # Cloud Run deployment
│   │   │   ├── gke/                  # Alternative: GKE cluster
│   │   │   ├── storage/              # Cloud Storage buckets
│   │   │   ├── memorystore/          # Redis
│   │   │   └── vertex-ai/            # Vertex AI setup
│   │   └── environments/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   │
│   └── kubernetes/                   # K8s manifests (if using GKE)
│       ├── base/
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   └── ingress.yaml
│       └── overlays/
│           ├── dev/
│           └── prod/
│
├── data/                             # Data processing scripts
│   ├── raw/                          # Raw downloaded data
│   ├── processed/                    # Cleaned data
│   └── scripts/
│       ├── generate_synthetic_data.py         # Synthetic data generator
│       ├── generate_synthetic_training_data.py # ML training data
│       ├── download_imd.py
│       ├── download_lsoa_boundaries.py
│       └── seed_database.py
│
└── docs/
    ├── architecture/
    │   ├── c4-diagrams/
    │   └── adr/                      # Architecture Decision Records
    ├── api/
    │   └── openapi.yaml
    └── deployment/
        └── gcp-setup.md

# Post-MVP (Phase 8+)
mobile/                               # PWA or React Native (future)
├── src/
│   ├── screens/
│   │   ├── RouteView.tsx
│   │   └── StopDetails.tsx
│   └── ...
```
    │   ├── c4-diagrams/
    │   └── adr/                      # Architecture Decision Records
    ├── api/
    │   └── openapi.yaml
    └── deployment/
```

---

## 4. Key API Endpoints

```yaml
# Core API Structure
/api/v1:
  
  # Authentication
  /auth:
    POST /login             # NHS SSO or local auth
    POST /logout
    GET  /me
  
  # Geographic Data
  /lsoa:
    GET  /                  # List LSOA with filters
    GET  /{lsoa_code}       # Single LSOA details
    GET  /{lsoa_code}/geojson  # GeoJSON for mapping
    GET  /search            # Search by postcode/name
    GET  /within-bounds     # Get LSOA in map viewport
  
  # Priority Scores (DEX)
  /priorities:
    GET  /                  # List all current priorities
    GET  /{lsoa_code}       # Priority for specific LSOA
    GET  /{lsoa_code}/history  # Historical scores
    GET  /{lsoa_code}/explain  # Detailed explanation
    POST /recalculate       # Trigger recalculation (admin)
  
  # Heatmap Data
  /heatmap:
    GET  /priority          # Priority heatmap data
    GET  /clinical          # Clinical risk heatmap
    GET  /deprivation       # IMD heatmap
  
  # Route Planning
  /routes:
    GET  /plans             # List route plans
    POST /plans             # Create new plan
    GET  /plans/{id}        # Get plan details
    POST /plans/{id}/optimize  # Run optimization
    PUT  /plans/{id}/approve   # Approve plan
    
    GET  /plans/{id}/assignments  # Get route assignments
    GET  /assignments/{id}/stops  # Get stops for assignment
  
  # Resources
  /resources:
    GET  /                  # List resources
    POST /                  # Add resource
    PUT  /{id}/availability # Update availability
  
  # Reporting
  /reports:
    GET  /equity            # Equity coverage report
    GET  /efficiency        # Efficiency metrics
    GET  /export            # Export data (CSV/Excel)
  
  # Admin
  /admin:
    GET  /dex-config        # Get DEX model config
    PUT  /dex-config        # Update weights/rules
    GET  /audit-log         # View audit trail
```

---

## 5. DEX Engine Implementation Detail

Evo detaljnije implementacije DEX engine-a:

```python
# backend/app/services/dex_engine/engine.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import numpy as np

class ClinicalCategory(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"
    CRITICAL = "CRITICAL"

class SocialCategory(Enum):
    LOW_VULNERABILITY = "LOW_VULNERABILITY"
    MODERATE_VULNERABILITY = "MODERATE_VULNERABILITY"
    HIGH_VULNERABILITY = "HIGH_VULNERABILITY"

class AccessCategory(Enum):
    GOOD = "GOOD"
    MODERATE = "MODERATE"
    POOR = "POOR"

class PriorityLabel(Enum):
    ROUTINE = "ROUTINE"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

@dataclass
class LSOAData:
    """Input data for DEX calculation"""
    lsoa_code: str
    
    # Clinical indicators
    diabetes_prevalence: float
    hypertension_prevalence: float
    copd_prevalence: float
    emergency_admissions_rate: float
    
    # Social indicators
    imd_decile: int  # 1-10, 1 = most deprived
    pct_minority: float  # 0-100
    pct_no_english: float  # 0-100
    pct_no_car: float  # 0-100
    
    # Accessibility
    time_to_gp_minutes: int
    time_to_hospital_minutes: int

@dataclass
class DEXResult:
    """Output from DEX calculation"""
    lsoa_code: str
    
    # Component scores (0-100)
    clinical_score: float
    social_score: float
    accessibility_score: float
    
    # Categories
    clinical_category: ClinicalCategory
    social_category: SocialCategory
    access_category: AccessCategory
    
    # Final result
    priority_score: float
    priority_label: PriorityLabel
    explanation: str
    
    # Constraints for routing
    requires_translator: bool
    min_visit_time_minutes: int

class DEXEngine:
    """
    Multi-Criteria Decision Analysis engine using DEX methodology.
    Converts raw LSOA data into intervention priorities.
    """
    
    def __init__(self, config: dict):
        """
        Initialize with configuration from database.
        
        config structure:
        {
            "weights": {
                "clinical": 0.40,
                "social": 0.35,
                "accessibility": 0.25
            },
            "thresholds": {
                "clinical": {...},
                "social": {...},
                "access": {...}
            },
            "rules": [...]
        }
        """
        self.config = config
        self.weights = config.get("weights", {
            "clinical": 0.40,
            "social": 0.35,
            "accessibility": 0.25
        })
    
    def calculate_priority(self, data: LSOAData) -> DEXResult:
        """Main entry point for priority calculation"""
        
        # Step 1: Fuzzification - Convert numeric values to categories
        clinical_cat, clinical_score = self._evaluate_clinical(data)
        social_cat, social_score = self._evaluate_social(data)
        access_cat, access_score = self._evaluate_accessibility(data)
        
        # Step 2: Apply expert rules to determine priority
        priority_label, base_priority = self._apply_rules(
            clinical_cat, social_cat, access_cat
        )
        
        # Step 3: Calculate weighted composite score
        weighted_score = (
            clinical_score * self.weights["clinical"] +
            social_score * self.weights["social"] +
            access_score * self.weights["accessibility"]
        )
        
        # Adjust weighted score based on rule-derived priority
        priority_multipliers = {
            PriorityLabel.URGENT: 1.0,
            PriorityLabel.HIGH: 0.75,
            PriorityLabel.MEDIUM: 0.50,
            PriorityLabel.ROUTINE: 0.25
        }
        final_score = min(100, weighted_score * priority_multipliers[priority_label] * 1.5)
        
        # Step 4: Generate explanation
        explanation = self._generate_explanation(
            data, clinical_cat, social_cat, access_cat, priority_label
        )
        
        # Step 5: Determine constraints
        requires_translator = data.pct_no_english > 15
        min_visit_time = self._calculate_min_visit_time(clinical_cat, social_cat)
        
        return DEXResult(
            lsoa_code=data.lsoa_code,
            clinical_score=clinical_score,
            social_score=social_score,
            accessibility_score=access_score,
            clinical_category=clinical_cat,
            social_category=social_cat,
            access_category=access_cat,
            priority_score=round(final_score, 2),
            priority_label=priority_label,
            explanation=explanation,
            requires_translator=requires_translator,
            min_visit_time_minutes=min_visit_time
        )
    
    def _evaluate_clinical(self, data: LSOAData) -> tuple[ClinicalCategory, float]:
        """
        Fuzzify clinical indicators into category and score.
        Uses normalized z-scores relative to national averages.
        """
        # National averages (these would come from config/database)
        AVG_DIABETES = 7.1  # per 100
        AVG_HYPERTENSION = 14.0
        AVG_COPD = 1.9
        AVG_EMERGENCY = 100  # per 1000
        
        # Calculate deviation from average (higher = worse)
        diabetes_factor = data.diabetes_prevalence / AVG_DIABETES
        hypertension_factor = data.hypertension_prevalence / AVG_HYPERTENSION
        copd_factor = data.copd_prevalence / AVG_COPD
        emergency_factor = data.emergency_admissions_rate / AVG_EMERGENCY
        
        # Weighted composite (diabetes and emergency weighted higher)
        composite = (
            diabetes_factor * 0.3 +
            hypertension_factor * 0.2 +
            copd_factor * 0.2 +
            emergency_factor * 0.3
        )
        
        # Convert to 0-100 score (capped)
        score = min(100, composite * 50)
        
        # Categorize
        if composite >= 1.8:
            category = ClinicalCategory.CRITICAL
        elif composite >= 1.4:
            category = ClinicalCategory.ELEVATED
        elif composite >= 1.0:
            category = ClinicalCategory.MODERATE
        else:
            category = ClinicalCategory.LOW
        
        return category, score
    
    def _evaluate_social(self, data: LSOAData) -> tuple[SocialCategory, float]:
        """
        Evaluate social vulnerability using IMD and demographic factors.
        """
        # IMD is already a composite - decile 1 is most deprived
        imd_score = (11 - data.imd_decile) * 10  # Convert to 0-100
        
        # Add bonus for ethnic minority concentration (health inequality proxy)
        minority_bonus = min(20, data.pct_minority * 0.4)
        
        # Language barrier factor
        language_bonus = min(15, data.pct_no_english * 1.5)
        
        # Transport deprivation
        transport_bonus = min(15, data.pct_no_car * 0.3)
        
        score = min(100, imd_score + minority_bonus + language_bonus + transport_bonus)
        
        # Categorize
        if score >= 70 or data.imd_decile <= 2:
            category = SocialCategory.HIGH_VULNERABILITY
        elif score >= 40 or data.imd_decile <= 4:
            category = SocialCategory.MODERATE_VULNERABILITY
        else:
            category = SocialCategory.LOW_VULNERABILITY
        
        return category, score
    
    def _evaluate_accessibility(self, data: LSOAData) -> tuple[AccessCategory, float]:
        """
        Evaluate healthcare accessibility based on travel times.
        """
        # Score based on GP access (primary metric)
        if data.time_to_gp_minutes <= 10:
            gp_score = 20
        elif data.time_to_gp_minutes <= 20:
            gp_score = 40
        elif data.time_to_gp_minutes <= 30:
            gp_score = 60
        else:
            gp_score = 80 + min(20, (data.time_to_gp_minutes - 30) * 2)
        
        # Hospital access bonus
        if data.time_to_hospital_minutes > 45:
            hospital_bonus = 20
        elif data.time_to_hospital_minutes > 30:
            hospital_bonus = 10
        else:
            hospital_bonus = 0
        
        score = min(100, gp_score + hospital_bonus)
        
        # Categorize
        if score >= 60:
            category = AccessCategory.POOR
        elif score >= 35:
            category = AccessCategory.MODERATE
        else:
            category = AccessCategory.GOOD
        
        return category, score
    
    def _apply_rules(
        self,
        clinical: ClinicalCategory,
        social: SocialCategory,
        access: AccessCategory
    ) -> tuple[PriorityLabel, float]:
        """
        Apply expert-defined decision rules.
        These rules encode domain knowledge about intervention priority.
        """
        
        # URGENT conditions
        if clinical == ClinicalCategory.CRITICAL and social == SocialCategory.HIGH_VULNERABILITY:
            return PriorityLabel.URGENT, 100
        
        if clinical == ClinicalCategory.CRITICAL and access == AccessCategory.POOR:
            return PriorityLabel.URGENT, 95
        
        # HIGH conditions
        if clinical == ClinicalCategory.ELEVATED and social == SocialCategory.HIGH_VULNERABILITY:
            return PriorityLabel.HIGH, 80
        
        if clinical == ClinicalCategory.CRITICAL:
            return PriorityLabel.HIGH, 75
        
        if social == SocialCategory.HIGH_VULNERABILITY and access == AccessCategory.POOR:
            return PriorityLabel.HIGH, 70
        
        # MEDIUM conditions
        if clinical == ClinicalCategory.ELEVATED:
            return PriorityLabel.MEDIUM, 55
        
        if social == SocialCategory.HIGH_VULNERABILITY:
            return PriorityLabel.MEDIUM, 50
        
        if access == AccessCategory.POOR and social == SocialCategory.MODERATE_VULNERABILITY:
            return PriorityLabel.MEDIUM, 45
        
        # Default to ROUTINE
        return PriorityLabel.ROUTINE, 25
    
    def _generate_explanation(
        self,
        data: LSOAData,
        clinical: ClinicalCategory,
        social: SocialCategory,
        access: AccessCategory,
        priority: PriorityLabel
    ) -> str:
        """
        Generate human-readable explanation for the priority decision.
        Required for NHS 'Explainable AI' compliance.
        """
        explanations = []
        
        # Clinical explanation
        if clinical == ClinicalCategory.CRITICAL:
            explanations.append(
                f"Critical health risk: diabetes prevalence {data.diabetes_prevalence:.1f}%, "
                f"emergency admissions {data.emergency_admissions_rate:.0f} per 1000"
            )
        elif clinical == ClinicalCategory.ELEVATED:
            explanations.append("Elevated chronic disease burden in this area")
        
        # Social explanation
        if social == SocialCategory.HIGH_VULNERABILITY:
            if data.imd_decile <= 2:
                explanations.append(f"Core20 population: IMD decile {data.imd_decile} (most deprived)")
            if data.pct_minority > 30:
                explanations.append(f"Significant ethnic minority population ({data.pct_minority:.0f}%)")
            if data.pct_no_english > 10:
                explanations.append(f"Language barriers present ({data.pct_no_english:.1f}% limited English)")
        
        # Access explanation
        if access == AccessCategory.POOR:
            explanations.append(
                f"Poor healthcare access: {data.time_to_gp_minutes} min to GP, "
                f"{data.time_to_hospital_minutes} min to hospital"
            )
        
        # Combine
        if explanations:
            reason = "; ".join(explanations)
            return f"{priority.value} priority: {reason}."
        else:
            return f"{priority.value} priority: Standard risk profile."
    
    def _calculate_min_visit_time(
        self,
        clinical: ClinicalCategory,
        social: SocialCategory
    ) -> int:
        """Calculate minimum recommended visit duration in minutes."""
        base_time = 15
        
        if clinical in [ClinicalCategory.CRITICAL, ClinicalCategory.ELEVATED]:
            base_time += 10
        
        if social == SocialCategory.HIGH_VULNERABILITY:
            base_time += 5
        
        return base_time
```

---

## 6. Sledeći Koraci (Recommended Roadmap)

Prema PRD-u, evo optimizovanog plana:

| Faza | Trajanje | Deliverables |
|------|----------|--------------|
| **WP1: Foundation** | 3-4 nedelje | Database setup, LSOA geography import, IMD/Census data pipeline |
| **WP2: DEX Core** | 4-5 nedelja | DEX engine, Admin UI za pravila, API endpoints |
| **WP3: Routing** | 4-5 nedelja | VRP solver integration, Route optimization API |
| **WP4: Frontend** | 5-6 nedelja | Dashboard, Heatmaps, Route planner UI |
| **WP5: Validation** | 3-4 nedelje | Testing, NHS compliance docs, Pilot |

---

Šta želiš da istražimo detaljnije?

1. **VRP Solver** - Detaljna implementacija Google OR-Tools za weighted routing
2. **Data Pipeline** - Kako ingestovati NHS podatke (IMD, QOF, Census)
3. **Frontend Components** - React komponente za heatmap i routing
4. **Infrastructure** - Terraform/GCP setup za UK deployment
5. **NHS Compliance** - DCB0129, DSPT, DPIA dokumentacija
6. **AI/ML Features** - Predictive models i LLM integration

---

## 7. AI/ML Intelligence Layer

### 7.1 Predictive Analytics Module

#### Health Outcome Prediction

ML modeli koji predviđaju buduće health outcomes na osnovu trenutnih demografskih i kliničkih podataka.

**Use Cases:**
- Predviđanje povećanja broja emergency admissions za LSOA u sledećih 6 meseci
- Identifikacija LSOA sa rizikom od epidemije (npr. gripa, COVID)
- Early warning sistem za deteriorating health indicators

**Model Architecture:**
```python
# backend/app/services/ml/health_predictor.py

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
from typing import Dict, List
import joblib

class HealthOutcomePredictor:
    """
    Predicts future health outcomes using historical trends.
    
    Features:
    - Demographics (age distribution, ethnicity, deprivation)
    - Clinical indicators (disease prevalence)
    - Seasonal factors
    - Historical intervention data (visits, resource allocation)
    
    Target:
    - Emergency admission rate (next 6 months)
    - Disease prevalence trends
    """
    
    def __init__(self, model_path: str = None):
        if model_path:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(f"{model_path}_scaler.pkl")
        else:
            self.model = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                random_state=42
            )
            self.scaler = StandardScaler()
    
    def prepare_features(self, lsoa_data: pd.DataFrame) -> pd.DataFrame:
        """Extract and engineer features from LSOA data."""
        features = pd.DataFrame()
        
        # Demographic features
        features['population'] = lsoa_data['population_2021']
        features['pct_elderly'] = lsoa_data['population_65_plus'] / lsoa_data['total_population']
        features['pct_minority'] = lsoa_data['pct_minority']
        features['imd_score'] = lsoa_data['imd_score']
        
        # Clinical features
        features['diabetes_prev'] = lsoa_data['diabetes_prevalence']
        features['copd_prev'] = lsoa_data['copd_prevalence']
        features['current_emergency_rate'] = lsoa_data['emergency_admissions_rate']
        
        # Accessibility features
        features['time_to_gp'] = lsoa_data['time_to_nearest_gp']
        
        # Historical intervention features (from route history)
        features['avg_visits_per_month'] = lsoa_data['historical_visit_count'] / 12
        features['avg_visit_duration'] = lsoa_data['historical_visit_duration_avg']
        
        # Temporal features
        features['month'] = pd.to_datetime('now').month
        features['quarter'] = (features['month'] - 1) // 3 + 1
        
        return features
    
    def train(self, training_data: pd.DataFrame, target_column: str):
        """Train the model on historical data."""
        X = self.prepare_features(training_data)
        y = training_data[target_column]
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        return self.model.score(X_scaled, y)  # R² score
    
    def predict(self, lsoa_data: pd.DataFrame) -> Dict[str, float]:
        """Predict future emergency admission rate."""
        X = self.prepare_features(lsoa_data)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        
        # Feature importance for explainability
        feature_importance = dict(zip(
            X.columns,
            self.model.feature_importances_
        ))
        
        return {
            'predicted_emergency_rate': predictions[0],
            'confidence_interval': self._calculate_confidence(X_scaled),
            'top_factors': sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def _calculate_confidence(self, X_scaled) -> tuple:
        """Calculate prediction confidence interval using tree variance."""
        predictions = []
        for tree in self.model.estimators_:
            predictions.append(tree.predict(X_scaled))
        
        predictions = np.array(predictions)
        std = np.std(predictions, axis=0)
        
        # 95% confidence interval
        return (
            np.mean(predictions) - 1.96 * std,
            np.mean(predictions) + 1.96 * std
        )
```

**Training Pipeline:**
```python
# backend/app/workers/tasks/train_ml_models.py

from app.services.ml.health_predictor import HealthOutcomePredictor
from app.repositories.lsoa_repo import LSOARepository
from google.cloud import storage
import pandas as pd

async def train_health_predictor_task():
    """
    Celery task to retrain health predictor model.
    Runs monthly with latest historical data.
    """
    # Fetch historical data
    repo = LSOARepository()
    historical_data = await repo.get_historical_health_data(
        months_back=36  # 3 years of data
    )
    
    # Initialize predictor
    predictor = HealthOutcomePredictor()
    
    # Train
    score = predictor.train(
        historical_data,
        target_column='emergency_admissions_rate_6mo_forward'
    )
    
    # Save to GCS
    model_path = '/tmp/health_predictor.pkl'
    joblib.dump(predictor.model, model_path)
    
    bucket = storage.Client().bucket('her-ml-models')
    blob = bucket.blob(f'health_predictor_v{datetime.now().strftime("%Y%m%d")}.pkl')
    blob.upload_from_filename(model_path)
    
    return {
        'r2_score': score,
        'model_version': blob.name,
        'trained_at': datetime.now().isoformat()
    }
```

---

#### Resource Demand Forecasting

Predviđa potrebu za resursima (nurses, vehicles) u sledećem periodu.

**Features:**
- Historical visit counts per LSOA
- Seasonal trends
- Disease prevalence trends
- Intervention effectiveness (% improvement after visits)

**Model:** Time-series forecasting (Prophet ili ARIMA)

**Output:**
- Expected number of visits needed per LSOA next month
- Resource allocation recommendations
- Confidence intervals

---

#### Risk Stratification with ML

Enhanced DEX scoring sa ML modelom koji uči iz historical outcomes.

**Approach:**
1. DEX engine daje baseline priority score
2. ML model adjusts score based on learned patterns:
   - Similar LSOA outcomes in the past
   - Intervention effectiveness data
   - Unexpected risk factors DEX rules may miss

**Model:** Gradient Boosting (XGBoost) za feature interactions

---

### 7.2 LLM Integration - Gemini API

#### Natural Language Insights Engine

**Use Case 1: Equity Report Narration**

Automatic generation of executive summaries for equity reports.

```python
# backend/app/services/llm/gemini_insights.py

import google.generativeai as genai
from typing import Dict, List
import json

class GeminiInsightsEngine:
    """
    Uses Gemini API to generate natural language insights.
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def generate_equity_report_summary(
        self,
        equity_metrics: Dict,
        priority_distribution: Dict,
        route_data: Dict
    ) -> str:
        """
        Generate executive summary of equity coverage.
        
        Input metrics:
        - core20_coverage_percentage
        - visits_by_priority_label
        - geographic_distribution
        - intervention_effectiveness
        """
        
        prompt = f"""
You are an NHS health equity analyst. Generate a concise executive summary 
of this month's community health intervention equity report.

**Equity Metrics:**
{json.dumps(equity_metrics, indent=2)}

**Priority Distribution:**
{json.dumps(priority_distribution, indent=2)}

**Route Performance:**
{json.dumps(route_data, indent=2)}

Provide:
1. Overall equity assessment (2-3 sentences)
2. Key wins (bullet points)
3. Areas of concern (bullet points)
4. Actionable recommendations (3 specific recommendations)

Use NHS terminology. Be data-driven but accessible to non-technical stakeholders.
"""
        
        response = await self.model.generate_content_async(prompt)
        return response.text
    
    async def generate_lsoa_insights(self, lsoa_code: str, lsoa_data: Dict) -> str:
        """
        Generate natural language explanation of why an LSOA has 
        its current priority score.
        """
        
        prompt = f"""
You are explaining to an NHS operations manager why LSOA {lsoa_code} 
has been assigned a specific priority level.

**LSOA Data:**
{json.dumps(lsoa_data, indent=2)}

Explain in 2-3 sentences:
1. What makes this area a priority (or not)
2. What specific factors contribute most
3. What type of intervention would be most effective

Be empathetic and action-oriented. Use plain English.
"""
        
        response = await self.model.generate_content_async(prompt)
        return response.text
```

---

**Use Case 2: AI Chat Assistant for Planners**

Interactive chat interface embedded in dashboard.

**Sample Queries:**
- "Which areas need more visits this month?"
- "Why is LSOA E01000523 marked as urgent?"
- "Show me areas with high diabetes prevalence and poor GP access"
- "What's the optimal resource allocation for next quarter?"
- "Summarize the impact of last month's interventions"

```python
# backend/app/api/v1/endpoints/chat.py

from fastapi import APIRouter, Depends
from app.services.llm.gemini_insights import GeminiInsightsEngine
from app.services.llm.context_builder import ChatContextBuilder
from pydantic import BaseModel

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    conversation_id: str

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict]  # Data sources used
    suggested_actions: List[str]

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    msg: ChatMessage,
    gemini: GeminiInsightsEngine = Depends()
):
    """
    AI chat endpoint using Gemini API with RAG 
    (Retrieval-Augmented Generation).
    """
    
    # Build context from database
    context_builder = ChatContextBuilder()
    context = await context_builder.build_context(msg.message)
    
    # Query Gemini with context
    prompt = f"""
You are an AI assistant for HealthEquiRoute, an NHS health equity platform.
Answer the user's question using the provided data context.

**User Question:** {msg.message}

**Data Context:**
{context.to_json()}

Provide:
1. Direct answer to the question
2. Supporting data points
3. 2-3 actionable recommendations

Be concise and data-driven.
"""
    
    response = await gemini.model.generate_content_async(prompt)
    
    # Extract suggested actions using structured output
    actions = await gemini.extract_actions(response.text)
    
    return ChatResponse(
        response=response.text,
        sources=context.sources,
        suggested_actions=actions
    )
```

---

**Use Case 3: Auto-Generated Policy Recommendations**

Based on monthly equity analysis, Gemini generates policy recommendations.

**Input:**
- Core20 coverage trends (last 6 months)
- Intervention effectiveness by area type
- Resource utilization rates
- Health outcome improvements

**Output:**
```
POLICY RECOMMENDATION REPORT - November 2025

1. INCREASE RESOURCE ALLOCATION TO RURAL DEPRIVED AREAS
   Rationale: Core20 coverage in rural areas (64%) lags behind 
   urban (82%). Travel times are a barrier.
   
   Action: Add 2 mobile units to cover outlying LSOA.
   Expected Impact: +15% coverage, reaching 600 additional patients.
   
2. IMPLEMENT SPECIALIST DIABETES PATHWAY IN HIGH-PREVALENCE LSOA
   Rationale: 12 LSOA have diabetes prevalence >12%, but generic 
   visit protocols show limited effectiveness.
   
   Action: Train 3 nurses in diabetes specialist care, assign to high-prev areas.
   Expected Impact: 20% reduction in emergency admissions (based on similar ICB data).

3. ENHANCE TRANSLATOR SERVICES
   Rationale: 23% of visits to LSOA with >10% non-English speakers 
   report communication barriers.
   
   Action: Contract remote interpreter service, integrate into visit workflow.
   Expected Impact: Improved patient satisfaction, better health literacy.
```

---

### 7.3 Database Schema Additions for ML

```sql
-- ============================================
-- ML MODELS METADATA
-- ============================================

CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,  -- HEALTH_PREDICTOR, DEMAND_FORECAST, RISK_STRATIFICATION
    
    -- Storage
    gcs_path TEXT NOT NULL,  -- gs://her-ml-models/health_predictor_v20251129.pkl
    
    -- Performance metrics
    training_metrics JSONB,  -- {"r2_score": 0.87, "mae": 12.3, ...}
    validation_metrics JSONB,
    
    -- Metadata
    trained_on TIMESTAMPTZ NOT NULL,
    training_data_period VARCHAR(50),  -- "2021-01 to 2024-12"
    features_used JSONB,  -- List of features
    
    is_active BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMPTZ,
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ml_models_active ON ml_models(is_active, model_type);

-- ============================================
-- ML PREDICTIONS
-- ============================================

CREATE TABLE ml_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models(id),
    lsoa_id UUID REFERENCES lsoa(id),
    
    prediction_type VARCHAR(50) NOT NULL,  -- EMERGENCY_RATE, DEMAND_FORECAST
    prediction_date DATE NOT NULL,
    prediction_horizon VARCHAR(20),  -- "6_MONTHS", "1_MONTH"
    
    -- Prediction results
    predicted_value DECIMAL(10, 2) NOT NULL,
    confidence_lower DECIMAL(10, 2),
    confidence_upper DECIMAL(10, 2),
    confidence_level DECIMAL(3, 2) DEFAULT 0.95,  -- 95% CI
    
    -- Explainability
    top_contributing_factors JSONB,  -- [{"feature": "imd_score", "importance": 0.34}, ...]
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ml_predictions_lsoa ON ml_predictions(lsoa_id, prediction_date);
CREATE INDEX idx_ml_predictions_model ON ml_predictions(model_id);

-- ============================================
-- LLM CHAT HISTORY
-- ============================================

CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),  -- Auto-generated from first message
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES chat_conversations(id) ON DELETE CASCADE,
    
    role VARCHAR(20) NOT NULL,  -- USER, ASSISTANT, SYSTEM
    message_text TEXT NOT NULL,
    
    -- Context used for RAG
    context_data JSONB,  -- LSOA data, priority scores, etc. that were retrieved
    
    -- Gemini metadata
    model_version VARCHAR(50),  -- gemini-1.5-pro
    token_count INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_conv ON chat_messages(conversation_id, created_at);
```

---

### 7.4 API Endpoints for AI Features

```yaml
# ML Predictions
/api/v1/ml:
  GET  /predictions/{lsoa_code}     # Get latest predictions for LSOA
  GET  /predictions/forecast        # Demand forecast for next period
  POST /predictions/refresh         # Trigger prediction refresh
  
  GET  /models                      # List available models
  GET  /models/{id}/performance     # Model performance metrics

# LLM Chat
/api/v1/chat:
  POST /                            # Send chat message
  GET  /conversations               # List user's conversations
  GET  /conversations/{id}/messages # Get conversation history
  DELETE /conversations/{id}        # Delete conversation

# AI Insights
/api/v1/insights:
  POST /equity-summary              # Generate equity report summary
  POST /lsoa-explanation/{code}     # Generate LSOA explanation
  POST /policy-recommendations      # Generate policy recommendations
```

---

### 7.5 Frontend Components

**AI Chat Widget:**
```typescript
// frontend/src/components/ai/ChatWidget.tsx

import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { aiApi } from '@/api/endpoints/ai';

export function ChatWidget() {
  const [message, setMessage] = useState('');
  const [conversationId, setConversationId] = useState<string>();
  
  const { data: messages } = useQuery({
    queryKey: ['chat', conversationId],
    queryFn: () => aiApi.getMessages(conversationId),
    enabled: !!conversationId
  });
  
  const sendMessage = useMutation({
    mutationFn: (text: string) => aiApi.sendMessage({
      message: text,
      conversation_id: conversationId || 'new'
    }),
    onSuccess: (data) => {
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }
    }
  });
  
  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white shadow-xl rounded-lg">
      <div className="p-4 bg-blue-600 text-white rounded-t-lg">
        <h3>AI Assistant</h3>
      </div>
      
      <div className="h-[480px] overflow-y-auto p-4">
        {messages?.map(msg => (
          <div key={msg.id} className={msg.role === 'user' ? 'text-right' : ''}>
            <div className="inline-block p-3 rounded-lg mb-2">
              {msg.message_text}
            </div>
          </div>
        ))}
      </div>
      
      <div className="p-4 border-t">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              sendMessage.mutate(message);
              setMessage('');
            }
          }}
          placeholder="Ask about equity metrics..."
          className="w-full p-2 border rounded"
        />
      </div>
    </div>
  );
}
```

**ML Insights Panel:**
```typescript
// frontend/src/components/dashboard/MLInsightsPanel.tsx

export function MLInsightsPanel({ lsoaCode }: { lsoaCode: string }) {
  const { data: prediction } = useQuery({
    queryKey: ['ml-prediction', lsoaCode],
    queryFn: () => mlApi.getPrediction(lsoaCode)
  });
  
  const { data: explanation } = useQuery({
    queryKey: ['ai-explanation', lsoaCode],
    queryFn: () => aiApi.getLsoaExplanation(lsoaCode)
  });
  
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">AI Insights</h3>
      
      {/* Prediction */}
      <div className="mb-4">
        <h4 className="font-medium">6-Month Forecast</h4>
        <p className="text-2xl font-bold text-blue-600">
          {prediction?.predicted_value.toFixed(1)} 
          <span className="text-sm text-gray-500">emergency admissions/1000</span>
        </p>
        <p className="text-sm text-gray-600">
          95% CI: [{prediction?.confidence_lower.toFixed(1)}, {prediction?.confidence_upper.toFixed(1)}]
        </p>
      </div>
      
      {/* Natural language explanation */}
      <div className="bg-blue-50 p-4 rounded">
        <p className="text-sm">{explanation?.text}</p>
      </div>
      
      {/* Top factors */}
      <div className="mt-4">
        <h4 className="font-medium mb-2">Key Risk Factors</h4>
        <ul className="space-y-1">
          {prediction?.top_contributing_factors.map(factor => (
            <li key={factor.feature} className="flex justify-between text-sm">
              <span>{factor.feature}</span>
              <span className="font-mono">{(factor.importance * 100).toFixed(0)}%</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

### 7.6 Training Data & Synthetic Data Generation

Za Pilot fazu, generisaćemo sintetičke podatke koji simuliraju NHS data:

```python
# data/scripts/generate_synthetic_training_data.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_historical_data(n_lsoa: int = 500, n_months: int = 36):
    """
    Generate synthetic historical data for ML training.
    Simulates 3 years of monthly health data for LSOA areas.
    """
    
    data = []
    
    for lsoa_idx in range(n_lsoa):
        # LSOA characteristics (fixed over time)
        base_imd = np.random.randint(1, 11)  # 1-10 decile
        base_population = np.random.randint(800, 3000)
        pct_elderly = np.random.uniform(0.08, 0.25)
        pct_minority = np.random.uniform(0, 0.6)
        
        # Time series with trend and seasonality
        for month_idx in range(n_months):
            date = datetime.now() - timedelta(days=30 * (n_months - month_idx))
            
            # Seasonal factor (winter = more emergency admissions)
            seasonal_factor = 1.2 if date.month in [12, 1, 2] else 1.0
            
            # Trend (slight increase over time in deprived areas)
            trend_factor = 1.0 + (month_idx / n_months) * 0.1 if base_imd <= 3 else 1.0
            
            # Base emergency rate depends on deprivation
            base_rate = 80 + (11 - base_imd) * 10  # Higher deprivation = more emergencies
            
            emergency_rate = base_rate * seasonal_factor * trend_factor * np.random.uniform(0.9, 1.1)
            
            # Simulated intervention effect
            visits_this_month = np.random.poisson(5 if base_imd <= 3 else 2)
            intervention_effect = 0.95 ** visits_this_month  # Each visit reduces rate by 5%
            
            data.append({
                'lsoa_code': f'E0100{lsoa_idx:04d}',
                'date': date,
                'imd_decile': base_imd,
                'population': base_population,
                'pct_elderly': pct_elderly,
                'pct_minority': pct_minority,
                'diabetes_prevalence': np.random.uniform(5, 15),
                'copd_prevalence': np.random.uniform(1, 4),
                'time_to_gp': np.random.randint(5, 40),
                'visits_count': visits_this_month,
                'emergency_admissions_rate': emergency_rate * intervention_effect,
                # Target: next month's rate
                'emergency_rate_next_month': None  # Will be filled
            })
    
    df = pd.DataFrame(data)
    
    # Fill forward target
    df = df.sort_values(['lsoa_code', 'date'])
    df['emergency_rate_next_month'] = df.groupby('lsoa_code')['emergency_admissions_rate'].shift(-1)
    
    # Similarly for 6-month forward
    df['emergency_rate_6mo_forward'] = df.groupby('lsoa_code')['emergency_admissions_rate'].shift(-6)
    
    return df.dropna()

# Generate and save
training_data = generate_synthetic_historical_data()
training_data.to_csv('data/processed/synthetic_training_data.csv', index=False)
```

---

Ovo predstavlja kompletan AI/ML sloj koji može da se dodaje inkrementalno nakon MVP-a.