from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(role):
    """
    Decorador para verificar el rol del usuario
    Args:
        role (str): Rol requerido ('professor' o 'student')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get("role") != role:
                    return jsonify({"msg": f"Acceso denegado: se requiere rol de {role}"}), 403
                return f(*args, **kwargs)
            except Exception:
                return jsonify({"msg": "Token inválido o expirado"}), 401
        return decorated_function
    return decorator