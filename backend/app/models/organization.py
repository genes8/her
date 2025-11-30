"""Organization, Team, User, and Resource models."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.route import RoutePlan, RouteAssignment


class Organization(Base, UUIDMixin, TimestampMixin):
    """NHS Organization (Trust, ICB, Local Authority, PCN)."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ods_code: Mapped[Optional[str]] = mapped_column(String(10), unique=True)
    coverage_area: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326),
    )
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    teams: Mapped[list["Team"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    route_plans: Mapped[list["RoutePlan"]] = relationship(back_populates="organization")


class Team(Base, UUIDMixin, TimestampMixin):
    """Healthcare team within an organization."""

    __tablename__ = "teams"

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    team_type: Mapped[Optional[str]] = mapped_column(String(50))
    base_location: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
    )
    working_hours: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="teams")
    users: Mapped[list["User"]] = relationship(back_populates="team")
    resources: Mapped[list["Resource"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    route_plans: Mapped[list["RoutePlan"]] = relationship(back_populates="team")


class User(Base, UUIDMixin, TimestampMixin):
    """System user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    organization_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"))
    team_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("teams.id"))
    nhs_smartcard_id: Mapped[Optional[str]] = mapped_column(String(50))
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column()

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="users")
    team: Mapped[Optional["Team"]] = relationship(back_populates="users")

    __table_args__ = (Index("idx_users_org", "organization_id"),)


class Resource(Base, UUIDMixin, TimestampMixin):
    """Healthcare resource (vehicle, nurse, health visitor)."""

    __tablename__ = "resources"

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_visits_per_day: Mapped[int] = mapped_column(Integer, default=15)
    skills: Mapped[list] = mapped_column(JSONB, default=list)
    start_location: Mapped[Optional[Geometry]] = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    end_location: Mapped[Optional[Geometry]] = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    working_hours: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    team: Mapped["Team"] = relationship(back_populates="resources")
    route_assignments: Mapped[list["RouteAssignment"]] = relationship(back_populates="resource")
