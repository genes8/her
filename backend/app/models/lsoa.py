"""Geographic and reference data models - LSOA, IMD, Demographics, Clinical."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.priority import DEXPriorityScore


class LSOA(Base, UUIDMixin, TimestampMixin):
    """Lower Layer Super Output Area - Core geographic unit."""

    __tablename__ = "lsoa"

    lsoa_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    lsoa_name: Mapped[str] = mapped_column(String(255), nullable=False)
    local_authority_code: Mapped[Optional[str]] = mapped_column(String(10))
    local_authority_name: Mapped[Optional[str]] = mapped_column(String(255))
    icb_code: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    icb_name: Mapped[Optional[str]] = mapped_column(String(255))

    # PostGIS geometry columns
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326),
        nullable=False,
    )
    centroid: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
    )

    area_hectares: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    population_2021: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    imd_data: Mapped[list["IMDData"]] = relationship(back_populates="lsoa", cascade="all, delete-orphan")
    demographic_data: Mapped[list["DemographicData"]] = relationship(back_populates="lsoa", cascade="all, delete-orphan")
    clinical_data: Mapped[list["ClinicalData"]] = relationship(back_populates="lsoa", cascade="all, delete-orphan")
    accessibility_data: Mapped[list["AccessibilityData"]] = relationship(back_populates="lsoa", cascade="all, delete-orphan")
    priority_scores: Mapped[list["DEXPriorityScore"]] = relationship(back_populates="lsoa", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_lsoa_geometry", "geometry", postgresql_using="gist"),
    )


class IMDData(Base, UUIDMixin):
    """Index of Multiple Deprivation data."""

    __tablename__ = "imd_data"

    lsoa_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lsoa.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Overall IMD
    imd_rank: Mapped[Optional[int]] = mapped_column(Integer)
    imd_decile: Mapped[Optional[int]] = mapped_column(Integer)
    imd_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))

    # Domain Scores
    income_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    employment_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    education_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    health_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    crime_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    housing_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    environment_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))

    # Derived flag - Core20 (most deprived 20%)
    is_core20: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    lsoa: Mapped["LSOA"] = relationship(back_populates="imd_data")

    __table_args__ = (
        CheckConstraint("imd_decile BETWEEN 1 AND 10", name="check_imd_decile"),
        Index("idx_imd_lsoa", "lsoa_id"),
        Index("idx_imd_decile", "imd_decile"),
        Index("idx_imd_core20", "is_core20", postgresql_where="is_core20 = TRUE"),
    )


class DemographicData(Base, UUIDMixin):
    """Census 2021 demographic data."""

    __tablename__ = "demographic_data"

    lsoa_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lsoa.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Population breakdown
    total_population: Mapped[Optional[int]] = mapped_column(Integer)
    population_0_17: Mapped[Optional[int]] = mapped_column(Integer)
    population_18_64: Mapped[Optional[int]] = mapped_column(Integer)
    population_65_plus: Mapped[Optional[int]] = mapped_column(Integer)

    # Ethnicity (ONS categories)
    pct_white: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_asian: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_black: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_mixed: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_other: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_minority: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Language
    pct_english_not_main: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_no_english: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Household
    pct_no_car_household: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_single_parent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pct_lone_pensioner: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    lsoa: Mapped["LSOA"] = relationship(back_populates="demographic_data")

    __table_args__ = (
        Index("idx_demo_lsoa", "lsoa_id"),
    )


class ClinicalData(Base, UUIDMixin, TimestampMixin):
    """QOF clinical/health data."""

    __tablename__ = "clinical_data"

    lsoa_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lsoa.id", ondelete="CASCADE"),
        nullable=False,
    )
    gp_practice_code: Mapped[Optional[str]] = mapped_column(String(10))
    data_period: Mapped[Optional[str]] = mapped_column(String(20))

    # Disease prevalence (per 1000 population)
    diabetes_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    hypertension_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    copd_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    asthma_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    chd_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    stroke_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    cancer_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    mental_health_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    dementia_prevalence: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))

    # Utilization metrics
    emergency_admissions_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    a_and_e_attendance_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))

    # Derived composite score
    clinical_risk_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Relationships
    lsoa: Mapped["LSOA"] = relationship(back_populates="clinical_data")

    __table_args__ = (
        Index("idx_clinical_lsoa", "lsoa_id"),
        Index("idx_clinical_period", "data_period"),
    )


class AccessibilityData(Base, UUIDMixin):
    """Healthcare accessibility data."""

    __tablename__ = "accessibility_data"

    lsoa_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lsoa.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Travel times (minutes)
    time_to_nearest_gp: Mapped[Optional[int]] = mapped_column(Integer)
    time_to_nearest_hospital: Mapped[Optional[int]] = mapped_column(Integer)
    time_to_nearest_pharmacy: Mapped[Optional[int]] = mapped_column(Integer)

    # Public transport accessibility
    public_transport_accessibility_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Distance (km)
    distance_to_nearest_gp: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    distance_to_nearest_hospital: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))

    # Derived category
    access_category: Mapped[Optional[str]] = mapped_column(String(20))

    calculated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    lsoa: Mapped["LSOA"] = relationship(back_populates="accessibility_data")

    __table_args__ = (
        Index("idx_access_lsoa", "lsoa_id"),
    )
