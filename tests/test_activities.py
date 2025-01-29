import pytest
import datetime

from mysql.connector.errors import IntegrityError, DataError, Error

from config import TestingConfig
from src.db import Database
from src.models.activity import Activity
from src.repositories.activity_repository import ActivityRepository
from tests.utils import cleanup


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

def test_update_all_fields_success(activity_repository):
    # Arrange
    original_activity = activity_repository.find_by_id(1)
    activity = Activity(
        id=1,
        name="Nombre actualizado",
        description="Nueva descripción",
        due_date="2025-02-01",
        min_grade=7,
        professor_id=1
    )

    # Act
    activity_repository.update(activity)
    updated_activity = activity_repository.find_by_id(1)

    # Assert
    assert updated_activity.name == "Nombre actualizado"
    assert updated_activity.description == "Nueva descripción"
    assert updated_activity.due_date == datetime.datetime(2025, 2, 1, 0, 0)
    assert updated_activity.min_grade == 7
    assert updated_activity.professor_id == original_activity.professor_id
    assert updated_activity.created_at == original_activity.created_at
    assert updated_activity.updated_at > original_activity.updated_at

def test_update_partial_fields(activity_repository):
    # Arrange
    original_activity = activity_repository.find_by_id(1)
    activity = Activity(
        id=1,
        name="Actualización parcial",
        description="Descripción para actualización parcial",
        due_date=original_activity.due_date,
        min_grade=original_activity.min_grade
    )

    # Act
    activity_repository.update(activity)
    updated_activity = activity_repository.find_by_id(1)

    # Assert
    assert updated_activity.name == "Actualización parcial"
    assert updated_activity.description == "Descripción para actualización parcial"
    assert updated_activity.due_date == original_activity.due_date
    assert updated_activity.min_grade == original_activity.min_grade
    assert updated_activity.professor_id == original_activity.professor_id
    assert updated_activity.created_at == original_activity.created_at
    assert updated_activity.updated_at > original_activity.updated_at

def test_update_with_invalid_date_format(activity_repository):
    # Arrange
    original_activity = activity_repository.find_by_id(1)
    activity = Activity(
        id=1,
        name="Actividad de prueba",
        description="Test Description",
        due_date="invalid-date",  # Formato inválido
        min_grade=7
    )

    # Act & Assert
    with pytest.raises(DataError):
        activity_repository.update(activity)
    
    # Assert
    current_activity = activity_repository.find_by_id(1)
    assert current_activity.name == original_activity.name
    assert current_activity.description == original_activity.description
    assert current_activity.due_date == original_activity.due_date
    assert current_activity.updated_at == original_activity.updated_at

def test_update_name_too_long_data_error(activity_repository):
    # Arrange
    original_activity = activity_repository.find_by_id(1)
    activity = Activity(
        id=1,
        name= "s" * 46,
        description= "Una nueva descripción",
        due_date= original_activity.due_date,
        min_grade= original_activity.min_grade
    )

    # Act & Assert
    with pytest.raises(DataError):
        activity_repository.update(activity)

    # Assert
    current_activity = activity_repository.find_by_id(1)
    assert current_activity.name == original_activity.name
    assert current_activity.updated_at == original_activity.updated_at

def test_update_notexistent_activity(activity_repository):
     # Arrange
    activity = Activity(
        id=9999,
        name= "Nuevo nombre de actividad",
        description= "Una nueva descripción",
        due_date= "2025-02-02",
        min_grade= 5
    )

    # Act
    activity_repository.update(activity)

    # Assert
    notexistent_activity = activity_repository.find_by_id(9999)
    assert notexistent_activity.id is None

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

def test_delete_existing_activity_id(activity_repository):
    # arrange
    activity_id = 4

    # act
    activity_repository.delete(activity_id)

    # assert
    activity = activity_repository.find_by_id(activity_id)
    assert activity.id is None

def test_delete_non_existing_activity_id(activity_repository):
    # arrange
    activity_id = 88

    # act
    activity_repository.delete(activity_id)

    # assert
    activity = activity_repository.find_by_id(activity_id)
    assert activity.id is None

def test_delete_non_valid_activity_id(activity_repository):
    # arrange
    activity_id = "s"

    # act assert
    with pytest.raises(Error):
        activity_repository.delete(activity_id)