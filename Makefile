# ============================================
# HEALTHEQUIROUTE MAKEFILE
# ============================================

.PHONY: help setup dev stop clean migrate seed test lint format

# Default target
help:
	@echo "HealthEquiRoute Development Commands"
	@echo "====================================="
	@echo ""
	@echo "Setup & Development:"
	@echo "  make setup      - Initial project setup (install dependencies)"
	@echo "  make dev        - Start development environment"
	@echo "  make stop       - Stop all services"
	@echo "  make clean      - Clean up containers and volumes"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Run database migrations"
	@echo "  make migrate-new NAME=<name> - Create new migration"
	@echo "  make seed       - Seed database with sample data"
	@echo "  make db-reset   - Reset database (WARNING: destroys data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test       - Run all tests"
	@echo "  make test-unit  - Run unit tests only"
	@echo "  make test-int   - Run integration tests only"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo ""
	@echo "Production:"
	@echo "  make build      - Build production Docker images"
	@echo "  make deploy     - Deploy to production"

# ============================================
# SETUP
# ============================================

setup: setup-backend setup-frontend
	@echo "✅ Setup complete!"
	@echo "📝 Don't forget to copy .env.example to .env and configure it"

setup-backend:
	@echo "🐍 Setting up Python backend..."
	cd backend && python3 -m venv .venv
	cd backend && .venv/bin/pip install --upgrade pip
	cd backend && .venv/bin/pip install -e ".[dev]"

setup-frontend:
	@echo "⚛️  Setting up React frontend..."
	cd frontend && npm install

# ============================================
# DEVELOPMENT
# ============================================

dev: dev-services dev-backend dev-frontend
	@echo "🚀 Development environment started!"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:5173"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo "   pgAdmin:  http://localhost:5050"

dev-services:
	@echo "🐳 Starting PostgreSQL and Redis..."
	docker compose up -d postgres redis pgadmin

dev-backend:
	@echo "🐍 Starting FastAPI backend..."
	cd backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

dev-frontend:
	@echo "⚛️  Starting React frontend..."
	cd frontend && npm run dev &

stop:
	@echo "🛑 Stopping all services..."
	-pkill -f "uvicorn app.main:app" || true
	-pkill -f "vite" || true
	docker compose down

clean:
	@echo "🧹 Cleaning up..."
	docker compose down -v --remove-orphans
	rm -rf backend/.venv
	rm -rf frontend/node_modules
	rm -rf backend/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ============================================
# DATABASE
# ============================================

migrate:
	@echo "📦 Running database migrations..."
	cd backend && .venv/bin/alembic upgrade head

migrate-new:
	@echo "📝 Creating new migration: $(NAME)"
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(NAME)"

migrate-down:
	@echo "⬇️  Rolling back last migration..."
	cd backend && .venv/bin/alembic downgrade -1

seed:
	@echo "🌱 Seeding database..."
	cd backend && .venv/bin/python -m app.services.data_ingestion.seed_database

db-reset:
	@echo "⚠️  Resetting database..."
	docker compose down -v postgres
	docker compose up -d postgres
	sleep 5
	$(MAKE) migrate
	$(MAKE) seed

# ============================================
# TESTING
# ============================================

test:
	@echo "🧪 Running all tests..."
	cd backend && .venv/bin/pytest -v

test-unit:
	@echo "🧪 Running unit tests..."
	cd backend && .venv/bin/pytest tests/unit -v

test-int:
	@echo "🧪 Running integration tests..."
	cd backend && .venv/bin/pytest tests/integration -v

test-cov:
	@echo "📊 Running tests with coverage..."
	cd backend && .venv/bin/pytest --cov=app --cov-report=html --cov-report=term

# ============================================
# CODE QUALITY
# ============================================

lint:
	@echo "🔍 Running linters..."
	cd backend && .venv/bin/ruff check app tests
	cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	cd backend && .venv/bin/ruff format app tests
	cd frontend && npm run format

# ============================================
# PRODUCTION
# ============================================

build:
	@echo "🏗️  Building production images..."
	docker compose -f docker-compose.prod.yml build

deploy:
	@echo "🚀 Deploying to production..."
	docker compose -f docker-compose.prod.yml up -d

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend
