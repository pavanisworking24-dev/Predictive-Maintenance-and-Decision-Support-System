
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    __table_args__ = (
        CheckConstraint(
            "cycle > 0",
            name="predictions_cycle_check",
        ),
        CheckConstraint(
            "predicted_rul >= 0",
            name="predictions_predicted_rul_check",
        ),
        CheckConstraint(
            "lower_bound IS NULL OR upper_bound IS NULL OR "
            "(lower_bound >= 0 AND upper_bound >= lower_bound)",
            name="chk_prediction_interval",
        ),
        CheckConstraint(
            "coverage_level IS NULL OR "
            "(coverage_level > 0 AND coverage_level < 1)",
            name="chk_coverage_level",
        ),
        UniqueConstraint(
            "machine_id",
            "model_version_id",
            "cycle",
            name="uq_prediction_machine_model_cycle",
        ),
        Index(
            "idx_predictions_machine_cycle",
            "machine_id",
            "cycle",
        ),
        Index(
            "idx_predictions_model",
            "model_version_id",
        ),
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

    model_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_versions.id"),
        nullable=False,
    )

    cycle: Mapped[int] = mapped_column(Integer, nullable=False)

    predicted_rul: Mapped[float] = mapped_column(
        DOUBLE_PRECISION,
        nullable=False,
    )

    lower_bound: Mapped[float | None] = mapped_column(DOUBLE_PRECISION)

    upper_bound: Mapped[float | None] = mapped_column(DOUBLE_PRECISION)

    coverage_level: Mapped[float | None] = mapped_column(DOUBLE_PRECISION)

    at_cap: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
