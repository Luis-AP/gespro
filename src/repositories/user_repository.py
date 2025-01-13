from src.models.user import User, Student, Professor


class UserRepository:

    def __init__(self, connection):
        self.connection = connection

    def find_by_email(self, user):
        query = "SELECT * FROM users WHERE email = %s"
        cursor = self.connection.cursor(dictionary=True)

        cursor.execute(query, (user.email,))

        result = cursor.fetchone()

        cursor.close()
        self.connection.close()

        if result:
            user.id = result["id"]
            user.first_name = result["first_name"]
            user.last_name = result["last_name"]
            user.created_at = result["created_at"]
        return None

    def _save_user(self, user):
        pass

    def save_student(self, student):
        pass
