from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    """Base configuration."""

    TESTING = False
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora en segundos


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


class DevelopmentConfig(Config):
    """Development configuration."""

    DB_HOST = "localhost"


class TestingConfig(Config):
    """Testing configuration."""

    DB_HOST = os.getenv("TEST_DB_HOST")
    DB_PORT = os.getenv("TEST_DB_PORT")
    DB_USER = os.getenv("TEST_DB_USER")
    DB_PASSWORD = os.getenv("TEST_DB_PASSWORD")
    DB_NAME = os.getenv("TEST_DB_NAME")
    TESTING = True
