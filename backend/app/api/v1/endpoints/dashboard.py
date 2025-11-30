"""Dashboard data endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================


class KPISummary(BaseModel):
    """KPI summary for dashboard."""

    total_lsoa: int
    core20_lsoa: int
    core20_percentage: float

    # Priority breakdown
    urgent_count: int
    high_count: int
    medium_count: int
    routine_count: int

    # Route metrics
    total_visits_today: int
    completed_visits_today: int
    completion_rate: float

    # Equity metrics
    core20_visits_percentage: float
    average_priority_score: float


class HeatmapDataPoint(BaseModel):
    """Single point for heatmap visualization."""

    lsoa_code: str
    lng: float
    lat: float
    value: float
    label: str


class HeatmapResponse(BaseModel):
    """Heatmap data response."""

    type: str = "FeatureCollection"
    features: list[dict]
    min_value: float
    max_value: float
    legend: list[dict]


class EquityCoverageResponse(BaseModel):
    """Equity coverage metrics."""

    total_core20_lsoa: int
    visited_core20_lsoa: int
    coverage_percentage: float

    # By priority
    urgent_covered: int
    urgent_total: int
    high_covered: int
    high_total: int

    # Trend
    trend_7_days: float  # % change
    trend_30_days: float


class TrendDataPoint(BaseModel):
    """Single trend data point."""

    date: str
    value: float


class TrendResponse(BaseModel):
    """Trend data response."""

    metric: str
    period: str
    data: list[TrendDataPoint]


# ============================================
# ENDPOINTS
# ============================================


@router.get("/summary", response_model=KPISummary)
async def get_dashboard_summary(
    icb_code: str | None = None,
    team_id: str | None = None,
) -> KPISummary:
    """
    Get KPI summary for dashboard.

    Optionally filter by ICB or team.
    """
    # TODO: Implement aggregation queries
    return KPISummary(
        total_lsoa=0,
        core20_lsoa=0,
        core20_percentage=0.0,
        urgent_count=0,
        high_count=0,
        medium_count=0,
        routine_count=0,
        total_visits_today=0,
        completed_visits_today=0,
        completion_rate=0.0,
        core20_visits_percentage=0.0,
        average_priority_score=0.0,
    )


@router.get("/heatmap/priority", response_model=HeatmapResponse)
async def get_priority_heatmap(
    min_lng: float | None = None,
    min_lat: float | None = None,
    max_lng: float | None = None,
    max_lat: float | None = None,
    icb_code: str | None = None,
) -> HeatmapResponse:
    """
    Get priority heatmap data for map visualization.

    Returns GeoJSON FeatureCollection with priority scores.
    """
    # TODO: Implement spatial query with PostGIS
    return HeatmapResponse(
        features=[],
        min_value=0.0,
        max_value=100.0,
        legend=[
            {"label": "Routine", "color": "#22c55e", "min": 0, "max": 25},
            {"label": "Medium", "color": "#eab308", "min": 25, "max": 50},
            {"label": "High", "color": "#f97316", "min": 50, "max": 75},
            {"label": "Urgent", "color": "#ef4444", "min": 75, "max": 100},
        ],
    )


@router.get("/heatmap/deprivation", response_model=HeatmapResponse)
async def get_deprivation_heatmap(
    min_lng: float | None = None,
    min_lat: float | None = None,
    max_lng: float | None = None,
    max_lat: float | None = None,
) -> HeatmapResponse:
    """
    Get IMD deprivation heatmap data.

    Shows Index of Multiple Deprivation by LSOA.
    """
    # TODO: Implement spatial query
    return HeatmapResponse(
        features=[],
        min_value=1.0,
        max_value=10.0,
        legend=[
            {"label": "Most Deprived (1-2)", "color": "#7f1d1d", "min": 1, "max": 2},
            {"label": "Deprived (3-4)", "color": "#dc2626", "min": 3, "max": 4},
            {"label": "Average (5-6)", "color": "#fbbf24", "min": 5, "max": 6},
            {"label": "Less Deprived (7-8)", "color": "#84cc16", "min": 7, "max": 8},
            {"label": "Least Deprived (9-10)", "color": "#15803d", "min": 9, "max": 10},
        ],
    )


@router.get("/equity-coverage", response_model=EquityCoverageResponse)
async def get_equity_coverage(
    icb_code: str | None = None,
    period_days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> EquityCoverageResponse:
    """
    Get Core20 equity coverage metrics.

    Shows how well the most deprived areas are being served.
    """
    # TODO: Implement coverage calculation
    return EquityCoverageResponse(
        total_core20_lsoa=0,
        visited_core20_lsoa=0,
        coverage_percentage=0.0,
        urgent_covered=0,
        urgent_total=0,
        high_covered=0,
        high_total=0,
        trend_7_days=0.0,
        trend_30_days=0.0,
    )


@router.get("/trends/{metric}", response_model=TrendResponse)
async def get_trend_data(
    metric: str,
    period: Annotated[str, Query(pattern="^(7d|30d|90d|1y)$")] = "30d",
    icb_code: str | None = None,
) -> TrendResponse:
    """
    Get trend data for a specific metric.

    Valid metrics: visits, coverage, priority_avg, completion_rate
    """
    # TODO: Implement trend calculation
    return TrendResponse(
        metric=metric,
        period=period,
        data=[],
    )
