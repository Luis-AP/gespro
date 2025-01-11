from flask_jwt_extended import JWTManager

def init_jwt(app):
    """Inicializa la configuración de JWT"""
    jwt = JWTManager(app)
    
    @jwt.additional_claims_loader
    def add_role_to_token(identity):
        """Agrega el rol del usuario al token JWT"""
        return {
            "role": identity.get("role", "student"),
            "user_id": identity.get("id")
        }
    
    return jwt