from datetime import datetime
import re
from src.models.project import Project
from src.repositories.project_repository import ProjectRepository, ProjectError
from src.repositories.activity_repository import ActivityRepository
from src.repositories.user_repository import UserRepository

class ProjectServiceError(Exception):
    pass

class ProjectValueError(Exception):
    pass

class ProjectOwnerError(Exception):
    pass

class NotFoundError(Exception):
    pass

class ProjectService:
    def __init__(self, db):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.activity_repository = ActivityRepository(db)
        self.user_repository = UserRepository(db)

    def create_project(self, project: Project, student_id: int) -> Project:
        # Validar que se incluyó un ID de actividad
        if project.activity_id is None:
            raise ProjectValueError("Activity ID is required")
        # Validar que la actividad existe
        activity = self.activity_repository.find_by_id(project.activity_id)
        if not activity.id:
            raise NotFoundError("Activity not found")

        # Validar fecha límite
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("Activity deadline has passed")
        
        # Validar que se incluyó un título
        if project.title is None:
            raise ProjectValueError("Title is required")
        
        if project.repository_url is None:
            raise ProjectValueError("Repository URL is required")

        # Validar URL del repositorio
        if not self._validate_repository_url(project.repository_url):
            raise ProjectValueError("Invalid repository URL format")
        
        try:
            return self.project_repository.create_project(project, student_id)
        except ProjectError as e:
            raise ProjectServiceError(str(e))

    def add_member(self, project_id: int, student_id: int, requesting_student_id: int) -> dict:
        project = self.project_repository.find_by_id(project_id)
        if not project.id:
            raise NotFoundError("Project not found")

        # Verificar si el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project_id, requesting_student_id):
            raise ProjectOwnerError("Only project owner can add members")

        # Validar fecha límite
        activity = self.activity_repository.find_by_id(project.activity_id)
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("Activity deadline has passed")
        try:
            member = self.project_repository.add_member(student_id, project_id)
            if member is None:
                raise ProjectServiceError("The ID doesn't belong to any student")
            return member
        except ProjectError as e:
            raise ProjectServiceError(str(e))

    def remove_member(self, project_id: int, student_id: int, requesting_student_id: int) -> None:
        # Validar que el proyecto exista
        project = self.project_repository.find_by_id(project_id)
        if not project.id:
            raise NotFoundError("Project not found")

        # Verificar si el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project_id, requesting_student_id):
            raise ProjectOwnerError("Only project owner can remove members")

        # Validar que el miembro pertenezca al proyecto
        if not self.project_repository.validate_member(student_id, project_id):
            raise NotFoundError("Member not found in project")
            
        # No se puede remover al dueño del proyecto
        if self.project_repository.is_project_owner(project_id, student_id):
            raise ProjectValueError("Cannot remove project owner")

        try:
            self.project_repository.remove_student_from_project(student_id, project_id)
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
    
    def update(self, project : Project, student_id: int) -> Project:
        # Validar que el proyecto exista
        og_project = self.project_repository.find_by_id(project.id)
        if og_project.id is None:
            raise NotFoundError("Project not found")
        
        # Validar que el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project.id, student_id):
            raise ProjectOwnerError("Only project owner can update project")
        
        # Validar fecha límite de la actividad
        activity = self.activity_repository.find_by_id(og_project.activity_id)
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("Cannot update project after activity deadline")
        
        # Validar URL del repositorio
        if project.repository_url and not self._validate_repository_url(project.repository_url):
            raise ProjectValueError("Invalid repository URL format")
        
        # Llenar campos faltantes con los originales
        if project.title is None:
            project.title = og_project.title
        if project.repository_url is None:
            project.repository_url = og_project.repository_url
        
        try:
            return self.project_repository.update(project)
        except ProjectError as e:
            raise
    
    def delete(self, project_id: int, student_id: int) -> None:
        """Elimina un proyecto, solo si existe y el estudiante es el dueño"""

        project = self.project_repository.find_by_id(project_id)
        if not project.id:
            raise NotFoundError("Project not found")
        
        # Validar que el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project_id, student_id):
            raise ProjectOwnerError("Only project owner can delete project")
        
        # Validar fecha límite de la actividad
        activity = self.activity_repository.find_by_id(project.activity_id)
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("Cannot delete project after activity deadline")

        self.project_repository.delete(project_id)