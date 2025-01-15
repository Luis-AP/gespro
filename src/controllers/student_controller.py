from flask import request
from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint

from src.models.user import Student
from src.services.auth_service import AuthService
from src.db import DbError

student_routes_bp = Blueprint(
    "student_bp", __name__, url_prefix="/api/users/students"
)


@student_routes_bp.route("/<int:user_id>", methods=["GET"])
def get_student(user_id):
    try:
        student = AuthService(app.db).get_student(user_id)
    except DbError:
        abort(500)
    else:
        if student and isinstance(student, Student):
            return (
                jsonify(
                    {
                        "id": student.id,
                        "email": student.email,
                        "first_name": student.first_name,
                        "last_name": student.last_name,
                        "user_id": student.user_id,
                        "enrollment_number": student.enrollment_number,
                        "major": student.major,
                        "enrolled_at": student.enrolled_at,
                        "created_at": student.created_at,
                    }
                ),
                200,
            )
        abort(404)
