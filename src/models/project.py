class Project:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.repository_url = kwargs.get("repository_url")
        self.activity_id = kwargs.get("activity_id")
        self.is_group = kwargs.get("is_group", False)
        self.grade = kwargs.get("grade")
        self.status = kwargs.get("status", "OPEN")
        self.created_at = kwargs.get("created_at")
        self.updated_at = kwargs.get("updated_at")

    def __repr__(self):
        return f"<Project {self.title}>"