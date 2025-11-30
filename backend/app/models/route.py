"""Route planning models."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, Numeric, String, Text, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.lsoa import LSOA
    from app.models.organization import Organization, Resource, Team, User


class VisitLocation(Base, UUIDMixin, TimestampMixin):
    """Location to visit (patient home, community center, care home)."""

    __tablename__ = "visit_locations"

    lsoa_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("lsoa.id"))
    organization_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"))

    name: Mapped[Optional[str]] = mapped_column(String(255))
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    postcode: Mapped[str] = mapped_column(String(10), nullable=False)
    location: Mapped[Geometry] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    location_type: Mapped[Optional[str]] = mapped_column(String(50))
    required_skills: Mapped[list] = mapped_column(JSONB, default=list)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    time_windows: Mapped[Optional[list]] = mapped_column(JSONB)
    priority_override: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    route_stops: Mapped[list["RouteStop"]] = relationship(back_populates="visit_location")

    __table_args__ = (
        Index("idx_visit_loc_geo", "location", postgresql_using="gist"),
        Index("idx_visit_loc_lsoa", "lsoa_id"),
    )


class RoutePlan(Base, UUIDMixin, TimestampMixin):
    """Route plan for a specific date."""

    __tablename__ = "route_plans"

    organization_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"))
    team_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("teams.id"))
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")
    optimization_config: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Results summary
    total_resources: Mapped[Optional[int]] = mapped_column(Integer)
    total_visits: Mapped[Optional[int]] = mapped_column(Integer)
    total_distance_km: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    total_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    equity_coverage_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Audit
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    optimized_at: Mapped[Optional[datetime]] = mapped_column()
    approved_at: Mapped[Optional[datetime]] = mapped_column()
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="route_plans")
    team: Mapped[Optional["Team"]] = relationship(back_populates="route_plans")
    assignments: Mapped[list["RouteAssignment"]] = relationship(back_populates="route_plan", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_route_plan_date", "plan_date"),
        Index("idx_route_plan_org", "organization_id"),
    )


class RouteAssignment(Base, UUIDMixin, TimestampMixin):
    """Route assignment to a specific resource."""

    __tablename__ = "route_assignments"

    route_plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("route_plans.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("resources.id"))

    route_geometry: Mapped[Optional[Geometry]] = mapped_column(Geometry(geometry_type="LINESTRING", srid=4326))

    sequence_count: Mapped[Optional[int]] = mapped_column(Integer)
    total_distance_km: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    total_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_start_time: Mapped[Optional[time]] = mapped_column(Time)
    estimated_end_time: Mapped[Optional[time]] = mapped_column(Time)

    # DEX metrics
    total_priority_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    core20_visits_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    route_plan: Mapped["RoutePlan"] = relationship(back_populates="assignments")
    resource: Mapped[Optional["Resource"]] = relationship(back_populates="route_assignments")
    stops: Mapped[list["RouteStop"]] = relationship(back_populates="route_assignment", cascade="all, delete-orphan")


class RouteStop(Base, UUIDMixin, TimestampMixin):
    """Individual stop in a route."""

    __tablename__ = "route_stops"

    route_assignment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("route_assignments.id", ondelete="CASCADE"), nullable=False
    )
    visit_location_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("visit_locations.id"))

    stop_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_arrival: Mapped[Optional[time]] = mapped_column(Time)
    estimated_departure: Mapped[Optional[time]] = mapped_column(Time)

    # Priority info (denormalized)
    priority_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    priority_label: Mapped[Optional[str]] = mapped_column(String(20))

    # Actual execution
    actual_arrival: Mapped[Optional[datetime]] = mapped_column()
    actual_departure: Mapped[Optional[datetime]] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    route_assignment: Mapped["RouteAssignment"] = relationship(back_populates="stops")
    visit_location: Mapped[Optional["VisitLocation"]] = relationship(back_populates="route_stops")

    __table_args__ = (
        Index("idx_route_stops_assignment", "route_assignment_id"),
        Index("idx_route_stops_sequence", "route_assignment_id", "stop_sequence"),
    )
