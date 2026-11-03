import uuid

import pytest
from app.models.machine import Machine
from app.models.sensor_reading import SensorReading
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.model_version import ModelVersion
from app.models.prediction import Prediction
from app.models.risk_score import RiskScore
from app.models.risk_threshold_config import RiskThresholdConfig
from app.models.alert import Alert


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
def test_create_and_retrieve_prediction(db_session):
    machine = Machine(
        machine_code=f"TEST-PRED-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=uuid.uuid4().int % 2_000_000_000 + 1,
    )

    model_version = ModelVersion(
        model_name=f"test-model-{uuid.uuid4().hex[:8]}",
        model_type="XGBoost",
        dataset_id="FD001",
        version="1.0.0",
        is_active=False,
    )

    db_session.add_all([machine, model_version])
    db_session.flush()

    prediction = Prediction(
        machine_id=machine.id,
        model_version_id=model_version.id,
        cycle=10,
        predicted_rul=45.5,
        lower_bound=40.0,
        upper_bound=51.0,
        coverage_level=0.90,
    )

    db_session.add(prediction)
    db_session.flush()

    retrieved = db_session.get(Prediction, prediction.id)

    assert retrieved is not None
    assert retrieved.machine_id == machine.id
    assert retrieved.model_version_id == model_version.id
    assert retrieved.cycle == 10
    assert retrieved.predicted_rul == 45.5
    assert retrieved.lower_bound == 40.0
    assert retrieved.upper_bound == 51.0
    assert retrieved.coverage_level == 0.90
    assert retrieved.at_cap is False
    assert retrieved.created_at is not None
def test_prediction_rejects_negative_rul(db_session):
    machine = Machine(
        machine_code=f"TEST-NEG-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=uuid.uuid4().int % 2_000_000_000 + 1,
    )

    model_version = ModelVersion(
        model_name=f"test-model-{uuid.uuid4().hex[:8]}",
        model_type="XGBoost",
        dataset_id="FD001",
        version="1.0.0",
        is_active=False,
    )

    db_session.add_all([machine, model_version])
    db_session.flush()

    prediction = Prediction(
        machine_id=machine.id,
        model_version_id=model_version.id,
        cycle=10,
        predicted_rul=-5.0,
    )

    db_session.add(prediction)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_prediction_rejects_invalid_coverage_level(db_session):
    machine = Machine(
        machine_code=f"TEST-COV-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=uuid.uuid4().int % 2_000_000_000 + 1,
    )

    model_version = ModelVersion(
        model_name=f"test-model-{uuid.uuid4().hex[:8]}",
        model_type="XGBoost",
        dataset_id="FD001",
        version="1.0.0",
        is_active=False,
    )

    db_session.add_all([machine, model_version])
    db_session.flush()

    prediction = Prediction(
        machine_id=machine.id,
        model_version_id=model_version.id,
        cycle=10,
        predicted_rul=50.0,
        coverage_level=1.5,
    )

    db_session.add(prediction)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_prediction_rejects_invalid_interval(db_session):
    machine = Machine(
        machine_code=f"TEST-INT-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=uuid.uuid4().int % 2_000_000_000 + 1,
    )

    model_version = ModelVersion(
        model_name=f"test-model-{uuid.uuid4().hex[:8]}",
        model_type="XGBoost",
        dataset_id="FD001",
        version="1.0.0",
        is_active=False,
    )

    db_session.add_all([machine, model_version])
    db_session.flush()

    prediction = Prediction(
        machine_id=machine.id,
        model_version_id=model_version.id,
        cycle=10,
        predicted_rul=50.0,
        lower_bound=60.0,
        upper_bound=40.0,
    )

    db_session.add(prediction)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_prediction_duplicate_machine_model_cycle(db_session):
    machine = Machine(
        machine_code=f"TEST-DUP-PRED-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=uuid.uuid4().int % 2_000_000_000 + 1,
    )

    model_version = ModelVersion(
        model_name=f"test-model-{uuid.uuid4().hex[:8]}",
        model_type="XGBoost",
        dataset_id="FD001",
        version="1.0.0",
        is_active=False,
    )

    db_session.add_all([machine, model_version])
    db_session.flush()

    prediction_1 = Prediction(
        machine_id=machine.id,
        model_version_id=model_version.id,
        cycle=10,
        predicted_rul=50.0,
    )

    db_session.add(prediction_1)
    db_session.flush()

    prediction_2 = Prediction(
        machine_id=machine.id,
        model_version_id=model_version.id,
        cycle=10,
        predicted_rul=45.0,
    )

    db_session.add(prediction_2)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_create_and_retrieve_risk_score(db_session):
    machine, prediction, threshold_config = (
        create_risk_score_dependencies(db_session)
    )

    risk_score = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="HIGH",
        rul_threshold=10,
        rul_threshold_probability=0.95,
        thresholds_version=threshold_config.version,
    )

    db_session.add(risk_score)
    db_session.flush()

    retrieved = db_session.get(RiskScore, risk_score.id)

    assert retrieved is not None
    assert retrieved.machine_id == machine.id
    assert retrieved.prediction_id == prediction.id
    assert retrieved.risk_level == "HIGH"
    assert retrieved.rul_threshold == 10
    assert retrieved.rul_threshold_probability == 0.95
    assert retrieved.thresholds_version == threshold_config.version
    assert retrieved.created_at is not None
def create_risk_score_dependencies(db_session):
    machine = Machine(
        machine_code=f"TEST-RISK-{uuid.uuid4().hex[:8]}",
        dataset_id="FD001",
        engine_id=uuid.uuid4().int % 2_000_000_000 + 1,
    )

    model_version = ModelVersion(
        model_name=f"test-model-{uuid.uuid4().hex[:8]}",
        model_type="XGBoost",
        dataset_id="FD001",
        version="1.0.0",
        is_active=False,
    )

    threshold_config = RiskThresholdConfig(
        version=f"test-threshold-{uuid.uuid4().hex[:8]}",
        horizon_cycles=30,
        high_rul_max=15,
        medium_rul_max=30,
        high_probability_min=0.80,
        medium_probability_min=0.50,
        alert_rul_threshold=10,
        is_active=False,
    )

    db_session.add_all([machine, model_version, threshold_config])
    db_session.flush()

    prediction = Prediction(
        machine_id=machine.id,
        model_version_id=model_version.id,
        cycle=10,
        predicted_rul=12.0,
        lower_bound=10.0,
        upper_bound=14.0,
        coverage_level=0.90,
    )

    db_session.add(prediction)
    db_session.flush()

    return machine, prediction, threshold_config
def test_risk_score_rejects_invalid_risk_level(db_session):
    machine, prediction, _ = create_risk_score_dependencies(db_session)

    risk_score = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="CRITICAL",
        rul_threshold=10,
        rul_threshold_probability=0.95,
    )

    db_session.add(risk_score)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_risk_score_rejects_negative_rul_threshold(db_session):
    machine, prediction, _ = create_risk_score_dependencies(db_session)

    risk_score = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="HIGH",
        rul_threshold=-5,
        rul_threshold_probability=0.95,
    )

    db_session.add(risk_score)

    with pytest.raises(IntegrityError):
        db_session.flush()
@pytest.mark.parametrize("probability", [-0.1, 1.1])
def test_risk_score_rejects_invalid_probability(db_session, probability):
    machine, prediction, _ = create_risk_score_dependencies(db_session)

    risk_score = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="HIGH",
        rul_threshold=10,
        rul_threshold_probability=probability,
    )

    db_session.add(risk_score)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_risk_score_rejects_duplicate_threshold_version(db_session):
    machine, prediction, threshold_config = (
        create_risk_score_dependencies(db_session)
    )

    risk_score_1 = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="HIGH",
        rul_threshold=10,
        rul_threshold_probability=0.95,
        thresholds_version=threshold_config.version,
    )

    db_session.add(risk_score_1)
    db_session.flush()

    risk_score_2 = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="MEDIUM",
        rul_threshold=10,
        rul_threshold_probability=0.70,
        thresholds_version=threshold_config.version,
    )

    db_session.add(risk_score_2)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_risk_score_rejects_duplicate_null_threshold_version(db_session):
    machine, prediction, _ = create_risk_score_dependencies(db_session)

    risk_score_1 = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="HIGH",
        rul_threshold=10,
        rul_threshold_probability=0.95,
        thresholds_version=None,
    )

    db_session.add(risk_score_1)
    db_session.flush()

    risk_score_2 = RiskScore(
        machine_id=machine.id,
        prediction_id=prediction.id,
        risk_level="MEDIUM",
        rul_threshold=10,
        rul_threshold_probability=0.70,
        thresholds_version=None,
    )

    db_session.add(risk_score_2)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_create_and_retrieve_alert(db_session):
    machine, prediction, _ = create_risk_score_dependencies(db_session)

    alert = Alert(
        machine_id=machine.id,
        prediction_id=prediction.id,
        alert_type="HIGH_RUL_RISK",
        severity="HIGH",
        message="Machine predicted to reach critical RUL threshold.",
    )

    db_session.add(alert)
    db_session.flush()

    retrieved = db_session.get(Alert, alert.id)

    assert retrieved is not None
    assert retrieved.machine_id == machine.id
    assert retrieved.prediction_id == prediction.id
    assert retrieved.alert_type == "HIGH_RUL_RISK"
    assert retrieved.severity == "HIGH"
    assert retrieved.message == (
        "Machine predicted to reach critical RUL threshold."
    )
    assert retrieved.status == "OPEN"
    assert retrieved.acknowledged_at is None
    assert retrieved.created_at is not None
def test_alert_rejects_invalid_severity(db_session):
    machine, _, _ = create_risk_score_dependencies(db_session)

    alert = Alert(
        machine_id=machine.id,
        alert_type="TEST_ALERT",
        severity="CRITICAL",
        message="Invalid severity test.",
    )

    db_session.add(alert)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_alert_rejects_invalid_status(db_session):
    machine, _, _ = create_risk_score_dependencies(db_session)

    alert = Alert(
        machine_id=machine.id,
        alert_type="TEST_ALERT",
        severity="HIGH",
        message="Invalid status test.",
        status="PENDING",
    )

    db_session.add(alert)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_alert_rejects_open_status_with_acknowledged_at(db_session):
    from datetime import datetime, timezone

    machine, _, _ = create_risk_score_dependencies(db_session)

    alert = Alert(
        machine_id=machine.id,
        alert_type="TEST_ALERT",
        severity="HIGH",
        message="Invalid acknowledgement test.",
        status="OPEN",
        acknowledged_at=datetime.now(timezone.utc),
    )

    db_session.add(alert)

    with pytest.raises(IntegrityError):
        db_session.flush()
def test_alert_accepts_acknowledged_status(db_session):
    from datetime import datetime, timezone

    machine, _, _ = create_risk_score_dependencies(db_session)

    acknowledged_time = datetime.now(timezone.utc)

    alert = Alert(
        machine_id=machine.id,
        alert_type="TEST_ALERT",
        severity="HIGH",
        message="Alert acknowledged by maintenance team.",
        status="ACKNOWLEDGED",
        acknowledged_at=acknowledged_time,
    )

    db_session.add(alert)
    db_session.flush()

    retrieved = db_session.get(Alert, alert.id)

    assert retrieved.status == "ACKNOWLEDGED"
    assert retrieved.acknowledged_at == acknowledged_time
def test_alert_accepts_resolved_status(db_session):
    from datetime import datetime, timezone

    machine, _, _ = create_risk_score_dependencies(db_session)

    acknowledged_time = datetime.now(timezone.utc)

    alert = Alert(
        machine_id=machine.id,
        alert_type="TEST_ALERT",
        severity="MEDIUM",
        message="Alert resolved after maintenance.",
        status="RESOLVED",
        acknowledged_at=acknowledged_time,
    )

    db_session.add(alert)
    db_session.flush()

    retrieved = db_session.get(Alert, alert.id)

    assert retrieved.status == "RESOLVED"
    assert retrieved.acknowledged_at == acknowledged_time
def test_deleting_machine_cascades_to_alerts(db_session):
    machine, _, _ = create_risk_score_dependencies(db_session)

    alert = Alert(
        machine_id=machine.id,
        alert_type="TEST_ALERT",
        severity="HIGH",
        message="Testing machine deletion cascade.",
    )

    db_session.add(alert)
    db_session.flush()

    alert_id = alert.id

    db_session.delete(machine)
    db_session.flush()

    # Clear SQLAlchemy's cached ORM objects.
    db_session.expire_all()

    # Verify directly against the database.
    remaining_alert = db_session.execute(
        select(Alert.id).where(Alert.id == alert_id)
    ).scalar_one_or_none()

    assert remaining_alert is None
def test_deleting_prediction_sets_alert_prediction_null(db_session):
    machine, prediction, _ = create_risk_score_dependencies(db_session)

    alert = Alert(
        machine_id=machine.id,
        prediction_id=prediction.id,
        alert_type="TEST_ALERT",
        severity="HIGH",
        message="Testing prediction deletion behavior.",
    )

    db_session.add(alert)
    db_session.flush()

    alert_id = alert.id

    db_session.delete(prediction)
    db_session.flush()

    db_session.refresh(alert)

    assert db_session.get(Alert, alert_id) is not None
    assert alert.prediction_id is None