from flask import Flask
from dotenv import load_dotenv
import os
from config import *
from src.db import Database
from src.controllers import *
from flask_cors import CORS
from src.utils.jwt_config import init_jwt
from src.utils.error_handlers import register_error_handlers
from src.controllers.auth_controller import auth_routes_bp
from src.controllers.activity_controller import activity_routes_bp
from src.controllers.student_controller import student_routes_bp
from src.controllers.professor_controller import professor_routes_bp

load_dotenv()


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    # Enable CORS for all domains
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Load the configuration
    env = os.getenv("FLASK_ENV", "development").lower()

    print(f"Running in {env} mode")

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

    with app.db.get_connection() as connection:
        with connection.cursor() as cursor:
            print(class_config.DB_NAME)
            cursor.execute("""
                SELECT ROUTINE_NAME, ROUTINE_TYPE, ROUTINE_SCHEMA
                FROM information_schema.ROUTINES
                WHERE ROUTINE_SCHEMA = %s
            """, (class_config.DB_NAME,))
            procedures = cursor.fetchall()
            print("\nStored Procedures in database:")
            for proc in procedures:
                print(f"- {proc[0]} ({proc[1]}) in schema {proc[2]}")
            print("\n")

    # Register routes

    # app.register_blueprint(auth_routes)
    app.register_blueprint(auth_routes_bp)
    app.register_blueprint(activity_routes_bp)
    app.register_blueprint(student_routes_bp)
    app.register_blueprint(professor_routes_bp)

    @app.route("/")
    def home():
        return "Welcome to GesPro API!"

    return app
