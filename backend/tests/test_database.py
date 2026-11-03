import uuid

import pytest

from sqlalchemy import select

from app.models.machine import Machine

from sqlalchemy.exc import IntegrityError

from app.models.sensor_reading import SensorReading

def test_database_connection(db_session):
    from sqlalchemy import text

    result = db_session.execute(
        text("SELECT current_database()")
    ).scalar_one()

    assert result == "predictive_maintenance_test"


def test_create_and_retrieve_machine(db_session):
    machine = Machine(
        machine_code=f"TEST-MACHINE-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=999999,
    )

    db_session.add(machine)
    db_session.flush()

    machine_id = machine.id

    retrieved_machine = db_session.execute(
        select(Machine).where(Machine.id == machine_id)
    ).scalar_one()

    assert retrieved_machine.machine_code == machine.machine_code
    assert retrieved_machine.dataset_id == "FD001"
    assert retrieved_machine.engine_id == 999999
def test_create_and_retrieve_sensor_reading(db_session):
    machine = Machine(
        machine_code=f"TEST-SENSOR-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=999998,
    )

    db_session.add(machine)
    db_session.flush()

    reading = SensorReading(
        machine_id=machine.id,
        cycle=1,
        op_setting_1=0.5,
        op_setting_2=0.25,
        op_setting_3=100.0,
        sensor_1=518.67,
        sensor_2=642.0,
    )

    db_session.add(reading)
    db_session.flush()

    retrieved = db_session.query(SensorReading).filter_by(
        machine_id=machine.id,
        cycle=1,
    ).one()

    assert retrieved.sensor_1 == 518.67
    assert retrieved.sensor_2 == 642.0
    assert retrieved.machine_id == machine.id


def test_sensor_reading_duplicate_machine_cycle(db_session):
    machine = Machine(
        machine_code=f"TEST-DUPLICATE-{uuid.uuid4().hex[:8]}",
        dataset_id="FD002",
        engine_id=999997,
    )

    db_session.add(machine)
    db_session.flush()

    reading_1 = SensorReading(
        machine_id=machine.id,
        cycle=1,
        sensor_1=518.67,
    )

    db_session.add(reading_1)
    db_session.flush()

    reading_2 = SensorReading(
        machine_id=machine.id,
        cycle=1,
        sensor_1=520.0,
    )

    db_session.add(reading_2)

    try:
        with pytest.raises(IntegrityError):
            db_session.flush()
    finally:
        db_session.rollback()

def test_sensor_reading_invalid_machine_id(db_session):
    reading = SensorReading(
        machine_id=uuid.uuid4(),
        cycle=1,
        sensor_1=518.67,
    )

    db_session.add(reading)

    with pytest.raises(IntegrityError):
        db_session.flush()