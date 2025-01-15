from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint

from src.models.user import Professor
from src.services.auth_service import AuthService
from src.db import DbError

professor_routes_bp = Blueprint(
    "professor_bp", __name__, url_prefix="/api/users/professors"
)


@professor_routes_bp.route("/<int:user_id>", methods=["GET"])
def get_professor(user_id):
    try:
        professor = AuthService(app.db).get_professor(user_id)
    except DbError:
        abort(500)
    else:
        if professor and isinstance(professor, Professor):
            return (
                jsonify(
                    {
                        "id": professor.id,
                        "email": professor.email,
                        "first_name": professor.first_name,
                        "last_name": professor.last_name,
                        "user_id": professor.user_id,
                        "department": professor.department,
                        "specialty": professor.specialty,
                        "created_at": professor.created_at,
                    }
                ),
                200,
            )
        abort(404)
