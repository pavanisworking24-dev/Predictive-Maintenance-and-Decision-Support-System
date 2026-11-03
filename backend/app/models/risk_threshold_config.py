
from datetime import datetime
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskThresholdConfig(Base):
    __tablename__ = "risk_threshold_configs"

    __table_args__ = (
        CheckConstraint(
            "horizon_cycles >= 1",
            name="risk_threshold_configs_horizon_cycles_check",
        ),
        CheckConstraint(
            "high_rul_max >= 0",
            name="risk_threshold_configs_high_rul_max_check",
        ),
        CheckConstraint(
            "medium_rul_max >= 0",
            name="risk_threshold_configs_medium_rul_max_check",
        ),
        CheckConstraint(
            "high_probability_min > 0 AND high_probability_min <= 1",
            name="risk_threshold_configs_high_probability_min_check",
        ),
        CheckConstraint(
            "medium_probability_min > 0 AND medium_probability_min <= 1",
            name="risk_threshold_configs_medium_probability_min_check",
        ),
        CheckConstraint(
            "alert_rul_threshold >= 0",
            name="risk_threshold_configs_alert_rul_threshold_check",
        ),
        CheckConstraint(
            "high_rul_max < medium_rul_max "
            "AND medium_probability_min < high_probability_min",
            name="chk_risk_threshold_order",
        ),
        UniqueConstraint(
            "version",
            name="risk_threshold_configs_version_key",
        ),
        Index(
            "uq_risk_threshold_configs_one_active",
            "is_active",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    version: Mapped[str] = mapped_column(String(50), nullable=False)

    horizon_cycles: Mapped[int] = mapped_column(Integer, nullable=False)

    high_rul_max: Mapped[int] = mapped_column(Integer, nullable=False)

    medium_rul_max: Mapped[int] = mapped_column(Integer, nullable=False)

    high_probability_min: Mapped[float] = mapped_column(
        DOUBLE_PRECISION,
        nullable=False,
    )

    medium_probability_min: Mapped[float] = mapped_column(
        DOUBLE_PRECISION,
        nullable=False,
    )

    alert_rul_threshold: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
