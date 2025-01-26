from src.models.user import Student, Professor
from typing import Union
from mysql.connector.errors import IntegrityError
from src.db import Database


class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Union[Student, Professor]:
        """Obtiene un usuario por su id, ya sea estudiante o profesor."""

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT u.id AS user_id, u.email, s.id AS student_id, p.id AS professor_id,
                    u.email, u.first_name, u.last_name, u.created_at,
                    s.enrollment_number, s.major, s.enrolled_at,
                    p.department, p.specialty,
                    CASE WHEN s.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_student
                FROM users u
                LEFT JOIN students s ON u.id = s.user_id
                LEFT JOIN professors p ON u.id = p.user_id
                WHERE u.id = %s
                """
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    if result["is_student"]:
                        user = Student(
                            id=result["student_id"],
                            user_id=result["user_id"],
                            first_name=result["first_name"],
                            last_name=result["last_name"],
                            enrollment_number=result["enrollment_number"],
                            major=result["major"],
                            enrolled_at=result["enrolled_at"],
                            created_at=result["created_at"],
                        )
                    else:
                        user = Professor(
                            id=result["professor_id"],
                            user_id=result["user_id"],
                            first_name=result["first_name"],
                            last_name=result["last_name"],
                            department=result["department"],
                            specialty=result["specialty"],
                            created_at=result["created_at"],
                        )
                    user.email = result["email"]
                    return user
                return None
        except:
            raise

    def get_user_by_email(self, email: str) -> Union[Student, Professor]:
        """Obtiene un usuario por su email, ya sea estudiante o profesor."""

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT u.id AS user_id, u.password, s.id AS student_id, p.id AS professor_id,
                    CASE WHEN s.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_student
                FROM users u
                LEFT JOIN students s ON u.id = s.user_id
                LEFT JOIN professors p ON u.id = p.user_id
                WHERE u.email = %s
                """
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                if result:
                    if result["is_student"]:
                        user = Student(
                            id=result["student_id"],
                            user_id=result["user_id"],
                            password=result["password"],
                        )
                    else:
                        user = Professor(
                            id=result["professor_id"],
                            user_id=result["user_id"],
                            password=result["password"],
                        )
                    user.email = email
                    return user
                return None
        except:
            raise

    def get_students(self, filter_criteria: dict = None) -> list:
        """Devuelve una lista de estudiantes.
        Args:
            filter_criteria (dict): Criterios de filtrado.
        Returns:
            list: Lista de estudiantes.
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT s.*, u.email, u.first_name, u.last_name, u.created_at
                FROM students s
                JOIN users u ON s.user_id = u.id
                """
                if filter_criteria:
                    query += " WHERE "
                    query += " AND ".join(
                        f"{key} = %s" for key in filter_criteria.keys()
                    )
                    cursor.execute(query, tuple(filter_criteria.values()))
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
                students = []
                for result in results:
                    student = Student(
                        id=result["id"],
                        email=result["email"],
                        first_name=result["first_name"],
                        last_name=result["last_name"],
                        enrollment_number=result["enrollment_number"],
                        major=result["major"],
                        enrolled_at=result["enrolled_at"],
                    )
                    students.append(student)
                return students
        except:
            raise

    def get_professors(self, filter_criteria: dict = None) -> list:
        """Devuelve una lista de profesores.
        Args:
            filter_criteria (dict, optional): Criterios de filtrado. Por defecto es None.
        Returns:
            list: Lista de profesores.
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT p.*, u.email, u.first_name, u.last_name, u.created_at
                FROM professors p
                JOIN users u ON p.user_id = u.id
                """
                if filter_criteria:
                    query += " WHERE "
                    query += " AND ".join(
                        f"{key} = %s" for key in filter_criteria.keys()
                    )
                    cursor.execute(query, tuple(filter_criteria.values()))
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
                professors = []
                for result in results:
                    professor = Professor(
                        id=result["id"],
                        email=result["email"],
                        first_name=result["first_name"],
                        last_name=result["last_name"],
                        department=result["department"],
                        specialty=result["specialty"],
                    )
                    professors.append(professor)
                return professors
        except:
            raise

    def create_student(self, student: Student) -> Student:
        """Llama al procedimiento almacenado para crear un estudiante."""
        with self.db.get_connection() as conn:
            try:
                cursor = conn.cursor()
                res = cursor.callproc(
                    "CreateStudent",
                    (
                        student.email,
                        student.password,
                        student.first_name,
                        student.last_name,
                        student.enrollment_number,
                        student.major,
                        student.enrolled_at,
                        None,
                    ),
                )
            except IntegrityError:
                conn.rollback()
                raise
            else:
                conn.commit()
                student.id = res[-1]
                student.password = None
                return student

    def get_professor_by_id(self, professor_id: int) -> dict:
        query = "SELECT * FROM professors WHERE id = %s"
        with self.db.get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, (professor_id,))
            professor_data =cur.fetchone()
            if professor_data:
                return Professor(**professor_data)
            else:
                return None
            
    def search_students(self, search_term: str) -> list:
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT s.*, u.email, u.first_name, u.last_name
                FROM students s
                JOIN users u ON s.user_id = u.id
                WHERE u.first_name LIKE %s 
                OR u.last_name LIKE %s 
                OR u.email LIKE %s
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern))
                results = cursor.fetchall()
                return [Student(**r) for r in results]
        except:
            raise

    def get_student_by_student_id(self, student_id: int) -> Student:
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT s.*, u.email, u.first_name, u.last_name, u.created_at
                FROM students s
                JOIN users u ON s.user_id = u.id
                WHERE s.id = %s
                """
                cursor.execute(query, (student_id,))
                result = cursor.fetchone()
                if result:
                    return Student(**result)
                return None
        except:
            raise

    def get_professor_by_professor_id(self, professor_id: int) -> Professor:
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT p.*, u.email, u.first_name, u.last_name, u.created_at
                FROM professors p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s
                """
                cursor.execute(query, (professor_id,))
                result = cursor.fetchone()
                if result:
                    return Professor(**result)
                return None
        except:
            raise