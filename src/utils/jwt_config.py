from flask_jwt_extended import JWTManager


def init_jwt(app):
    """Inicializa la configuración de JWT"""
    jwt = JWTManager(app)
    
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
