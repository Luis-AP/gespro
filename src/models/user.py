class User:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.email = kwargs.get("email")
        self.password = kwargs.get("password")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.created_at = kwargs.get("created_at")

    def __repr__(self):
        return f"<User {self.email}>"


class Student(User):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = kwargs.get("user_id")
        self.enrollment_number = kwargs.get("enrollment_number")
        self.major = kwargs.get("major")
        self.enrolled_at = kwargs.get("enrolled_at")

    def __repr__(self):
        return f"<Student {self.email}>"


class Professor(User):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = kwargs.get("user_id")
        self.department = kwargs.get("department")
        self.specialty = kwargs.get("specialty")

    def __repr__(self):
        return f"<Professor {self.email}>"
