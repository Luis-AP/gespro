import json

import bcrypt
from flask import jsonify
from flask_jwt_extended import create_access_token

from src.models.user import User, Student, Professor
from src.repositories.user_repository import UserRepository
from mysql.connector.errors import IntegrityError
from src.db import DbError

class AuthPasswordError(Exception):
    pass


class AuthService:
    def __init__(self, db):
        try:
            self.user_repository = UserRepository(db)
        except DbError:
            raise

    def login(self, user: User) -> tuple:
        try:
            # Intentar obtener el usuario por su email
            saved_user = self.user_repository.get_user_by_email(user.email)
            
            if not saved_user:
                return None, "INVALID_CREDENTIALS"
                
            # Segunda validación: contraseña correcta    
            user_pass_bytes = user.password.encode("utf-8")
            if not bcrypt.checkpw(user_pass_bytes, saved_user.password):
                return None, "INVALID_CREDENTIALS"
            
            # Si las credenciales son correctas
            if isinstance(saved_user, Student):
                token = create_access_token(
                    json.dumps(
                        {"user_id": saved_user.user_id, "role": "student"}
                    )
                )
                return token, "student"
            elif isinstance(saved_user, Professor):
                token = create_access_token(
                    json.dumps(
                        {"user_id": saved_user.user_id, "role": "professor"}
                    )
                )
                return token, "professor"
                
        except Exception as e:
            return None, "SERVER_ERROR"

    def create_student(self, student: Student):
        if not student.email:
            raise ValueError(f"Email empty.")
        # Validar requisitos de contraseña (8-16 caracteres, una mayúscula y un número)
        if not (len(student.password) > 8 and len(student.password) < 16):
            raise AuthPasswordError(
                f"Non conforming password. Password length: {len(student.password)}"
            )
        try:
            student.password = bcrypt.hashpw(
                student.password.encode("utf-8"), bcrypt.gensalt()
            )
            saved_student = self.user_repository.create_student(student)
        except IntegrityError as err:
            # devolver el mismo student, sin id
            return student
        else:
            # devolver el estudiante guardado con su id
            return saved_student

    def get_student(self, user_id: int) -> Student:
        student = self.user_repository.get_user_by_id(user_id)
        if isinstance(student, Student):
            return student
        else:
            return None

    def get_professor(self, user_id: int) -> Professor:
        professor = self.user_repository.get_user_by_id(user_id)
        if isinstance(professor, Professor):
            return professor
        else:
            return None