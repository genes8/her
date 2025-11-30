# HealthEquiRoute

NHS Health Equity Route Optimization Platform - A system for optimizing healthcare service delivery with a focus on equity (Core20PLUS5).

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
git clone <repository-url>
cd healthequiroute
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
healthequiroute/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Security, config
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   │   ├── dex_engine/ # Priority calculation
│   │   │   ├── routing/    # VRP optimization
│   │   │   └── data_ingestion/
│   │   └── workers/        # Celery tasks
│   ├── alembic/            # Database migrations
│   └── tests/
├── frontend/               # React TypeScript frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── api/
├── infrastructure/         # Deployment configs
├── data/                   # Data files
└── docker-compose.yml
```

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

## NHS Compliance

This application is designed with NHS compliance in mind:
- **GDPR/UK GDPR:** EU hosting (Hetzner Germany)
- **Audit Logging:** All user actions logged
- **RBAC:** Role-based access control
- **Encryption:** Data at rest and in transit
- **DPIA:** Documentation templates included

## License

Proprietary - NHS Use Only

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.
