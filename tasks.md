# HealthEquiRoute Development Plan

**Last Updated**: 2024-11-30

## MVP Scope (Phases 1-5)

Core functionality: Backend infrastructure, DEX Engine, Route optimization, Web frontend

---

## Faza 1: Foundation Setup (3-4 nedelje) - **IN PROGRESS**

### Project initialization
- [x] Create repository structure
- [x] Setup Docker Compose development environment
- [x] Configure PostgreSQL + PostGIS database ✅ (lokalno postgresql@17)
- [ ] Setup Redis for caching

### Database schema implementation
- [x] Create Alembic migrations (001_initial_schema.py)
- [x] Implement all core tables from PRD (18 tabela)
- [x] Create indexes and spatial indexes
- [ ] Add materialized views (mv_lsoa_dashboard)

### Basic backend structure
- [x] Setup FastAPI application (main.py)
- [x] Configure settings management (config.py)
- [x] Implement JWT authentication
- [ ] Implement Google OAuth integration
- [x] Setup SQLAlchemy models

### Synthetic data pipeline
- [x] LSOA boundary generator (synthetic_generator.py)
- [x] IMD data generator (synthetic)
- [x] Census demographic data generator
- [x] Clinical data generator
- [x] Accessibility data calculator

### API Endpoints (Basic)
- [x] Auth endpoints (auth.py)
- [x] LSOA endpoints (lsoa.py)
- [x] Priorities endpoints (priorities.py)
- [x] Routes endpoints (routes.py)
- [x] Dashboard endpoints (dashboard.py)

### 🎯 NEXT STEPS (Faza 1)
- [ ] **Pokrenuti synthetic data generator i napuniti bazu**
- [ ] Setup Redis lokalno
- [ ] Testirati API endpoints
- [ ] Dodati materialized view za dashboard

---

## Faza 2: DEX Engine Core (4-5 nedelja)

### DEX engine implementation
- [ ] Clinical risk fuzzifier
- [ ] Social vulnerability scorer
- [ ] Accessibility evaluator
- [ ] Rule-based aggregation engine
- [ ] Explanation generator

### DEX API endpoints
- [ ] Priority calculation API
- [ ] LSOA priority listing
- [ ] Historical priority tracking
- [ ] Explanation endpoints

### Admin configuration
- [ ] DEX model config management
- [ ] Weight adjustment UI
- [ ] Rule editor

### Background jobs
- [ ] Celery/Redis setup
- [ ] Priority recalculation workers
- [ ] Scheduled data sync

---

## Faza 3: Routing Engine (4-5 nedelja)

### VRP solver integration
- [ ] Google OR-Tools setup
- [ ] Distance matrix calculator
- [ ] Travel time estimator
- [ ] Multi-vehicle routing solver

### Routing optimization
- [ ] Priority-weighted optimization
- [ ] Resource constraint handling
- [ ] Time window support
- [ ] Skill matching

### Route management API
- [ ] Create route plan endpoint
- [ ] Optimize route endpoint
- [ ] Route assignment management
- [ ] Stop sequencing

### Route execution
- [ ] Real-time status updates
- [ ] Actual vs. planned tracking
- [ ] Route modifications

---

## Faza 4: Frontend Development (5-6 nedelja)

### Frontend foundation
- [ ] Vite + React + TypeScript setup
- [ ] React Router configuration
- [ ] API client layer
- [ ] State management (Zustand)
- [ ] Google OAuth integration

### Authentication UI
- [ ] Login page
- [ ] Google Sign-In button
- [ ] Protected routes

### Dashboard components
- [ ] Strategic Planning dashboard
- [ ] Operations Manager dashboard
- [ ] KPI cards
- [ ] Priority panels

### Map visualization
- [ ] MapLibre GL JS setup
- [ ] LSOA polygon layer
- [ ] Priority heatmap layer
- [ ] Route visualization layer
- [ ] Interactive tooltips

### Route planning UI
- [ ] Resource management
- [ ] Visit location management
- [ ] Route optimizer controls
- [ ] Timeline visualization

### Admin UI
- [ ] DEX config editor
- [ ] User management
- [ ] Audit log viewer

---

## Faza 5: Testing, Deployment & MVP Launch (4-5 nedelja)

### Unit tests
- [ ] DEX engine tests
- [ ] VRP solver tests
- [ ] API endpoint tests

### Integration tests
- [ ] End-to-end route optimization
- [ ] Data pipeline tests
- [ ] Authentication flow tests (JWT + Google OAuth)

### Performance testing
- [ ] Large dataset handling
- [ ] Concurrent user load
- [ ] Map rendering performance

### NHS compliance
- [ ] Security audit
- [ ] DSPT requirements documentation
- [ ] DPIA documentation
- [ ] DCB0129 compliance check

### Infrastructure deployment
- [ ] Hetzner server setup (Docker + Docker Compose)
- [ ] PostgreSQL + PostGIS deployment (Docker volume)
- [ ] Redis deployment (Docker volume)
- [ ] Nginx reverse proxy configuration
- [ ] SSL certificate setup (Let's Encrypt)
- [ ] Automated backup configuration

### CI/CD pipeline
- [ ] GitHub Actions workflows
- [ ] Automated testing
- [ ] Docker image building
- [ ] Deployment automation

### Monitoring & logging
- [ ] Application logging (Docker logs)
- [ ] Performance metrics
- [ ] Error tracking (Sentry)
- [ ] Backup monitoring

---

## 🎯 MVP COMPLETE - Production Ready

---

## Post-MVP Enhancement (Phase 6)

Advanced AI/ML features to be implemented after MVP validation

---

## Faza 6: AI/ML Intelligence Module (5-6 nedelja)

### ML infrastructure setup
- [ ] Local ML model storage (Docker volumes)
- [ ] Model versioning strategy
- [ ] Synthetic training data generator

### Predictive Analytics
- [ ] Health outcome predictor (RandomForest)
- [ ] Demand forecasting model
- [ ] Model training pipeline (Celery task)
- [ ] Prediction API endpoints
- [ ] Feature engineering pipeline
- [ ] Model performance tracking

### Kimi-K2 LLM Integration
- [ ] Kimi API client setup
- [ ] Equity report summarization
- [ ] LSOA insight generator
- [ ] Policy recommendation engine

### AI Chat Assistant
- [ ] Chat conversation schema (new tables)
- [ ] RAG context builder
- [ ] Chat API endpoints
- [ ] Real-time chat interface

### AI Frontend Components
- [ ] AI Chat Widget
- [ ] ML Insights Panel
- [ ] Prediction visualizations
- [ ] LLM-generated summaries display

### ML Testing & Validation
- [ ] ML model training pipeline tests
- [ ] Prediction accuracy validation
- [ ] Kimi API integration tests
- [ ] Chat assistant response quality tests
- [ ] ML inference performance benchmarks

---

## Mobile/PWA (Optional, post-MVP)

- [ ] React Native or PWA setup
- [ ] Field worker route view
- [ ] Offline capability
- [ ] Real-time status updates

---

## Progress Summary

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Foundation | 🟡 In Progress | ~80% |
| Phase 2: DEX Engine | ⚪ Not Started | 0% |
| Phase 3: Routing | ⚪ Not Started | 0% |
| Phase 4: Frontend | ⚪ Not Started | 0% |
| Phase 5: Deployment | ⚪ Not Started | 0% |
| Phase 6: AI/ML | ⚪ Post-MVP | 0% |
