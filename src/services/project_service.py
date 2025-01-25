from datetime import datetime
import re
from src.models.project import Project
from src.repositories.project_repository import ProjectRepository, ProjectError
from src.repositories.activity_repository import ActivityRepository
from src.repositories.user_repository import UserRepository

class ProjectServiceError(Exception):
    pass

class ProjectValueError(ProjectServiceError):
    pass

class ProjectService:
    def __init__(self, db):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.activity_repository = ActivityRepository(db)
        self.user_repository = UserRepository(db)

    def create_project(self, project_data: dict, student_id: int) -> Project:
        # Validar que la actividad existe
        activity = self.activity_repository.find_by_id(project_data['activity_id'])
        if not activity.id:
            raise ProjectValueError("Activity not found")

        # Validar fecha límite
        if datetime.now() > activity.due_date:
            raise ProjectValueError("Activity deadline has passed")

        # Validar URL del repositorio
        if not self._validate_repository_url(project_data['repository_url']):
            raise ProjectValueError("Invalid repository URL format")

        # Crear proyecto
        project = Project(**project_data)
        try:
            return self.project_repository.create_project(project, student_id)
        except ProjectError as e:
            raise ProjectServiceError(str(e))

    def add_member(self, project_id: int, student_id: int, requesting_student_id: int) -> dict:
        project = self.project_repository.find_by_id(project_id)
        if not project.id:
            raise ProjectServiceError("Project not found")

        # Verificar si el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project_id, requesting_student_id):
            raise ProjectServiceError("Only project owner can add members")

        # Validar fecha límite
        activity = self.activity_repository.find_by_id(project.activity_id)
        if datetime.now() > activity.due_date:
            raise ProjectValueError("Activity deadline has passed")
        try:
            member = self.project_repository.add_member(student_id, project_id)
            if member is None:
                raise ProjectServiceError("The ID doesn't belong to any student")
            return member
        except ProjectError as e:
            raise ProjectServiceError(str(e))

    def get_projects(self, filters: dict = None) -> list[dict]:
        projects = self.project_repository.find_projects_with_details(filters)
        for project in projects:
            project['member_ids'] = [int(id) for id in project['member_ids'].split(',')]
        return projects

    def _validate_repository_url(self, url: str) -> bool:
        # Validar formato básico de URL de Git
        git_url_pattern = r'^(https?:\/\/)?(www\.)?([\w\d\-]+)\.([\w]+)\/([\w\d\-_]+)\/([\w\d\-_]+)(\.git)?\/?$'
        return bool(re.match(git_url_pattern, url))