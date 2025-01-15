from datetime import datetime

from src.models.activity import Activity
from typing import Union
from mysql.connector.errors import IntegrityError

class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self) -> list[dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities")
            result = cursor.fetchall()
            return result

    def find_by_id(self, activity_id: int) -> Activity:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE id = %s", (activity_id,))
            activity = cursor.fetchone()
            if activity:
                return Activity(**activity)
            else:
                return Activity(id=None)

    def find_by_name(self, name):
        """Buscar actividades por nombre.

        Se utilizan los comodines %name%, con LIKE.
        """
        name = f"%{name}%"
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE name LIKE %s", (name,))
            result = cursor.fetchall()
            if result:
                activities = []
                for row in result:
                    activity = Activity(**row)
                    activities.append(activity)
                return activities
            else:
                return []

    def find_by_professor(self, professor_id):
        """Buscar todas las actividades de un professor."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE professor_id = %s", (professor_id,))
            result = cursor.fetchall()
            return result

    def find_by_due_date(self, due_date: datetime):
        """Buscar actividades por fecha de entrega.

        Se asume due_date del tipo datetime.datetime y al buscar
        se utiliza solo due_date.date.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE due_date = %s", (due_date.date,))
            result = cursor.fetchall()
            return result

    def save(self, activity: Activity):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                res = cursor.callproc("CreateActivity",
                                      (activity.name,
                                       activity.description,
                                       activity.due_date,
                                       activity.min_grade,
                                       activity.professor_id,
                                       None))
            except IntegrityError:
                conn.rollback()
                raise
            else:
                conn.commit()
                activity.id = res[-1]
                return activity

    def update(self, activity: Activity):
        """Actualizar datos de una actividad.

        Por defecto no se actualiza el id del professor
        que creo la actividad originalmente.
        """
        query = """UPDATE activities
                    SET name = %s, description = %s, due_date = %s, min_grade = %s
                    WHERE id = %s"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (activity.name,
                                        activity.description,
                                        activity.due_date,
                                        activity.min_grade,
                                        activity.id))
            except IntegrityError:
                conn.rollback()
                raise
            else:
                conn.commit()

    def delete(self, activity: Activity):
        """Eliminar una actividad.

        Asume que se pasa una actividad con un id valido.
        Aunque puede no existir.
        """
        query = "DELETE FROM activities WHERE id = %s"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (activity.id,))
            except IntegrityError:
                conn.rollback()
                raise
            else:
                conn.commit()