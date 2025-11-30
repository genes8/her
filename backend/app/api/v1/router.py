"""API v1 router - aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, lsoa, priorities, routes, dashboard

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# LSOA geographic data endpoints
api_router.include_router(
    lsoa.router,
    prefix="/lsoa",
    tags=["LSOA"],
)

# DEX priority endpoints
api_router.include_router(
    priorities.router,
    prefix="/priorities",
    tags=["Priorities"],
)

# Route planning endpoints
api_router.include_router(
    routes.router,
    prefix="/routes",
    tags=["Routes"],
)

# Dashboard data endpoints
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
)
