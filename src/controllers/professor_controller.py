from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint

from src.models.user import Professor
from src.services.auth_service import AuthService
from flask_jwt_extended import jwt_required
from src.db import DbError

professor_routes_bp = Blueprint(
    "professor_bp", __name__, url_prefix="/api/users/professors"
)


@professor_routes_bp.route("/<int:professor_id>", methods=["GET"])
@jwt_required()
def get_professor_by_professor_id(professor_id):
    try:
        professor = AuthService(app.db).get_professor_by_professor_id(professor_id)
        if professor:
            return jsonify(professor), 200
        abort(404)
    except DbError:
        abort(500)