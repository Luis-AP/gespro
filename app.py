from flask import Flask
from dotenv import load_dotenv
import os
from config import *
from src.db import Database
from src.controllers import *
from flask_cors import CORS

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

    # Initialize the database pool

    app.db = Database(app.config)

    # Register routes

    # app.register_blueprint(auth_routes)

    @app.route("/")
    def home():
        return "Welcome to GesPro API!"

    return app
