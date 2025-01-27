from datetime import datetime

class Activity:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.due_date = kwargs.get("due_date")
        self.min_grade = kwargs.get("min_grade")
        self.professor_id = kwargs.get("professor_id")
        self.created_at = kwargs.get("created_at")
        self.updated_at = kwargs.get("updated_at")

    def __repr__(self):
        attrs = (f"{k}={v}" for k,v in self.__dict__.items())
        return "{}({})".format(self.__class__.__name__, f", ".join(attrs))
