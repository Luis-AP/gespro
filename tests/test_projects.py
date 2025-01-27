import pytest
from flask import Flask
from flask.testing import FlaskClient
from config import TestingConfig
from src.db import Database
from tests.utils import cleanup
from src.repositories.project_repository import ProjectRepository
from src.models.project import Project


class TestProjects:
    """Pruebas de integración para los proyectos."""

    @pytest.fixture
    def config(self):
        """Obtener una instancia del conector con la configuración de pruebas."""
        db = Database(TestingConfig)

        return db

    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Inicializa y limpia la base de datos antes y después de cada prueba."""
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

    @pytest.fixture
    def project_repository(self, config: Database) -> ProjectRepository:
        """Obtener instancia de ProjectRepository"""
        db = config
        return ProjectRepository(db)

    @pytest.fixture
    def app(self, config) -> Flask:
        """Configura la aplicación con todos sus componentes en un entorno de prueba."""
        from app import create_app

        test_app = create_app()

        test_app.db = config
        return test_app

    @pytest.fixture
    def client(self, app: Flask) -> FlaskClient:
        """Crear un cliente de pruebas."""
        return app.test_client()

    @pytest.fixture
    def get_student_token(self, client: FlaskClient) -> str:
        """Obtiene token de autenticación de un estudiante"""

        response = client.post(
            "/api/auth/login",
            data={
                "email": "nicolas_blanco1989@yahoo.com",
                "password": "password123",
            },
            content_type="multipart/form-data",
        )

        return response.json["token"]

    @pytest.fixture
    def get_professor_token(self, client: FlaskClient) -> str:
        """Obtiene token de autenticación de un profesor"""

        response = client.post(
            "/api/auth/login",
            data={
                "email": "professorX@hotmail.com",
                "password": "password123",
            },
            content_type="multipart/form-data",
        )

        return response.json["token"]

    def test_update_project_ok(
        self,
        client: FlaskClient,
        get_student_token: str,
        project_repository: ProjectRepository,
    ) -> None:
        """Caso de éxito para edición de un proyecto"""

        # Arrange
        request_body = {
            "title": "GesPro",
            "repository_url": "https://github.com/nicolas89/gespro",
        }
        headers = {"Authorization": f"Bearer {get_student_token}"}
        project_id = 1
        og_project = project_repository.find_by_id(project_id)

        # Act
        response = client.patch(
            f"/api/projects/{project_id}",
            json=request_body,
            headers=headers,
            content_type="application/json",
        )

        # Assert
        assert response.status_code == 200

        # Act
        project = project_repository.find_by_id(project_id)

        # Assert
        assert project.title == request_body["title"]
        assert project.repository_url == request_body["repository_url"]

        assert project.title != og_project.title
        assert project.repository_url != og_project.repository_url

    def test_update_project_professor_forbidden(
        self,
        client: FlaskClient,
        get_professor_token: str,
        project_repository: ProjectRepository,
    ) -> None:
        """Caso de error para edición, los profesores no pueden editar proyectos"""

        # Arrange
        request_body = {
            "title": "Gespro Profesor",
            "repository_url": "https://github.com/charlesX/gespro",
        }
        headers = {"Authorization": f"Bearer {get_professor_token}"}

        project_id = 1

        og_project = project_repository.find_by_id(project_id)

        # Act
        response = client.patch(
            f"/api/projects/{project_id}",
            json=request_body,
            headers=headers,
            content_type="application/json",
        )

        # Assert
        assert response.status_code == 403

        # Act
        project = project_repository.find_by_id(project_id)

        # Assert
        assert project.title == og_project.title
        assert project.repository_url == og_project.repository_url

    def test_update_project_unauthorized(
        self,
        client: FlaskClient,
        project_repository: ProjectRepository,
    ) -> None:
        """Caso de error para edición, los profesores no pueden editar proyectos"""

        # Arrange
        request_body = {
            "title": "Gespro Anónimo",
            "repository_url": "https://github.com/anonimo/gespro",
        }
        project_id = 1

        og_project = project_repository.find_by_id(project_id)

        # Act
        response = client.patch(
            f"/api/projects/{project_id}",
            json=request_body,
            content_type="application/json",
        )

        # Assert
        assert response.status_code == 401

        # Act
        project = project_repository.find_by_id(project_id)

        # Assert
        assert project.title == og_project.title
        assert project.repository_url == og_project.repository_url
