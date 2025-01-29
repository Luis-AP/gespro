from datetime import datetime

from flask import current_app as app

from src.models.activity import Activity
from src.models.project import Project
from src.repositories.activity_repository import ActivityRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.user_repository import UserRepository

class ActivityOwnerError(Exception):
    pass

class ActivityService:
    def __init__(self, db):
        self.activity_repository = ActivityRepository(db)
        self.project_repository = ProjectRepository(db)
        self.user_repository = UserRepository(db)

    def get_activity(self, activity_id: int, professor_id: None) -> Activity:
        activity = self.activity_repository.find_by_id(activity_id)
        if activity.id is None: # si la actividad no existe su id es None
            return activity
        if professor_id is not None: # un professor está haciendo el request
            if professor_id != activity.professor_id:
                raise ActivityOwnerError("El professor_id de la petición no coincide con el de la actividad.")
        return activity

    def get_activities(self, professor_id=None):
        """Obtiene todas las actividades, filtrando por professor_id si existe."""

        if professor_id:
            if self.user_repository.get_professor_by_id(professor_id):
                return self.activity_repository.find_by_professor(professor_id)
            else:
                raise ValueError("El id de profesor no existe.")
        return self.activity_repository.find_all()

    def create(self, activity: Activity) -> Activity:
        if activity.name is None:
            raise ValueError("El nombre de la actividad no puede estar vacío.")
        # no hay ninguna validacion para activity.description
        if activity.due_date is None:
            raise ValueError("La fecha due_date no puede estar vacía.")
        else:
            try:
                activity.due_date = datetime.strptime(activity.due_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("La fecha due_date de la actividad tiene formato incorrecto.")
            else:
                if activity.due_date < datetime.today():
                    raise ValueError("La fecha due_date de la actividad no puede ser en el pasado.")
        if activity.min_grade is None:
            raise ValueError("La nota mínima de la actividad no puede estar vacía.")
        else:
            if activity.min_grade.isdecimal():
                activity.min_grade = int(activity.min_grade)
                if not (0 < activity.min_grade <= 10):
                    raise ValueError("La nota mínima de la actividad no está en el rango 1 - 10.")
        if activity.professor_id is None: # esto no debería pasar nunca
            app.logger.critical("activity.professor_id is None, no debería pasar nunca.")
            raise RuntimeError("El professor_id de la actividad no puede estar vacío.")
        return self.activity_repository.save(activity)

    def update(self, activity: Activity) -> Activity:
        og_activity = self.activity_repository.find_by_id(activity.id)
        if og_activity.id is None: # si la actividad no existe su id es None
            return og_activity
        if activity.professor_id != og_activity.professor_id:
            raise ActivityOwnerError("El professor_id de la petición no coincide con el de la actividad.")
        if activity.name is None:
            activity.name = og_activity.name
        if activity.description is None and og_activity.description is not None:
            activity.description = og_activity.description
        if activity.due_date is None:
            activity.due_date = og_activity.due_date
        else:
            try:
                activity.due_date = datetime.strptime(activity.due_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("La fecha due_date de la actividad tiene formato incorrecto.")
            else:
                if activity.due_date < datetime.today():
                    raise ValueError("La fecha due_date de la actividad no puede ser en el pasado.")
        if activity.min_grade is None:
            activity.min_grade = og_activity.min_grade
        else:
            if activity.min_grade.isdecimal():
                activity.min_grade = int(activity.min_grade)
                if not (0 < activity.min_grade <= 10):
                    raise ValueError("La nota mínima de la actividad no está en el rango 1 - 10.")
            else:
                raise ValueError("La nota mínima de la actividad debe ser decimal.")
        return self.activity_repository.update(activity)

    def delete (self, activity_id: int, professor_id: int):
        """Elimina una actividad.

        Solo si existe, es del professor pasado por
        param y si no esta vencida todavia.
        """
        activity = self.activity_repository.find_by_id(activity_id)
        if activity.id is None:
            raise ValueError("La actividad no existe.")
        if professor_id != activity.professor_id:
            raise ActivityOwnerError("El professor_id de la petición no coincide con el de la actividad.")
        if activity.due_date.date() < datetime.today().date():
            raise ValueError("La actividad ya se venció.")

        self.activity_repository.delete(activity.id)

    def get_grades(self, activity_id: int, professor_id: int) -> list[Project]:
        og_activity = self.activity_repository.find_by_id(activity_id)
        if og_activity.id is None: # si la actividad no existe su id es None
            raise ValueError("La actividad no existe.")
        if professor_id != og_activity.professor_id:
            raise ActivityOwnerError("El professor_id de la petición no coincide con el de la actividad.")
        return [Project(**project) for project in self.project_repository.find_by_activity(activity_id)]
