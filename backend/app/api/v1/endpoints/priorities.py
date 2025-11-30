"""DEX priority score endpoints."""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================


class PriorityScoreBase(BaseModel):
    """Base priority score schema."""

    lsoa_code: str
    priority_score: float
    priority_label: str  # URGENT, HIGH, MEDIUM, ROUTINE


class PriorityScoreResponse(PriorityScoreBase):
    """Priority score response schema."""

    id: UUID
    calculation_date: date
    model_version: str

    # Component scores
    clinical_risk_score: float
    social_vulnerability_score: float
    accessibility_score: float


class PriorityExplanation(BaseModel):
    """Detailed priority explanation schema."""

    lsoa_code: str
    priority_score: float
    priority_label: str
    explanation_text: str
    contributing_factors: dict

    # Flags
    requires_translator: bool = False
    requires_specialist: bool = False
    min_visit_time_minutes: int = 15


class PriorityHistoryItem(BaseModel):
    """Historical priority score item."""

    calculation_date: date
    priority_score: float
    priority_label: str
    model_version: str


class PriorityListResponse(BaseModel):
    """Paginated priority list response."""

    items: list[PriorityScoreResponse]
    total: int
    page: int
    page_size: int


class RecalculateRequest(BaseModel):
    """Priority recalculation request."""

    lsoa_codes: list[str] | None = None  # None = all LSOA
    force: bool = False  # Recalculate even if recent


class RecalculateResponse(BaseModel):
    """Priority recalculation response."""

    task_id: str
    status: str
    message: str


# ============================================
# ENDPOINTS
# ============================================


@router.get("/", response_model=PriorityListResponse)
async def list_priorities(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    priority_label: str | None = None,
    min_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    max_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    is_core20: bool | None = None,
    icb_code: str | None = None,
    sort_by: str = "priority_score",
    sort_order: str = "desc",
) -> PriorityListResponse:
    """
    List current priority scores with filtering.

    - **priority_label**: Filter by URGENT, HIGH, MEDIUM, ROUTINE
    - **min_score/max_score**: Filter by score range
    - **is_core20**: Filter by Core20 status
    - **icb_code**: Filter by Integrated Care Board
    """
    # TODO: Implement database query
    return PriorityListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.get("/summary")
async def get_priority_summary(
    icb_code: str | None = None,
) -> dict:
    """
    Get summary statistics for priorities.

    Returns counts by priority label and Core20 coverage.
    """
    # TODO: Implement aggregation query
    return {
        "total_lsoa": 0,
        "by_label": {
            "URGENT": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "ROUTINE": 0,
        },
        "core20_count": 0,
        "core20_percentage": 0.0,
        "average_score": 0.0,
    }


@router.get("/{lsoa_code}", response_model=PriorityScoreResponse)
async def get_priority(lsoa_code: str) -> PriorityScoreResponse:
    """
    Get current priority score for an LSOA.
    """
    # TODO: Implement database query
    from app.core.exceptions import NotFoundError

    raise NotFoundError("Priority score", lsoa_code)


@router.get("/{lsoa_code}/explain", response_model=PriorityExplanation)
async def explain_priority(lsoa_code: str) -> PriorityExplanation:
    """
    Get detailed explanation for an LSOA's priority score.

    Includes contributing factors and recommendations.
    """
    # TODO: Implement with DEX engine explainer
    from app.core.exceptions import NotFoundError

    raise NotFoundError("Priority score", lsoa_code)


@router.get("/{lsoa_code}/history", response_model=list[PriorityHistoryItem])
async def get_priority_history(
    lsoa_code: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 12,
) -> list[PriorityHistoryItem]:
    """
    Get historical priority scores for an LSOA.

    Useful for tracking changes over time.
    """
    # TODO: Implement database query
    return []


@router.post("/recalculate", response_model=RecalculateResponse)
async def recalculate_priorities(
    request: RecalculateRequest,
) -> RecalculateResponse:
    """
    Trigger priority recalculation.

    Admin only. Starts a background task to recalculate DEX scores.
    """
    # TODO: Implement Celery task trigger
    return RecalculateResponse(
        task_id="pending",
        status="queued",
        message="Priority recalculation queued",
    )
