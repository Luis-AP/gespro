from src.models.project import Project
from src.models.member import Member
from mysql.connector.errors import IntegrityError
from mysql.connector.errors import DatabaseError
from mysql.connector.errors import Error

class ProjectError(Exception):
    pass

class ProjectRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self) -> list[dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM projects")
            return cursor.fetchall()

    def find_by_id(self, project_id: int) -> Project:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
            project = cursor.fetchone()
            return Project(**project) if project else Project(id=None)

    def find_by_activity(self, activity_id: int) -> list[dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM projects WHERE activity_id = %s", (activity_id,))
            return cursor.fetchall()

    def find_projects_with_details(self, filters: dict = None) -> list[dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.*, a.name as activity_name, a.due_date, a.professor_id,
                       GROUP_CONCAT(DISTINCT m2.student_id) as member_ids
                FROM projects p
                JOIN activities a ON p.activity_id = a.id
                LEFT JOIN members m ON p.id = m.project_id
                LEFT JOIN members m2 ON p.id = m2.project_id
            """
            where_clauses = []
            params = []

            if filters:
                if 'student_id' in filters:
                    where_clauses.append("m.student_id = %s")
                    params.append(filters['student_id'])
                if 'professor_id' in filters:
                    where_clauses.append("a.professor_id = %s")
                    params.append(filters['professor_id'])
                if 'activity_id' in filters:
                    where_clauses.append("p.activity_id = %s")
                    params.append(filters['activity_id'])

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " GROUP BY p.id, a.name, a.due_date"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    def get_project_members(self, project_id: int) -> list[Member]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM members WHERE project_id = %s", (project_id,))
            results = cursor.fetchall()
            return [Member(**member) for member in results] if results else []

    def create_project(self, project: Project, student_id: int) -> Project:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                res = cursor.callproc("CreateProject", 
                    (project.title,
                     project.repository_url,
                     project.activity_id,
                     student_id,
                     None))
                conn.commit()
                project.id = res[-1]
                return project
            except DatabaseError as e:
                conn.rollback()
                if e.errno == 1644:  # SQLSTATE '45000'
                    raise ProjectError("Student already participates in a project for this activity")
                raise IntegrityError from e

    def is_project_owner(self, project_id: int, student_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT 1 FROM members WHERE project_id = %s AND student_id = %s AND is_owner = 1",
                (project_id, student_id)
            )
            return cursor.fetchone() is not None

    def validate_member(self, student_id: int, project_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM members WHERE student_id = %s AND project_id = %s",
                (student_id, project_id)
            )
            return cursor.fetchone() is not None

    def add_member(self, student_id: int, project_id: int) -> Member:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                res = cursor.callproc("AddMember", 
                    (student_id,
                     project_id,
                     None))
                conn.commit()
                return Member(id=res[-1], 
                            project_id=project_id, 
                            student_id=student_id)
            except DatabaseError as e:
                conn.rollback()
                if e.errno == 1644:  # SQLSTATE '45000'
                    raise ProjectError("Student already participates in a project for this activity")
            except IntegrityError:
                conn.rollback()
                raise ProjectError("The ID doesn't belong to any student")
            except Error as e:
                conn.rollback()
                raise

    def remove_student_from_project(self, student_id: int, project_id: int) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "DELETE FROM members WHERE student_id = %s AND project_id = %s",
                    (student_id, project_id)
                )
                
                # Si solo queda un miembro en el proyecto, se convierte en un proyecto individual
                cursor.execute("""
                    UPDATE projects p
                    SET is_group = CASE 
                        WHEN (SELECT COUNT(*) FROM members m WHERE m.project_id = p.id) <= 1 THEN 0
                        ELSE 1
                    END
                    WHERE id = %s
                """, (project_id,))
                
                conn.commit()
            except IntegrityError:
                conn.rollback()
                raise ProjectError("Cannot remove student from project")

    def update_status(self, project_id: int, status: str):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE projects SET status = %s WHERE id = %s",
                    (status, project_id)
                )
                conn.commit()
            except IntegrityError:
                conn.rollback()
                raise
                
    def update_grade(self, project_id: int, grade: float):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE projects SET grade = %s, status = 'GRADED' WHERE id = %s",
                    (grade, project_id)
                )
                conn.commit()
            except IntegrityError:
                conn.rollback()
                raise

    def update(self, project: Project) -> Project:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE projects SET title = %s, repository_url = %s WHERE id = %s",
                    (project.title, project.repository_url, project.id)
                )
            except Error:
                conn.rollback()
                raise ProjectError("Error updating project")
            else:
                conn.commit()
                return self.find_by_id(project.id)

    def delete(self, project_id: int) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
            except Error:
                conn.rollback()
                raise ProjectError("Error deleting project")
            else:
                conn.commit()