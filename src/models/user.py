class User:

    def __init__(
        self,
        user_id=None,
        email=None,
        password=None,
        first_name=None,
        last_name=None,
        created_at=None,
    ):
        self.id = user_id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = created_at

    def __repr__(self):
        return f"<User {self.email}>"


class Student(User):
    def __init__(
        self,
        user_id=None,
        email=None,
        password=None,
        first_name=None,
        last_name=None,
        created_at=None,
        student_id=None,
        enrollment_number=None,
        major=None,
        enrolled_at=None,
    ):
        super().__init__(
            user_id, email, password, first_name, last_name, created_at
        )
        self.id = student_id
        self.user_id = user_id
        self.enrollment_number = enrollment_number
        self.major = major
        self.enrolled_at = enrolled_at

    def __repr__(self):
        return f"<Student {self.email}>"


class Professor(User):
    def __init__(
        self,
        user_id=None,
        email=None,
        password=None,
        first_name=None,
        last_name=None,
        created_at=None,
        professor_id=None,
        department=None,
        speciality=None,
    ):
        super().__init__(
            user_id, email, password, first_name, last_name, created_at
        )
        self.id = professor_id
        self.user_id = user_id
        self.department = department
        self.speciality = speciality

    def __repr__(self):
        return f"<Professor {self.email}>"
