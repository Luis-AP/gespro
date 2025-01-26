from flask import request
from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint

from src.models.user import Student
from src.services.auth_service import AuthService
from src.db import DbError
from flask_jwt_extended import jwt_required

student_routes_bp = Blueprint(
    "student_bp", __name__, url_prefix="/api/users/students"
)


@student_routes_bp.route("/search", methods=["GET"])
@jwt_required()
def search_students():
    search_term = request.args.get("q", "")
    if not search_term or len(search_term) < 2:
        return jsonify([]), 200

    try:
        students = AuthService(app.db).search_students(search_term)
        return jsonify([{
            "id": s.id,
            "email": s.email,
            "first_name": s.first_name,
            "last_name": s.last_name
        } for s in students]), 200
    except DbError:
        abort(500)

@student_routes_bp.route("/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_by_student_id(student_id):
    try:
        student = AuthService(app.db).get_student_by_student_id(student_id)
        if student:
            return jsonify(student), 200
        abort(404)
    except DbError:
        abort(500)