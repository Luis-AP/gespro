from flask import request
from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint

from src.models.user import User, Student
from src.services.auth_service import AuthService, AuthPasswordError
from src.db import DbError
from flask_jwt_extended import jwt_required, get_jwt

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
    try:
        saved_student = AuthService(app.db).create_student(student_to_register)
    except DbError:
        abort(500)
    except AuthPasswordError:
        return jsonify({"message": "La contraseña no cumple las condiciones."}), 401
    except ValueError:
        return jsonify({"message": "Empty email"}), 401
    else:
        if saved_student.id:
            return jsonify({"message": f"Estudiante {saved_student.email} guardado con éxito."}), 200
        else:
            return jsonify({"message": "Error de integridad: el correo o número de matrícula ya existe."}), 500

@auth_routes_bp.route('/login', methods=['POST'])
def login():
    user = User(email=request.form.get("email", ''),
                password=request.form.get("password", ''))

    token, result, professor_id, student_id  = AuthService(app.db).login(user)

    if token:
        return jsonify({"token": token, "role": result, "professor_id": professor_id, "student_id": student_id}), 200
        
    if result == "INVALID_CREDENTIALS":
        return jsonify({
            "error": "Credenciales inválidas",
            "message": "Credenciales inválidas. Por favor, revisa tu email y contraseña."
        }), 401
    else:
        abort(500)

@auth_routes_bp.route("/validate", methods=["GET"])
@jwt_required()
def validate_token():
    """Valida el token JWT y retorna la información del usuario"""
    try:
        claims = get_jwt()
        user_id = claims.get("user_id")
        role = claims.get("role")
        student_id = claims.get("student_id")
        professor_id = claims.get("professor_id")
        
        if role == "student":
            user = AuthService(app.db).get_student(user_id)
        else:
            user = AuthService(app.db).get_professor(user_id)
        
        if user:
            return jsonify({
                "id": user.user_id,
                "student_id": student_id if role == "student" else None,
                "professor_id": professor_id if role == "professor" else None,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": role,
                "enrollmentNumber": user.enrollment_number if role == "student" else None,
                "major": user.major if role == "student" else None,
                "department": user.department if role == "professor" else None,
                "specialty": user.specialty if role == "professor" else None
            }), 200
        else:
            abort(404)
            
    except Exception as e:
        app.logger.error(f"Error validando token: {str(e)}")
        abort(500)
