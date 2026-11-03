
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    __table_args__ = (
        CheckConstraint(
            "risk_level IN ('LOW', 'MEDIUM', 'HIGH')",
            name="risk_scores_risk_level_check",
        ),
        CheckConstraint(
            "rul_threshold >= 0",
            name="risk_scores_rul_threshold_check",
        ),
        CheckConstraint(
            "rul_threshold_probability IS NULL OR "
            "(rul_threshold_probability >= 0 "
            "AND rul_threshold_probability <= 1)",
            name="risk_scores_rul_threshold_probability_check",
        ),
        UniqueConstraint(
            "prediction_id",
            "rul_threshold",
            "thresholds_version",
            name="uq_risk_score_prediction_threshold",
            postgresql_nulls_not_distinct=True,
        ),
        Index("idx_risk_scores_machine", "machine_id"),
        Index("idx_risk_scores_level", "risk_level"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    machine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)

    rul_threshold: Mapped[int] = mapped_column(Integer, nullable=False)

    rul_threshold_probability: Mapped[float | None] = mapped_column(
        DOUBLE_PRECISION,
    )

    thresholds_version: Mapped[str | None] = mapped_column(
        ForeignKey("risk_threshold_configs.version"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
