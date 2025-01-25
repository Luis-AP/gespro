class Member:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.project_id = kwargs.get("project_id")
        self.student_id = kwargs.get("student_id")
        self.is_owner = kwargs.get("is_owner", False)
        self.joined_at = kwargs.get("joined_at")

    def __repr__(self):
        return f"<Member {self.student_id} of Project {self.project_id}>"