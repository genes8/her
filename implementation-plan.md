Implementation Plan: HealthEquiRoute Platform
=============================================

Plan razvoja NHS HealthEquiRoute platforme - sistem za optimizaciju zdravstvenih usluga sa fokusem na pravičnost (equity).

* * * * *

User Review Required
--------------------

IMPORTANT

**MVP Scope (Phases 1-5)**: Core functionality bez AI/ML features:

-   **Phase 1**: Backend foundation + PostgreSQL/PostGIS + Auth (JWT + Google OAuth)
-   **Phase 2**: DEX Engine (priority calculation)
-   **Phase 3**: Routing Engine (Google OR-Tools VRP)
-   **Phase 4**: Frontend (Vite + React + TypeScript, maps, dashboards)
-   **Phase 5**: Testing + GCP Deployment

**Post-MVP (Phase 6)**: AI/ML Intelligence - Gemini API, ML predictions, Chat Assistant

IMPORTANT

**Tech Stack**:

-   **Backend**: FastAPI (Python) + PostgreSQL/PostGIS
-   **Frontend**: React Router + TypeScript
-   **Routing**: Google OR-Tools
-   **Auth**: JWT + Google OAuth 2.0 (manual setup, ne Firebase)
-   **Hosting**: Hetzner (Docker deployment)
-   **AI/ML** (Post-MVP): Kimi-K2 Thinking Turbo API + scikit-learn

IMPORTANT

**Data Strategy**:

-   **MVP**: Sintetički podaci (synthetic data generators)
-   **Production**: Data Adapter Pattern omogućava laku zamenu sa realnim NHS podacima

WARNING

**NHS Compliance**:

-   EU hosting (Hetzner Germany datacenter) - GDPR compliant
-   End-to-end encryption (data at rest & in transit)
-   Audit logging (sve user actions)
-   Role-based access control (RBAC)
-   DPIA dokumentacija required

* * * * *

Proposed Changes - MVP Scope
----------------------------

Izmene organizovane po MVP fazama (1-5). AI/ML features su izdvojene u Post-MVP sekciju.

### Phase 1: Project Foundation

#### [NEW] docker-compose.yml

Docker Compose konfiguracija za lokalni development sa sledećim servisima:

-   PostgreSQL 15 + PostGIS extension
-   Redis za cache i message queue
-   FastAPI backend (hot reload)
-   React Router frontend (dev server)
-   pgAdmin za database management

#### [NEW] .env.example

Template za environment varijable:

-   Database connection strings (PostgreSQL)
-   JWT secret keys
-   Google OAuth 2.0 client ID/secret
-   Kimi API key (za Post-MVP)
-   MapLibre API settings
-   DEX model konfiguracija
-   Hetzner server credentials

#### [NEW] Makefile

Makefile sa korisnim komandama:

-   `make setup` - inicijalno setup projekta
-   `make dev` - pokreće development environment
-   `make migrate` - database migrations
-   `make test` - pokreće testove
-   `make seed` - učitava sample podatke

* * * * *

### Backend Component

#### [NEW] backend/Dockerfile

Multi-stage Docker build za production-ready Python backend sa:

-   Python 3.11
-   Poetry za dependency management
-   GDAL/PostGIS klijent biblioteke
-   Non-root user za security

#### [NEW] backend/pyproject.toml

Python dependencies:

-   FastAPI + Uvicorn
-   SQLAlchemy + Alembic
-   PostGIS support (GeoAlchemy2)
-   Pydantic za validaciju
-   NumPy/Pandas za DEX engine
-   Google OR-Tools za routing
-   Redis/Celery za background jobs
-   pytest za testing

#### [NEW] backend/app/main.py

FastAPI application entry point:

-   CORS middleware configuration
-   Router registration (v1 API)
-   Database session middleware
-   Audit logging middleware
-   Health check endpoint
-   Startup/shutdown events

#### [NEW] backend/app/config.py

Settings management using Pydantic BaseSettings:

-   Database URLs (PostgreSQL connection string)
-   JWT configuration
-   Google OAuth 2.0 configuration
-   Hetzner deployment settings
-   DEX model defaults
-   Feature flags (enable/disable modules)

#### [NEW] backend/app/core/security.py

Security utilities:

-   JWT token creation/validation
-   Password hashing (bcrypt)
-   Role-based permissions decorator
-   NHS Smartcard SSO integration (placeholder)

* * * * *

### Database Layer

#### [NEW] backend/alembic/env.py

Alembic configuration za migrations sa:

-   PostGIS extension support
-   Automatic model detection
-   Migration versioning

#### [NEW] backend/alembic/versions/001_initial_schema.py

Initial database migration koji kreira sve tabele iz PRD-a:

-   Geographic tables (LSOA)
-   Reference data (IMD, Demographics, Clinical)
-   DEX engine tables
-   Route planning tables
-   User/organization tables
-   Audit log

#### [NEW] backend/app/models/lsoa.py

SQLAlchemy model za LSOA geographic data:

-   UUID primary keys
-   PostGIS geometry columns
-   Relationships sa IMD, demographics, clinical data
-   Spatial indexes

#### [NEW] backend/app/models/priority.py

DEX priority scores model:

-   Component scores (clinical, social, accessibility)
-   Priority labels i scores
-   Explanation text
-   Contributing factors (JSONB)
-   Model version tracking

#### [NEW] backend/app/models/route.py

Route planning models:

-   RoutePlan (header)
-   RouteAssignment (resource assignment)
-   RouteStop (individual stops)
-   Actual vs. planned tracking

* * * * *

### DEX Engine Implementation

#### [NEW] backend/app/services/dex_engine/engine.py

Core DEX engine implementation (već definisan u PRD-u):

-   Multi-criteria decision analysis
-   Fuzzification (numeric → categorical)
-   Rule-based aggregation
-   Weighted scoring
-   Explanation generation
-   Visit time calculation

#### [NEW] backend/app/services/dex_engine/fuzzifier.py

Fuzzification utilities:

-   Clinical indicator categorization
-   Social vulnerability scoring
-   Accessibility categorization
-   Threshold management

#### [NEW] backend/app/services/dex_engine/explainer.py

Explainable AI implementation:

-   Human-readable explanations
-   Contributing factors breakdown
-   NHS compliance (explainability requirement)
-   Multi-language support (potential)

* * * * *

### Data Ingestion Pipeline

#### [NEW] backend/app/services/data_ingestion/imd_importer.py

Index of Multiple Deprivation data importer:

-   Download from ONS
-   CSV parsing
-   LSOA code mapping
-   Bulk insert sa progress tracking

#### [NEW] backend/app/services/data_ingestion/geography_importer.py

LSOA boundary importer:

-   Download GeoJSON/Shapefile from ONS Geography
-   Transform to WGS84 (SRID 4326)
-   Calculate centroids
-   PostGIS insert

#### [NEW] backend/app/services/data_ingestion/census_importer.py

Census 2021 demographic data:

-   Population breakdown
-   Ethnicity percentages
-   Language data
-   Household composition

#### [NEW] backend/app/services/data_ingestion/qof_importer.py

QOF (Quality and Outcomes Framework) clinical data:

-   Disease prevalence by GP practice
-   Map to LSOA via postcode lookup
-   Calculate area-level prevalence

* * * * *

### Routing Engine

#### [NEW] backend/app/services/routing/vrp_solver.py

Google OR-Tools Vehicle Routing Problem solver:

-   Multi-vehicle capacity constraints
-   Time windows
-   Skill matching
-   Priority-weighted objective function
-   Distance/duration minimization

#### [NEW] backend/app/services/routing/optimizer.py

High-level route optimization orchestrator:

-   Load visits and resources from database
-   Build distance matrix
-   Call VRP solver
-   Save optimized routes
-   Calculate equity metrics

#### [NEW] backend/app/services/routing/distance_matrix.py

Distance/time matrix calculator:

-   Use Ordnance Survey routing API or OSRM
-   Cache results in Redis
-   Haversine distance fallback

#### [NEW] backend/app/services/routing/clustering.py

Location clustering pre-processor:

-   K-means clustering za velike datasets
-   Reduce computation time
-   Maintain priority balance

* * * * *

### AI/ML Intelligence Layer

#### [NEW] backend/app/services/ml/health_predictor.py

ML model za predviđanje health outcomes:

-   RandomForest regressor za emergency admission prediction
-   Feature engineering (demographics, clinical, seasonal)
-   Confidence interval calculation
-   Feature importance za explainability
-   Model versioning i local storage (Docker volumes)

#### [NEW] backend/app/services/ml/demand_forecaster.py

Time-series forecasting za resource demand:

-   Prophet ili ARIMA model
-   Seasonal decomposition
-   Forecast sa confidence intervals
-   Resource allocation recommendations

#### [NEW] backend/app/services/llm/gemini_insights.py

Gemini API integration:

-   **Equity report narration** - auto-generated summaries
-   **LSOA insights generator** - natural language explanations
-   **Policy recommendations** - actionable insights
-   Prompt engineering za consistent outputs

#### [NEW] backend/app/services/llm/context_builder.py

RAG (Retrieval-Augmented Generation) context builder:

-   Query understanding
-   Relevant data retrieval from database
-   Context formatting za Kimi API prompts
-   Source tracking

#### [NEW] backend/app/workers/tasks/train_ml_models.py

ML model training pipeline (Celery task):

-   Fetch historical data
-   Train health predictor
-   Save model to local storage (Docker volume)
-   Update model registry u database
-   Performance metrics tracking

#### [NEW] backend/app/api/v1/endpoints/ml.py

ML prediction endpoints:

-   `GET /api/v1/ml/predictions/{lsoa_code}` - Latest predictions
-   `GET /api/v1/ml/predictions/forecast` - Demand forecast
-   `POST /api/v1/ml/predictions/refresh` - Trigger refresh
-   `GET /api/v1/ml/models` - List available models
-   `GET /api/v1/ml/models/{id}/performance` - Model metrics

#### [NEW] backend/app/api/v1/endpoints/chat.py

AI Chat Assistant endpoints:

-   `POST /api/v1/chat/` - Send message
-   `GET /api/v1/chat/conversations` - List conversations
-   `GET /api/v1/chat/conversations/{id}/messages` - Get history
-   `DELETE /api/v1/chat/conversations/{id}` - Delete conversation

#### [NEW] backend/app/api/v1/endpoints/insights.py

AI-powered insights endpoints:

-   `POST /api/v1/insights/equity-summary` - Generate equity report summary
-   `POST /api/v1/insights/lsoa-explanation/{code}` - LSOA explanation
-   `POST /api/v1/insights/policy-recommendations` - Policy recommendations

#### [NEW] backend/app/models/ml.py

SQLAlchemy models for ML:

-   `MLModel` - model metadata, versioning, GCS paths
-   `MLPrediction` - prediction results, confidence intervals
-   `ChatConversation` - chat sessions
-   `ChatMessage` - individual messages sa RAG context

#### [NEW] data/scripts/generate_synthetic_training_data.py

Synthetic training data generator:

-   3 years of monthly health data za 500 LSOA
-   Realistic seasonal trends
-   Simulated intervention effects
-   Forward-looking target variables
-   CSV export za ML training

* * * * *

### Frontend AI Components

#### [NEW] frontend/src/components/ai/ChatWidget.tsx

AI Chat Widget component:

-   Fixed position chat interface
-   Message history display
-   Real-time message sending
-   Conversation persistence
-   Loading states

#### [NEW] frontend/src/components/dashboard/MLInsightsPanel.tsx

ML Insights display panel:

-   6-month forecast visualization
-   Confidence interval display
-   Natural language explanation (Gemini-generated)
-   Top risk factors breakdown
-   Feature importance chart

#### [NEW] frontend/src/api/endpoints/ai.ts

Frontend API client za AI features:

-   Chat message sending
-   ML predictions fetching
-   Insights generation
-   TypeScript types za all responses

* * * * *

### API Endpoints

#### [NEW] backend/app/api/v1/endpoints/lsoa.py

LSOA geographic endpoints:

-   `GET /api/v1/lsoa/` - List LSOA sa filterima
-   `GET /api/v1/lsoa/{code}` - Single LSOA details
-   `GET /api/v1/lsoa/{code}/geojson` - GeoJSON za mapu
-   `GET /api/v1/lsoa/search` - Postcode/name search
-   `GET /api/v1/lsoa/within-bounds` - Viewport filtering

#### [NEW] backend/app/api/v1/endpoints/priorities.py

DEX priority endpoints:

-   `GET /api/v1/priorities/` - List current priorities
-   `GET /api/v1/priorities/{code}` - LSOA priority
-   `GET /api/v1/priorities/{code}/history` - Historical scores
-   `GET /api/v1/priorities/{code}/explain` - Detailed explanation
-   `POST /api/v1/priorities/recalculate` - Trigger recalc (admin)

#### [NEW] backend/app/api/v1/endpoints/routes.py

Route planning endpoints:

-   `GET /api/v1/routes/plans` - List route plans
-   `POST /api/v1/routes/plans` - Create plan
-   `POST /api/v1/routes/plans/{id}/optimize` - Run optimization
-   `PUT /api/v1/routes/plans/{id}/approve` - Approve plan
-   `GET /api/v1/routes/assignments/{id}/stops` - Stop details

#### [NEW] backend/app/api/v1/endpoints/dashboard.py

Dashboard data endpoints:

-   `GET /api/v1/dashboard/summary` - KPI summary
-   `GET /api/v1/dashboard/heatmap/priority` - Priority heatmap data
-   `GET /api/v1/dashboard/equity-coverage` - Core20 coverage %

* * * * *

### Frontend Component

#### [NEW] frontend/package.json

Frontend dependencies:

-   Vite 5 + React 18 + TypeScript
-   React Router DOM v6
-   MapLibre GL JS (open-source maps)
-   Zustand (state management)
-   TanStack Query (data fetching)
-   TailwindCSS (styling)
-   Recharts (KPI charts)
-   shadcn/ui (component library)
-   @react-oauth/google (Google Sign-In)

#### [NEW] frontend/src/main.tsx

Vite entry point:

-   React root rendering
-   Router provider
-   Query client provider
-   Global providers

#### [NEW] frontend/src/App.tsx

Main app component:

-   Route definitions
-   Layout wrapper
-   Auth guards:
-   Global styles
-   Authentication provider
-   Query client provider
-   Navigation sidebar

#### [NEW] frontend/src/pages/DashboardPage.tsx

Strategic Planning Dashboard page:

-   Priority heatmap
-   KPI cards (equity coverage, total visits)
-   LSOA search
-   Filter controls
-   ML Insights Panel integration

#### [NEW] frontend/src/pages/RoutesPage.tsx

Operations Manager Route Planning page:

-   Route plan list
-   Create/optimize controls
-   Resource management
-   Route timeline visualization

#### [NEW] frontend/src/components/auth/GoogleSignIn.tsx

Google OAuth 2.0 authentication:

-   Google Sign-In button
-   OAuth flow handling
-   JWT token exchange
-   User profile fetch

#### [NEW] frontend/src/components/maps/MapContainer.tsx

MapLibre GL map component:

-   Base map layer
-   LSOA polygon layer
-   Interactive tooltips
-   Viewport state management

#### [NEW] frontend/src/components/maps/HeatmapLayer.tsx

Priority heatmap visualization:

-   Color gradient by priority score
-   LSOA polygon fill
-   Legend component
-   Choropleth styling

#### [NEW] frontend/src/components/maps/RouteLayer.tsx

Route line visualization:

-   LineString geometry rendering
-   Stop markers
-   Resource color coding
-   Highlight on hover

#### [NEW] frontend/src/api/client.ts

API client setup:

-   Axios instance sa base URL
-   Request/response interceptors
-   JWT token handling
-   Error handling

* * * * *

### Background Jobs

#### [NEW] backend/app/workers/celery_app.py

Celery configuration:

-   Redis broker
-   Task routing
-   Result backend

#### [NEW] backend/app/workers/tasks/recalculate_priorities.py

Background task za DEX recalculation:

-   Load latest data for all LSOA
-   Calculate priorities batch-wise
-   Save results
-   Send notifications

#### [NEW] backend/app/workers/tasks/generate_routes.py

Async route optimization task:

-   Long-running optimization
-   Progress updates via WebSocket
-   Result persistence

* * * * *

### Infrastructure

#### [NEW] docker-compose.prod.yml

Production Docker Compose setup za Hetzner deployment:

-   PostgreSQL 15 + PostGIS (persistent volume)
-   Redis (persistent volume)
-   FastAPI backend (multiple replicas)
-   React Router frontend (nginx served)
-   Nginx reverse proxy
-   Certbot za SSL certificates
-   Automated backups

#### [NEW] infrastructure/hetzner/setup.sh

Hetzner server setup script:

-   Docker + Docker Compose installation
-   Firewall configuration (ufw)
-   SSL certificate setup (Let's Encrypt)
-   PostgreSQL volume initialization
-   Backup cron jobs

#### [NEW] infrastructure/nginx/nginx.conf

Nginx configuration:

-   Reverse proxy za backend API
-   Static file serving za frontend
-   SSL/TLS configuration
-   Rate limiting
-   Gzip compression

#### [NEW] infrastructure/backup/backup.sh

Automated backup script:

-   PostgreSQL database dumps
-   ML model backups
-   Upload to Hetzner Storage Box ili S3-compatible storage
-   Retention policy (30 days)

* * * * *

### Data Scripts

#### [NEW] data/scripts/download_imd.py

Script za download IMD 2019 data:

-   ONS API ili manual download
-   Save to `data/raw/imd/`

#### [NEW] data/scripts/download_lsoa_boundaries.py

Download LSOA boundaries:

-   ONS Geography boundary files
-   Save GeoJSON to `data/raw/geography/`

#### [NEW] data/scripts/seed_database.py

Database seeding script:

-   Call importers
-   Create sample resources
-   Create test users
-   Generate sample routes

* * * * *

Verification Plan
-----------------

### Automated Tests

**Backend Tests:**

# DEX engine unit tests

pytest  backend/tests/unit/test_dex_engine.py  -v

# VRP solver tests

pytest  backend/tests/unit/test_vrp_solver.py  -v

# API integration tests

pytest  backend/tests/integration/test_api_routes.py  -v

# Coverage report

pytest  --cov=app  --cov-report=html

**Frontend Tests:**

# Component tests

npm  test

# E2E tests (Playwright)

npm  run  test:e2e

### Manual Verification

**1\. DEX Engine Validation:**

-   [ ]  Load sample LSOA data
-   [ ]  Verify priority scores match expected ranges
-   [ ]  Check explanation text quality
-   [ ]  Test weight adjustments via admin UI

**2\. Route Optimization:**

-   [ ]  Create route plan sa 50+ visits
-   [ ]  Run optimization
-   [ ]  Verify Core20 areas prioritized
-   [ ]  Check time window compliance
-   [ ]  Validate equity coverage score

**3\. Map Visualization:**

-   [ ]  Load priority heatmap
-   [ ]  Verify color gradient correctness
-   [ ]  Test LSOA polygon tooltips
-   [ ]  Check route line rendering
-   [ ]  Test viewport filtering performance

**4\. Data Pipeline:**

-   [ ]  Run IMD importer
-   [ ]  Verify data loaded to database
-   [ ]  Check spatial queries work
-   [ ]  Validate materialized view refresh

**5\. NHS Compliance (MVP):**

-   [ ]  Audit log captures all actions
-   [ ]  JWT tokens expire correctly
-   [ ]  Google OAuth flow works
-   [ ]  Role-based access works
-   [ ]  EU hosting verified (Hetzner Germany)

### Performance Benchmarks (MVP)

-   Map rendering: < 2s za 1000+ LSOA polygons
-   Priority calculation: < 5s za sve LSOA (batch)
-   Route optimization: < 30s za 100 visits, 10 resources
-   API response time: p95 < 500ms

* * * * *

Post-MVP Enhancement: AI/ML Intelligence Layer
----------------------------------------------

Ova sekcija pokriva sve AI/ML komponente koje se implementiraju **nakon MVP validacije** (Phase 6).

### AI/ML Components

#### [NEW] backend/app/services/ml/health_predictor.py

ML model za predviđanje health outcomes:

-   RandomForest regressor za emergency admission prediction
-   Feature engineering (demographics, clinical, seasonal)
-   Confidence interval calculation
-   Feature importance za explainability
-   Model versioning i local storage (Docker volumes)

#### [NEW] backend/app/services/ml/demand_forecaster.py

Time-series forecasting za resource demand:

-   Prophet ili ARIMA model
-   Seasonal decomposition
-   Forecast sa confidence intervals
-   Resource allocation recommendations

#### [NEW] backend/app/services/llm/kimi_insights.py

Kimi-K2 Thinking Turbo API integration:

-   **Equity report narration** - auto-generated summaries
-   **LSOA insights generator** - natural language explanations
-   **Policy recommendations** - actionable insights
-   Prompt engineering za consistent outputs

#### [NEW] backend/app/services/llm/context_builder.py

RAG (Retrieval-Augmented Generation) context builder:

-   Query understanding
-   Relevant data retrieval from database
-   Context formatting za Kimi API prompts
-   Source tracking

#### [NEW] backend/app/workers/tasks/train_ml_models.py

ML model training pipeline (Celery task):

-   Fetch historical data
-   Train health predictor
-   Save model to local storage (Docker volume)
-   Update model registry u database
-   Performance metrics tracking

#### [NEW] backend/app/api/v1/endpoints/ml.py

ML prediction endpoints:

-   `GET /api/v1/ml/predictions/{lsoa_code}` - Latest predictions
-   `GET /api/v1/ml/predictions/forecast` - Demand forecast
-   `POST /api/v1/ml/predictions/refresh` - Trigger refresh
-   `GET /api/v1/ml/models` - List available models
-   `GET /api/v1/ml/models/{id}/performance` - Model metrics

#### [NEW] backend/app/api/v1/endpoints/chat.py

AI Chat Assistant endpoints:

-   `POST /api/v1/chat/` - Send message
-   `GET /api/v1/chat/conversations` - List conversations
-   `GET /api/v1/chat/conversations/{id}/messages` - Get history
-   `DELETE /api/v1/chat/conversations/{id}` - Delete conversation

#### [NEW] backend/app/api/v1/endpoints/insights.py

AI-powered insights endpoints:

-   `POST /api/v1/insights/equity-summary` - Generate equity report summary
-   `POST /api/v1/insights/lsoa-explanation/{code}` - LSOA explanation
-   `POST /api/v1/insights/policy-recommendations` - Policy recommendations

#### [NEW] backend/app/models/ml.py

SQLAlchemy models for ML (new database tables):

-   `MLModel` - model metadata, versioning, GCS paths
-   `MLPrediction` - prediction results, confidence intervals
-   `ChatConversation` - chat sessions
-   `ChatMessage` - individual messages sa RAG context

#### [NEW] data/scripts/generate_synthetic_training_data.py

Synthetic training data generator:

-   3 years of monthly health data za 500 LSOA
-   Realistic seasonal trends
-   Simulated intervention effects
-   Forward-looking target variables
-   CSV export za ML training

### AI Frontend Components

#### [NEW] frontend/src/components/ai/ChatWidget.tsx

AI Chat Widget component:

-   Fixed position chat interface
-   Message history display
-   Real-time message sending
-   Conversation persistence
-   Loading states

#### [NEW] frontend/src/components/dashboard/MLInsightsPanel.tsx

ML Insights display panel:

-   6-month forecast visualization
-   Confidence interval display
-   Natural language explanation (Kimi-generated)
-   Top risk factors breakdown
-   Feature importance chart

#### [NEW] frontend/src/api/endpoints/ai.ts

Frontend API client za AI features:

-   Chat message sending
-   ML predictions fetching
-   Insights generation
-   TypeScript types za all responses

### AI/ML Testing & Validation

**Post-MVP AI/ML Verification:**

-   [ ]  ML model training pipeline works end-to-end
-   [ ]  Predictions have reasonable accuracy (R² > 0.7)
-   [ ]  Kimi API generates coherent, actionable summaries
-   [ ]  Chat assistant responds accurately to domain questions
-   [ ]  Synthetic training data is realistic and balanced
-   [ ]  ML inference latency < 200ms per LSOA
-   [ ]  Kimi API response < 3s

**Additional Performance Benchmarks (Post-MVP):**

-   ML model training time: < 10 minutes for 500 LSOA × 36 months
-   Kimi API cost tracking and optimization
-   Model versioning and rollback functionality

* * * * *

Next Steps
----------

1.  **MVP Development (Phases 1-5)**:

    -   Phase 1: Foundation setup (backend, DB, auth)
    -   Phase 2: DEX Engine implementation
    -   Phase 3: Routing optimization (Google OR-Tools)
    -   Phase 4: Frontend web application
    -   Phase 5: Testing & Hetzner deployment
2.  **MVP Launch & Validation**:

    -   Deploy to staging environment
    -   User acceptance testing sa NHS stakeholders
    -   Gather feedback on core functionality
    -   Validate equity coverage algorithms
3.  **Post-MVP Enhancement (Phase 6)**:

    -   Kimi API integration
    -   ML predictive models
    -   AI Chat Assistant
    -   Advanced insights generation
4.  **Hetzner Setup Prerequisites**:

    -   Provision Hetzner dedicated server (Germany datacenter)
    -   Setup Docker + Docker Compose
    -   Configure domain & DNS
    -   Setup SSL certificates (Let's Encrypt)
    -   Configure automated backups