# src/utils/error_handlers.py
from flask import jsonify

def register_error_handlers(app):
    """Registra los manejadores de errores para la aplicación"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Maneja errores de petición incorrecta"""
        return jsonify({
            "error": "Solicitud incorrecta",
            "mensaje": str(error.description)
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        """Maneja errores de autenticación"""
        return jsonify({
            "error": "No autorizado",
            "mensaje": "Debe iniciar sesión para acceder a este recurso"
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        """Maneja errores de permisos"""
        return jsonify({
            "error": "Acceso denegado",
            "mensaje": "No tiene permisos para acceder a este recurso"
        }), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores de recurso no encontrado"""
        return jsonify({
            "error": "No encontrado",
            "mensaje": "El recurso solicitado no existe"
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Maneja errores internos del servidor"""
        app.logger.error(f"Error interno: {str(error)}")
        return jsonify({
            "error": "Error del servidor",
            "mensaje": "Ha ocurrido un error interno en el servidor"
        }), 500