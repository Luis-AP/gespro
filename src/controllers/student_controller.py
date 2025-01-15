from flask import jsonify
from flask import current_app as app

from src.repositories.user_repository import UserRepository
from src.models.user import Student

class StudentController:

    @staticmethod
    def get_student(user_id: int):
        user_repository = UserRepository(app.db.get_connection())
        student = user_repository.get_user_by_id(user_id)
        if isinstance(student, Student):
            if student:
                return jsonify({"message": f"Student {student.id} obtained"}), 200
        return jsonify({"message": "Not found"}), 404
