
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Machine(Base):
    __tablename__ = "machines"

    __table_args__ = (
        CheckConstraint(
            "dataset_id IN ('FD001', 'FD002', 'FD003', 'FD004')",
            name="machines_dataset_id_check",
        ),
        CheckConstraint(
            "engine_id > 0",
            name="machines_engine_id_check",
        ),
        UniqueConstraint("machine_code", name="machines_machine_code_key"),
        UniqueConstraint(
            "dataset_id",
            "engine_id",
            name="uq_machine_dataset_engine",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    machine_code: Mapped[str] = mapped_column(String(50), nullable=False)

    dataset_id: Mapped[str] = mapped_column(String(10), nullable=False)

    engine_id: Mapped[int] = mapped_column(Integer, nullable=False)

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

    sensor_readings = relationship(
        "SensorReading",
        back_populates="machine",
        cascade="all, delete",
        passive_deletes=True,
    )
