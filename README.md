# HealthEquiRoute

NHS Health Equity Route Optimization Platform - A system for optimizing healthcare service delivery with a focus on equity (Core20PLUS5).

## 📊 Current Status

**Version**: v0.1.0-alpha | **Status**: MVP Development | **Progress**: 65%

- ✅ **Backend Foundation**: FastAPI + PostgreSQL + PostGIS (80% complete)
- ✅ **Frontend Foundation**: React Router + TypeScript (60% complete) 
- ✅ **Database Schema**: 18 tables with spatial extensions (90% complete)
- 🔴 **DEX Engine**: Priority calculation system (0% complete)
- 🔴 **Routing Engine**: Google OR-Tools VRP solver (0% complete)
- 🟡 **Deployment**: Docker + Hetzner configuration (70% complete)

**Repository**: https://github.com/genes8/her  
**Documentation**: See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for detailed progress report

---

## Overview

HealthEquiRoute is a modular monolith application designed to help NHS organizations:
- **Prioritize** healthcare visits based on clinical need, social vulnerability, and accessibility
- **Optimize** routes for community health workers using the DEX (Decision EXpert) engine
- **Visualize** health equity data on interactive maps
- **Track** impact on reducing health inequalities

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11 + FastAPI |
| Database | PostgreSQL 15 + PostGIS |
| Cache | Redis 7 |
| Frontend | React 18 + TypeScript + Vite |
| Maps | MapLibre GL JS |
| Routing | Google OR-Tools |
| Auth | JWT + Google OAuth 2.0 |
| Deployment | Docker + Hetzner |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15 (via Docker or native)
- Redis 7 (via Docker or native)

### Development Setup

1. **Clone and setup environment:**
```bash
git clone https://github.com/genes8/her.git
cd her
cp .env.example .env
# Edit .env with your configuration
```

2. **Start infrastructure services:**
```bash
docker compose up -d postgres redis pgadmin
```

3. **Setup backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
```

4. **Setup frontend:**
```bash
cd frontend
npm install
```

5. **Run development servers:**
```bash
# Terminal 1 - Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

Or use the Makefile:
```bash
make setup
make dev
```

### Access Points

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050

## Project Structure

```
her/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API endpoints (25+ implemented)
│   │   ├── core/           # Security, config
│   │   ├── models/         # SQLAlchemy models (6 implemented)
│   │   ├── services/       # Business logic
│   │   │   ├── dex_engine/ # Priority calculation (TODO)
│   │   │   ├── routing/    # VRP optimization (TODO)
│   │   │   └── data_ingestion/ # Synthetic data generators
│   │   └── workers/        # Celery tasks (TODO)
│   ├── alembic/            # Database migrations
│   └── tests/              # Tests (TODO)
├── frontend/               # React TypeScript frontend
│   └── app/
│       ├── routes/         # React Router pages (8 implemented)
│       ├── components/     # UI components (20+ implemented)
│       ├── stores/         # Zustand state management
│       └── types/          # TypeScript definitions
├── infrastructure/         # Deployment configs
│   ├── nginx/             # Nginx configuration
│   └── postgres/          # Database initialization
├── data/                   # Data files and scripts
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── PROJECT_STATUS.md       # 📊 Detailed progress report
├── tasks.md               # 📋 Development tasks and timeline
└── implementation-plan.md  # 📐 Technical specifications
```

## 🚀 Implementation Progress

### ✅ Completed Components

#### Backend (FastAPI)
- **API Endpoints**: 25+ endpoints for auth, LSOA, priorities, routes, dashboard
- **Database Models**: 6 SQLAlchemy models with relationships
- **Authentication**: JWT-based security with password hashing
- **Data Generation**: Synthetic data generators for LSOA, IMD, demographics, clinical data
- **Migrations**: Alembic database migrations with PostGIS support

#### Frontend (React Router + TypeScript)
- **Routing**: 8 page routes with React Router v6
- **Components**: 20+ reusable UI components (layout, dashboard, forms)
- **State Management**: Zustand stores for authentication and dashboard state
- **TypeScript**: Full type safety with custom type definitions
- **UI Framework**: TailwindCSS with custom component library

#### Database (PostgreSQL + PostGIS)
- **Schema**: 18 tables including geographic, clinical, and organizational data
- **Spatial Extensions**: PostGIS for geographic queries and indexing
- **Relationships**: Complex foreign key relationships with cascade deletes
- **Indexes**: Optimized spatial and performance indexes

#### Infrastructure
- **Docker**: Multi-container development environment
- **PostgreSQL**: Database service with persistent volumes
- **Redis**: Caching service (configured, needs local setup)
- **Nginx**: Reverse proxy configuration for production

### 🔴 Missing Core Components

#### DEX Engine (Decision Engine)
```python
# Critical for MVP - Not implemented
backend/app/services/dex_engine/
├── engine.py              # Multi-criteria decision analysis
├── fuzzifier.py           # Numeric → Category mapping  
├── rules.py              # Rule-based aggregation
├── explainer.py          # Explanation generation
└── config_loader.py      # Dynamic rule configuration
```

#### Routing Engine (Google OR-Tools)
```python
# Critical for MVP - Not implemented
backend/app/services/routing/
├── vrp_solver.py         # Vehicle Routing Problem solver
├── optimizer.py          # Route optimization orchestrator
├── distance_matrix.py    # Travel time calculations
└── clustering.py         # Location clustering
```

#### Map Integration (MapLibre GL JS)
```typescript
// Critical for MVP - Not implemented
frontend/app/components/maps/
├── MapContainer.tsx      # Base map component
├── HeatmapLayer.tsx      # Priority heatmap visualization
├── RouteLayer.tsx        # Route line rendering
└── LSOAPolygons.tsx      # Geographic boundary display
```

### 🟡 Partially Implemented

#### Authentication
- ✅ JWT token generation and validation
- ✅ Password hashing with bcrypt
- 🔴 Google OAuth 2.0 integration (client setup needed)
- 🔴 Frontend auth state management

#### Testing
- ✅ pytest configuration for backend
- ✅ Test database setup
- 🔴 Unit test implementation (0% coverage)
- 🔴 Integration tests (not implemented)

#### Background Jobs
- ✅ Celery configuration
- 🔴 Redis setup (local installation needed)
- 🔴 Background task implementation

## 📋 Development Tasks

### Immediate Priorities (Next 2 weeks)
1. **Redis Setup**: Install and configure Redis locally
2. **Database Seeding**: Run synthetic data generators to populate database
3. **Google OAuth**: Complete authentication integration
4. **Basic Testing**: Implement unit tests for core components

### Short Term (Next 4-6 weeks)
1. **DEX Engine**: Implement priority calculation algorithms
2. **Map Integration**: Add MapLibre GL JS with LSOA visualization
3. **API Testing**: Comprehensive endpoint testing
4. **Frontend Polish**: Complete dashboard and map interfaces

### Medium Term (Next 8-10 weeks)
1. **Routing Engine**: Google OR-Tools VRP solver
2. **Advanced Frontend**: Real-time updates, advanced filtering
3. **Performance Optimization**: Database query optimization
4. **Deployment**: Hetzner production deployment

## Development

### Running Tests
```bash
make test          # All tests
make test-unit     # Unit tests only
make test-cov      # With coverage report
```

### Database Migrations
```bash
make migrate                    # Apply migrations
make migrate-new NAME="add_users"  # Create new migration
```

### Code Quality
```bash
make lint    # Run linters
make format  # Format code
```

### Data Seeding
```bash
make seed    # Populate database with synthetic data
```

## 📊 Metrics & KPIs

### Code Metrics
- **Backend**: ~15,000 lines Python code
- **Frontend**: ~8,000 lines TypeScript code
- **Database**: 18 tables, 50+ indexes
- **API Endpoints**: 25+ implemented
- **Components**: 20+ React components
- **Test Coverage**: 0% (target: 80%)

### Performance Targets
- Map rendering: < 2s for 1000+ LSOA polygons
- Priority calculation: < 5s for all LSOA
- Route optimization: < 30s for 100 visits
- API response time: p95 < 500ms

## NHS Compliance

This application is designed with NHS compliance in mind:
- **GDPR/UK GDPR:** EU hosting (Hetzner Germany)
- **Audit Logging:** All user actions logged
- **RBAC:** Role-based access control
- **Encryption:** Data at rest and in transit
- **DPIA:** Documentation templates included

## 🎯 MVP Success Criteria

### Technical Requirements
- [ ] 1000+ LSOA areas with synthetic data
- [ ] DEX priority scores calculated for all areas
- [ ] Route optimization working for 50+ visits
- [ ] Interactive map with priority heatmap
- [ ] User authentication and authorization
- [ ] Basic dashboard with KPI metrics

### User Requirements
- [ ] Strategic planner can view equity data
- [ ] Operations manager can optimize routes
- [ ] Field worker can view assigned routes
- [ ] Admin can configure DEX parameters
- [ ] System passes NHS security review

## 📞 Support & Documentation

- **Documentation**: 
  - [PROJECT_STATUS.md](./PROJECT_STATUS.md) - Detailed progress report
  - [tasks.md](./tasks.md) - Development tasks and timeline
  - [implementation-plan.md](./implementation-plan.md) - Technical specifications
- **Repository**: https://github.com/genes8/her
- **API Documentation**: http://localhost:8000/docs (when running)
- **Issues**: Report bugs and feature requests on GitHub

## License

Proprietary - NHS Use Only

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

**Last Updated**: 1. Decembar 2025  
**Version**: v0.1.0-alpha  
**Next Milestone**: Phase 1 Foundation Complete (15. Decembar 2025)
