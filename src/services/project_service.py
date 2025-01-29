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
            raise ProjectValueError("El id de la actividad es obligatorio")
        # Validar que la actividad existe
        activity = self.activity_repository.find_by_id(project.activity_id)
        if not activity.id:
            raise NotFoundError("Actividad no encontrada")

        # Validar fecha límite
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("El plazo de la actividad ha finalizado")

        # Validar que se incluyó un título
        if project.title is None:
            raise ProjectValueError("El título es obligatorio")

        if project.repository_url is None:
            raise ProjectValueError("La URL del repositorio es obligatoria")

        # Validar URL del repositorio
        if not self._validate_repository_url(project.repository_url):
            raise ProjectValueError("Formato de URL de repositorio no válido")

        try:
            return self.project_repository.create_project(project, student_id)
        except ProjectError as e:
            raise ProjectServiceError(str(e))

    def add_member(self, project_id: int, student_id: int, requesting_student_id: int) -> dict:
        project = self.project_repository.find_by_id(project_id)
        if not project.id:
            raise NotFoundError("Proyecto no encontrado")

        # Verificar si el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project_id, requesting_student_id):
            raise ProjectOwnerError("Solo el propietario del proyecto puede añadir miembros")

        # Validar fecha límite
        activity = self.activity_repository.find_by_id(project.activity_id)
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("El plazo de actividad ha finalizado")
        try:
            member = self.project_repository.add_member(student_id, project_id)
            if member is None:
                raise ProjectServiceError("El id no pertenece a ningún estudiante")
            return member
        except ProjectError as e:
            raise ProjectServiceError(str(e))

    def remove_member(self, project_id: int, student_id: int, requesting_student_id: int) -> None:
        # Validar que el proyecto exista
        project = self.project_repository.find_by_id(project_id)
        if not project.id:
            raise NotFoundError("Proyecto no encontrado")

        # Verificar si el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project_id, requesting_student_id):
            raise ProjectOwnerError("Solo el propietario del proyecto puede eliminar miembros")

        # Validar que el miembro pertenezca al proyecto
        if not self.project_repository.validate_member(student_id, project_id):
            raise NotFoundError("El estudiante no pertenece al proyecto")

        # No se puede remover al dueño del proyecto
        if self.project_repository.is_project_owner(project_id, student_id):
            raise ProjectValueError("No se puede eliminar al propietario del proyecto")

        try:
            self.project_repository.remove_student_from_project(student_id, project_id)
        except ProjectError as e:
            raise ProjectServiceError(str(e))

    def get_projects(self, filters: dict = None) -> list[dict]:
        projects = self.project_repository.find_projects_with_details(filters)
        for project in projects:
            project['member_ids'] = [int(id) for id in project['member_ids'].split(',')]
            project['created_at'] = project['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            project['updated_at'] = project['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            project['due_date'] = project['due_date'].strftime('%Y-%m-%d')
        return projects

    def _validate_repository_url(self, url: str) -> bool:
        # Validar formato básico de URL de Git
        git_url_pattern = r'^(https?:\/\/)?(www\.)?([\w\d\-]+)\.([\w]+)\/([\w\d\-_]+)\/([\w\d\-_]+)(\.git)?\/?$'
        return bool(re.match(git_url_pattern, url))

    def update(self, project : Project, student_id: int) -> Project:
        # Validar que el proyecto exista
        og_project = self.project_repository.find_by_id(project.id)
        if og_project.id is None:
            raise NotFoundError("Proyecto no encontrado")

        # Validar que el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project.id, student_id):
            raise ProjectOwnerError("Solo el propietario del proyecto puede actualizar el proyecto")

        # Validar fecha límite de la actividad
        activity = self.activity_repository.find_by_id(og_project.activity_id)
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("No se puede actualizar el proyecto una vez finalizado el plazo de actividad")

        # Validar URL del repositorio
        if project.repository_url and not self._validate_repository_url(project.repository_url):
            raise ProjectValueError("Formato de URL de repositorio no válido")

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
            raise NotFoundError("Proyecto no encontrado")

        # Validar que el estudiante es el dueño del proyecto
        if not self.project_repository.is_project_owner(project_id, student_id):
            raise ProjectOwnerError("Solo el propitario del proyecto puede eliminar el proyecto")

        # Validar fecha límite de la actividad
        activity = self.activity_repository.find_by_id(project.activity_id)
        if datetime.now().date() > activity.due_date.date():
            raise ProjectServiceError("No se puede eliminar el proyecto una vez finalizado el plazo de actividad")

        self.project_repository.delete(project_id)

    def grade(self, project_id: int, professor_id: int, grade: str) -> Project:
        """Llamar a calificar un proyecto.

        Revisar si el proyecto existe
        Revisar si el profesor es el creador de la actividad.
        Revisar que haya pasado la due_date de la actividad.
        Revisar si la nota está entre 0 y 10.
        """
        project = self.project_repository.find_by_id(project_id)
        if project.id is None:
            raise ValueError("El proyecto no existe.")
        activity = self.activity_repository.find_by_id(project.activity_id)
        if activity.id:
            if professor_id != activity.professor_id:
                raise ValueError("La actividad del proyecto no pertenece al profesor solicitante.")
            else:
                if activity.due_date.date() >= datetime.today().date():
                    raise ValueError("No se puede calificar. La actividad sigue abierta.")

                try:
                    grade = float(grade)
                except ValueError:
                    raise ValueError("Calificación inválida.")
                else:
                    if 0.0 <= grade <= 10.0:
                        try:
                            self.project_repository.update_grade(project.id, grade)
                        except:
                            raise
                        else:
                            return self.project_repository.find_by_id(project.id)
                    else:
                        raise ValueError("Calificación inválida.")
        else:
            # thisi is highly unusual
            raise RuntimeError("Error de FK entre proyecto y actividad")
