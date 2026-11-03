
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Explanation(Base):
    __tablename__ = "explanations"

    __table_args__ = (
        CheckConstraint(
            "contribution_rank > 0",
            name="explanations_contribution_rank_check",
        ),
        UniqueConstraint(
            "prediction_id",
            "feature",
            name="uq_explanation_prediction_feature",
        ),
        UniqueConstraint(
            "prediction_id",
            "contribution_rank",
            name="uq_explanation_prediction_rank",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
    )

    contribution_rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    feature: Mapped[str] = mapped_column(String(100), nullable=False)

    sensor: Mapped[str | None] = mapped_column(String(20))

    shap_value: Mapped[float] = mapped_column(
        DOUBLE_PRECISION,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
