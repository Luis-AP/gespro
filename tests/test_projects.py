import pytest
import datetime

from flask import Flask
from flask.testing import FlaskClient

from config import TestingConfig
from src.db import Database
from tests.utils import cleanup
from src.repositories.project_repository import ProjectRepository
from src.models.project import Project
from src.repositories.activity_repository import ActivityRepository
from src.models.activity import Activity

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
    def activity_repository(self, config: Database) -> ActivityRepository:
        """Obtener instancia de ActivityRepository"""
        db = config
        return ActivityRepository(db)

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
    def get_not_owner_token(self, client: FlaskClient) -> str:
        """Obtiene token de autenticación de un estudiante"""

        response = client.post(
            "/api/auth/login",
            data={
                "email": "juan_monzon2001@gmail.com",
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

    def test_delete_project_ok(self, client, get_student_token, project_repository):
        """
        Caso de éxito para eliminar un proyecto
        """
        # Arrange
        project_id = 1
        headers =  {"Authorization": f"Bearer {get_student_token}"}

        # Act
        response = client.delete(
            f"/api/projects/{project_id}",
            headers=headers
        )

        # Assert
        assert response.status_code == 204
        assert response.data == b''

        deleted_project = project_repository.find_by_id(project_id)
        assert deleted_project.id is None

    def test_delete_project_professor_forbidden(self, client, get_professor_token, project_repository):
        """
        Caso de fallo para eliminar un proyecto por parte de un profesor
        """
        # Arrange
        project_id = 1
        headers =  {"Authorization": f"Bearer {get_professor_token}"}

        # Act
        response = client.delete(
            f"/api/projects/{project_id}",
            headers=headers
        )

        # Assert
        assert response.status_code == 403
        assert response.json["mensaje"] == "Only students can delete projects"

        deleted_project = project_repository.find_by_id(project_id)
        assert deleted_project.id is not None

    def test_delete_project_not_owner(self, client, get_not_owner_token, project_repository):
        """
        Caso de fallo por un estudiante que no es el dueño del proyecto
        """
        # Arrange
        project_id = 1
        headers =  {"Authorization": f"Bearer {get_not_owner_token}"}

        # Act
        response = client.delete(
            f"/api/projects/{project_id}",
            headers=headers
        )

        # Assert
        assert response.status_code == 403
        assert response.json["mensaje"] == "Only project owner can delete project"

        deleted_project = project_repository.find_by_id(project_id)
        assert deleted_project.id is not None
    
    def test_delete_project_after_deadline(self, client, get_student_token, project_repository, activity_repository):
        """
        Caso de fallo al intentar eliminar un proyecto de una actividad que ya cerró
        """
        # Assert
        project_id = 1
        headers =  {"Authorization": f"Bearer {get_student_token}"}

        # Modificar fecha de entrega de actividad para que esté cerrada en el día de hoy
        original_activity = activity_repository.find_by_id(1)
        updated_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
        formatted_date = updated_date.strftime("%Y-%m-%d")

        activity = Activity(
            id=original_activity.id,
            name=original_activity.name,
            description=original_activity.description,
            due_date=formatted_date,
            min_grade=original_activity.min_grade,
            professor_id=original_activity.professor_id
        )
        activity_repository.update(activity)

        # Act
        response = client.delete(
            f"/api/projects/{project_id}",
            headers=headers
        )

        # Assert
        assert response.status_code == 403
        assert response.json["mensaje"] == "Cannot delete project after activity deadline"

        deleted_project = project_repository.find_by_id(project_id)
        assert deleted_project.id is not None

    def test_create_project_non_existent_activity(self, client, get_student_token):
        # arrange
        # obtener token
        token = get_student_token
        activity_id = 5  # id de actividad inexistente

        # act
        # enviar request
        request = {"title": "Mi proyecto",
                   "repository_url": "https://github.com/miuser/mirepo",
                   "activity_id": activity_id}
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/projects/",
                               json=request,
                               headers=headers,
                               content_type="application/json")
        # assert
        # ver la response (codigo) debe ser 404
        #logger.info("valor de status code: %s", response.status_code)
        assert response.status_code == 404
        # ver que el 'mensaje' sea "Activity not found"
        #logger.info("valor de mensaje: %s", response.json["mensaje"])
        assert response.json["mensaje"] == "Activity not found"