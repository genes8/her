"""DEX Engine priority score models."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.lsoa import LSOA
    from app.models.organization import User


class DEXPriorityScore(Base, UUIDMixin):
    """DEX Engine calculated priority scores."""

    __tablename__ = "dex_priority_scores"

    lsoa_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lsoa.id", ondelete="CASCADE"),
        nullable=False,
    )
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False)
    model_version: Mapped[str] = mapped_column(String(20), nullable=False)

    # Component scores (0-100)
    clinical_risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    social_vulnerability_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    accessibility_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    # Final priority
    priority_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    priority_label: Mapped[str] = mapped_column(String(20), nullable=False)

    # Explainability
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False)
    contributing_factors: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Flags
    requires_translator: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_specialist: Mapped[bool] = mapped_column(Boolean, default=False)
    min_visit_time_minutes: Mapped[int] = mapped_column(default=15)

    # Audit
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    # Relationships
    lsoa: Mapped["LSOA"] = relationship(back_populates="priority_scores")

    __table_args__ = (
        Index("idx_dex_lsoa", "lsoa_id"),
        Index("idx_dex_priority", "priority_score", postgresql_ops={"priority_score": "DESC"}),
        Index("idx_dex_label", "priority_label"),
        Index("idx_dex_date", "calculation_date"),
    )


class DEXModelConfig(Base, UUIDMixin):
    """DEX model configuration and weights."""

    __tablename__ = "dex_model_config"

    model_version: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    # Weight configuration
    clinical_weight: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0.40"))
    social_weight: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0.35"))
    accessibility_weight: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("0.25"))

    # Rule definitions (stored as JSON for flexibility)
    fuzzy_rules: Mapped[dict] = mapped_column(JSONB, nullable=False)
    aggregation_rules: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    approved_at: Mapped[Optional[datetime]] = mapped_column()
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    __table_args__ = (
        CheckConstraint(
            "clinical_weight + social_weight + accessibility_weight BETWEEN 0.99 AND 1.01",
            name="weights_sum_to_one",
        ),
    )
