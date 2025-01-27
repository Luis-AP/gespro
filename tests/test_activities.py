import pytest
from config import TestingConfig
from src.db import Database
from src.models.activity import Activity
from src.repositories.activity_repository import ActivityRepository
from tests.utils import cleanup
from mysql.connector.errors import IntegrityError, DataError


@pytest.fixture
def config():
    db = Database(TestingConfig)

    return db


@pytest.fixture
def activity_repository(config):
    db = config
    return ActivityRepository(db)


@pytest.fixture(autouse=True)
def setup(config):
    db = config

    with db.get_connection() as conn:
        cursor = conn.cursor()

        with open("gespro_struct_data.sql", "r") as file:
            sql_script = file.read()

        sql_statements = sql_script.split(";")

        for statement in sql_statements:
            if statement.strip():
                cursor.execute(statement)

        conn.commit()

        cursor.close()

    yield

    db = config
    with db.get_connection() as conn:
        cleanup(conn)


def test_save_with_all_fields(activity_repository):
    # Arrange
    activity = Activity(
        name="Activity Test",
        description="Test Description",
        due_date="2025-01-21",
        min_grade=6,
        professor_id=1,
    )

    # Act
    saved_activity = activity_repository.save(activity)

    # Assert
    assert saved_activity.id == 4


def test_save_raises_integrity_error_invalid_professor_id(activity_repository):
    # Arrange
    wrong_professor_id = 100
    activity = Activity(
        name="Activity Test",
        description="Test Description",
        due_date="2025-01-21",
        min_grade=6,
        professor_id=wrong_professor_id,
    )

    # Act & Assert
    with pytest.raises(IntegrityError):
        activity_repository.save(activity)


def test_save_raises_data_error_name_too_long(activity_repository):
    # Arrange
    activity = Activity(
        name="a" * 46,
        description="Test Description",
        due_date="2025-01-21",
        min_grade=6,
        professor_id=1,
    )

    # Act & Assert
    with pytest.raises(DataError):
        activity_repository.save(activity)


def test_save_without_optional_fields(activity_repository):
    # Arrange
    activity = Activity(
        name="Activity Test",
        due_date="2025-01-21",
        min_grade=6,
        professor_id=1,
    )
    # Act
    saved_activity = activity_repository.save(activity)

    # Assert
    assert saved_activity.id == 4


def test_save_raises_integrity_error_null_name(activity_repository):
    # Arrange
    activity = Activity(
        description="Test Description",
        due_date="2025-01-21",
        min_grade=6,
        professor_id=1,
    )

    # Act
    with pytest.raises(IntegrityError):
        activity_repository.save(activity)
