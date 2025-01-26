from datetime import datetime

from mysql.connector.errors import Error
from flask import current_app as app

from src.models.activity import Activity
from src.db import Database

class ActivityRepository:
    def __init__(self, db: Database):
        self.db = db

    def find_all(self) -> list[Activity]:
        with self.db.get_connection() as conn:
            query = """SELECT a.id, a.name, a.description, a.due_date, a.min_grade, a.professor_id, a.created_at,
                       a.updated_at, u.last_name, u.first_name
                       FROM activities AS a INNER JOIN professors AS p
                       ON a.professor_id = p.id
                       INNER JOIN users AS u ON p.user_id = u.id
                       ORDER BY u.last_name ASC, u.first_name ASC, created_at DESC"""
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchall()
            return [Activity(**activity) for activity in result]

    def find_by_id(self, activity_id: int) -> Activity:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE id = %s", (activity_id,))
            activity = cursor.fetchone()
            app.logger.debug("activity: %s", activity)
            if activity:
                return Activity(**activity)
            else:
                return Activity(id=None)

    def find_by_name(self, name) -> list[Activity]:
        """Buscar actividades por nombre.

        Se utilizan los comodines %name%, con LIKE.
        """
        name = f"%{name}%"
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE name LIKE %s ORDER BY created_at DESC",
                           (name,))
            result = cursor.fetchall()
            if result:
                activities = []
                for row in result:
                    activity = Activity(**row)
                    activities.append(activity)
                return activities
            else:
                return []

    def find_by_professor(self, professor_id) -> list[Activity]:
        """Buscar todas las actividades de un professor."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE professor_id = %s ORDER BY created_at DESC",
                           (professor_id,))
            result = cursor.fetchall()
            return [Activity(**activity) for activity in result]

    def find_by_due_date(self, due_date: datetime) -> list[Activity]:
        """Buscar actividades por fecha de entrega.

        Se asume due_date del tipo datetime.datetime y al buscar
        se utiliza solo due_date.date.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activities WHERE due_date = %s ORDER BY created_at DESC",
                           (due_date.date,))
            result = cursor.fetchall()
            return [Activity(**activity) for activity in result]

    def save(self, activity: Activity) -> Activity:
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
            except Error:
                conn.rollback()
                raise
            else:
                conn.commit()
                activity.id = res[-1]
                return self.find_by_id(activity.id)

    def update(self, activity: Activity) -> Activity:
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
            except Error:
                conn.rollback()
                raise
            else:
                conn.commit()
                return self.find_by_id(activity.id)

    def delete(self, activity_id: int) -> None:
        """Eliminar una actividad.

        Asume que se pasa una actividad con un id valido.
        Aunque puede no existir.
        """
        query = "DELETE FROM activities WHERE id = %s AND due_date > current_date()"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (activity_id,))
            except Error:
                conn.rollback()
                raise
            else:
                conn.commit()