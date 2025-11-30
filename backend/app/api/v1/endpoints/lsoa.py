"""LSOA geographic data endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================


class LSOABase(BaseModel):
    """Base LSOA schema."""

    lsoa_code: str
    lsoa_name: str
    local_authority_name: str | None = None
    icb_name: str | None = None
    population_2021: int | None = None


class LSOAResponse(LSOABase):
    """LSOA response schema."""

    id: UUID


class LSOADetailResponse(LSOAResponse):
    """Detailed LSOA response with all data."""

    # IMD data
    imd_decile: int | None = None
    imd_score: float | None = None
    is_core20: bool = False

    # Demographics
    pct_minority: float | None = None
    pct_no_car_household: float | None = None
    pct_no_english: float | None = None

    # Clinical
    diabetes_prevalence: float | None = None
    clinical_risk_score: float | None = None

    # Accessibility
    access_category: str | None = None
    time_to_nearest_gp: int | None = None


class LSOAGeoJSON(BaseModel):
    """GeoJSON response for LSOA."""

    type: str = "Feature"
    properties: dict
    geometry: dict


class LSOAListResponse(BaseModel):
    """Paginated LSOA list response."""

    items: list[LSOAResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================
# ENDPOINTS
# ============================================


@router.get("/", response_model=LSOAListResponse)
async def list_lsoa(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    icb_code: str | None = None,
    local_authority_code: str | None = None,
    is_core20: bool | None = None,
    search: str | None = None,
) -> LSOAListResponse:
    """
    List LSOA areas with optional filtering.

    - **icb_code**: Filter by Integrated Care Board
    - **local_authority_code**: Filter by Local Authority
    - **is_core20**: Filter by Core20 status (most deprived 20%)
    - **search**: Search by LSOA code or name
    """
    # TODO: Implement database query
    return LSOAListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        pages=0,
    )


@router.get("/search")
async def search_lsoa(
    q: Annotated[str, Query(min_length=2)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[LSOAResponse]:
    """
    Search LSOA by postcode or name.

    Returns top matches for autocomplete functionality.
    """
    # TODO: Implement search with pg_trgm
    return []


@router.get("/within-bounds")
async def get_lsoa_within_bounds(
    min_lng: float,
    min_lat: float,
    max_lng: float,
    max_lat: float,
    include_geometry: bool = False,
) -> list[LSOAResponse | LSOAGeoJSON]:
    """
    Get LSOA areas within map viewport bounds.

    Used for efficient map rendering - only loads visible areas.
    """
    # TODO: Implement spatial query with PostGIS
    return []


@router.get("/{lsoa_code}", response_model=LSOADetailResponse)
async def get_lsoa(lsoa_code: str) -> LSOADetailResponse:
    """
    Get detailed information for a single LSOA.

    Includes IMD, demographics, clinical data, and accessibility.
    """
    # TODO: Implement database query with joins
    from app.core.exceptions import NotFoundError

    raise NotFoundError("LSOA", lsoa_code)


@router.get("/{lsoa_code}/geojson", response_model=LSOAGeoJSON)
async def get_lsoa_geojson(lsoa_code: str) -> LSOAGeoJSON:
    """
    Get GeoJSON geometry for a single LSOA.

    Used for highlighting selected area on map.
    """
    # TODO: Implement with PostGIS ST_AsGeoJSON
    from app.core.exceptions import NotFoundError

    raise NotFoundError("LSOA", lsoa_code)


@router.get("/{lsoa_code}/neighbors")
async def get_lsoa_neighbors(
    lsoa_code: str,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> list[LSOAResponse]:
    """
    Get neighboring LSOA areas.

    Uses PostGIS ST_Touches for spatial adjacency.
    """
    # TODO: Implement spatial neighbor query
    return []
