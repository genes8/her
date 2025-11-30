"""Route planning endpoints."""

from datetime import date, time
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================


class RoutePlanBase(BaseModel):
    """Base route plan schema."""

    plan_date: date
    team_id: UUID | None = None


class RoutePlanCreate(RoutePlanBase):
    """Route plan creation schema."""

    visit_location_ids: list[UUID]
    resource_ids: list[UUID]
    optimization_config: dict | None = None


class RoutePlanResponse(RoutePlanBase):
    """Route plan response schema."""

    id: UUID
    status: str  # DRAFT, OPTIMIZED, APPROVED, IN_PROGRESS, COMPLETED
    total_resources: int | None = None
    total_visits: int | None = None
    total_distance_km: float | None = None
    total_duration_minutes: int | None = None
    equity_coverage_score: float | None = None
    created_at: str


class RouteAssignmentResponse(BaseModel):
    """Route assignment response schema."""

    id: UUID
    resource_id: UUID
    resource_name: str
    sequence_count: int
    total_distance_km: float
    total_duration_minutes: int
    estimated_start_time: time | None = None
    estimated_end_time: time | None = None
    core20_visits_count: int


class RouteStopResponse(BaseModel):
    """Route stop response schema."""

    id: UUID
    stop_sequence: int
    visit_location_id: UUID
    location_name: str
    address: str
    estimated_arrival: time | None = None
    estimated_departure: time | None = None
    priority_score: float
    priority_label: str
    status: str  # PENDING, COMPLETED, SKIPPED, RESCHEDULED


class OptimizeRequest(BaseModel):
    """Route optimization request."""

    max_time_seconds: int = 30
    prioritize_core20: bool = True
    balance_workload: bool = True


class OptimizeResponse(BaseModel):
    """Route optimization response."""

    task_id: str
    status: str
    message: str


class RoutePlanListResponse(BaseModel):
    """Paginated route plan list response."""

    items: list[RoutePlanResponse]
    total: int
    page: int
    page_size: int


# ============================================
# ENDPOINTS
# ============================================


@router.get("/plans", response_model=RoutePlanListResponse)
async def list_route_plans(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    team_id: UUID | None = None,
) -> RoutePlanListResponse:
    """
    List route plans with filtering.
    """
    # TODO: Implement database query
    return RoutePlanListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.post("/plans", response_model=RoutePlanResponse, status_code=201)
async def create_route_plan(plan_data: RoutePlanCreate) -> RoutePlanResponse:
    """
    Create a new route plan.

    Initially in DRAFT status until optimization is run.
    """
    # TODO: Implement database insert
    from app.core.exceptions import ValidationError

    raise ValidationError("Route plan creation not yet implemented")


@router.get("/plans/{plan_id}", response_model=RoutePlanResponse)
async def get_route_plan(plan_id: UUID) -> RoutePlanResponse:
    """
    Get route plan details.
    """
    # TODO: Implement database query
    from app.core.exceptions import NotFoundError

    raise NotFoundError("Route plan", str(plan_id))


@router.post("/plans/{plan_id}/optimize", response_model=OptimizeResponse)
async def optimize_route_plan(
    plan_id: UUID,
    request: OptimizeRequest,
) -> OptimizeResponse:
    """
    Run VRP optimization on a route plan.

    Starts a background task using Google OR-Tools.
    """
    # TODO: Implement Celery task trigger
    return OptimizeResponse(
        task_id="pending",
        status="queued",
        message="Route optimization queued",
    )


@router.put("/plans/{plan_id}/approve", response_model=RoutePlanResponse)
async def approve_route_plan(plan_id: UUID) -> RoutePlanResponse:
    """
    Approve an optimized route plan.

    Changes status from OPTIMIZED to APPROVED.
    """
    # TODO: Implement status update
    from app.core.exceptions import NotFoundError

    raise NotFoundError("Route plan", str(plan_id))


@router.get("/plans/{plan_id}/assignments", response_model=list[RouteAssignmentResponse])
async def get_route_assignments(plan_id: UUID) -> list[RouteAssignmentResponse]:
    """
    Get all route assignments for a plan.
    """
    # TODO: Implement database query
    return []


@router.get("/assignments/{assignment_id}/stops", response_model=list[RouteStopResponse])
async def get_route_stops(assignment_id: UUID) -> list[RouteStopResponse]:
    """
    Get all stops for a route assignment.

    Returns stops in sequence order.
    """
    # TODO: Implement database query
    return []


@router.put("/stops/{stop_id}/status")
async def update_stop_status(
    stop_id: UUID,
    status: str,
    notes: str | None = None,
) -> RouteStopResponse:
    """
    Update stop status (for field workers).

    Valid statuses: PENDING, COMPLETED, SKIPPED, RESCHEDULED
    """
    # TODO: Implement status update
    from app.core.exceptions import NotFoundError

    raise NotFoundError("Route stop", str(stop_id))
