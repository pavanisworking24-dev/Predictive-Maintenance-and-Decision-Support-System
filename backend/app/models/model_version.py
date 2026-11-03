
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    __table_args__ = (
        UniqueConstraint(
            "model_name",
            "version",
            name="uq_model_version",
        ),
        Index(
            "uq_model_versions_one_active_per_dataset",
            "dataset_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
        CheckConstraint(
            "dataset_id IN ('FD001', 'FD002', 'FD003', 'FD004')",
            name="model_versions_dataset_id_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)

    model_type: Mapped[str] = mapped_column(String(50), nullable=False)

    dataset_id: Mapped[str] = mapped_column(String(10), nullable=False)

    version: Mapped[str] = mapped_column(String(50), nullable=False)

    artifact_uri: Mapped[str | None] = mapped_column(Text)

    feature_version: Mapped[str | None] = mapped_column(String(50))

    preprocessing_version: Mapped[str | None] = mapped_column(String(50))

    calibration_version: Mapped[str | None] = mapped_column(String(50))

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
