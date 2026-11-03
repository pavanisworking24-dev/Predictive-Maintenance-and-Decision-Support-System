
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    __table_args__ = (
        CheckConstraint(
            "cycle > 0",
            name="sensor_readings_cycle_check",
        ),
        UniqueConstraint(
            "machine_id",
            "cycle",
            name="uq_sensor_reading_machine_cycle",
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

    cycle: Mapped[int] = mapped_column(Integer, nullable=False)

    # Operating settings
    op_setting_1: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    op_setting_2: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    op_setting_3: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)

    # Sensor measurements
    sensor_1: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_2: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_3: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_4: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_5: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_6: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_7: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_8: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_9: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_10: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_11: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_12: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_13: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_14: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_15: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_16: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_17: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_18: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_19: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_20: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)
    sensor_21: Mapped[Optional[float]] = mapped_column(DOUBLE_PRECISION)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    machine = relationship(
        "Machine",
        back_populates="sensor_readings",
    )
