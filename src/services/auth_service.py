import bcrypt

from src.models import User, Student, Professor
from src.repositories import UserRepository, UserRepositoryError


class AuthService:
    def __init__(self, db):
        self.user_repository = UserRepository(db.get_connection)
    
    def login(self, user: User) -> str:
        saved_user = self.user_repository.get_user_by_email(user.email)
        # devuelve una instancia de professor o student para simplificar 
        # 
        if bcrypt.checkpw(user.password, saved_user.password):
            # login correcto obtener token
            if isinstance(saved_user, Student):
                pass # get student token
            else:
                pass  # get professor token

    def create_student(self, student):
        try
            saved_student = self.user_repository.create_student(student)
        except UserRepositoryError as err:
