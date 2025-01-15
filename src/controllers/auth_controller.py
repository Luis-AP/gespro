from flask import request
from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint

from src.models.user import User, Student
from src.services.auth_service import AuthService

auth_routes_bp = Blueprint('auth_bp', __name__, url_prefix="/api/auth")

@auth_routes_bp.route("/register", methods=["POST"])
def register_student():
    student_to_register = Student(
                            email=request.form.get("email", ''),
                            password=request.form.get("password", ''),
                            first_name=request.form.get("first_name", ''),
                            last_name=request.form.get("last_name", ''),
                            enrollment_number=request.form.get("enrollment_number", ''),
                            major=request.form.get("major", ''),
                            enrolled_at=request.form.get("enrolled_at", '')
    )
    saved_student = AuthService(app.db).create_student(student_to_register)
    if saved_student.id:
        return jsonify({"message": f"Student {saved_student.email} successfully saved"}), 200
    else:
        return jsonify({"message": "Error al guardar el coso"}), 500

@auth_routes_bp.route('/login', methods=['POST'])
def login():
    user = User(email=request.form.get("email", ''),
                password=request.form.get("password", ''))

    token, role = AuthService(app.db).login(user)
    if token:
        return jsonify({"token": token, "role": role}), 200
    else:
        abort(404)