from flask_jwt_extended import JWTManager
from flask import request, make_response


def init_jwt(app):
    """Inicializa la configuración de JWT"""
    jwt = JWTManager(app)

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add(
                "Access-Control-Allow-Headers", "Content-Type,Authorization"
            )
            response.headers.add(
                "Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS"
            )
            return response

    @jwt.additional_claims_loader
    def add_role_to_token(identity):
        """Agrega el rol del usuario al token JWT"""
        import json

        json_identity = json.loads(identity)

        return {
            "role": json_identity.get("role", "student"),
            "user_id": json_identity.get("user_id"),
            "student_id": json_identity.get("student_id"),
            "professor_id": json_identity.get("professor_id"),
        }

    return jwt
