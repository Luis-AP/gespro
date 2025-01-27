import os

from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv
from config import *
from src.db import Database
from src.controllers import *
from src.utils.custom_json_provider import CustomJSONProvider
from src.utils.jwt_config import init_jwt
from src.utils.error_handlers import register_error_handlers
from src.controllers.auth_controller import auth_routes_bp
from src.controllers.activity_controller import activity_routes_bp
from src.controllers.student_controller import student_routes_bp
from src.controllers.professor_controller import professor_routes_bp
from src.controllers.project_controller import project_routes_bp

load_dotenv()


def create_app():
    """Application factory function."""
    app = Flask(__name__)

    app.json = CustomJSONProvider(app)

    # Enable CORS for all domains
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["*"],
                "methods": [
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE",
                    "OPTIONS",
                ],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    # Load the configuration
    env = os.getenv("FLASK_ENV", "development").lower()

    app.logger.info("Running in %s environment", env)

    class_config = {
        "production": ProductionConfig,
        "development": DevelopmentConfig,
        "testing": TestingConfig,
    }.get(env, DevelopmentConfig)

    app.config.from_object(class_config)

    # Inicializar JWT
    init_jwt(app)

    # Registrar manejadores de errores
    register_error_handlers(app)

    # Initialize the database pool

    app.db = Database(class_config)

    # Register routes

    # app.register_blueprint(auth_routes)
    app.register_blueprint(auth_routes_bp)
    app.register_blueprint(activity_routes_bp)
    app.register_blueprint(student_routes_bp)
    app.register_blueprint(professor_routes_bp)
    app.register_blueprint(project_routes_bp)

    @app.route("/")
    def home():
        return "Welcome to GesPro API!"

    return app
