from datetime import datetime

from flask.json.provider import DefaultJSONProvider

from src.models.activity import Activity
from src.models.project import Project


class CustomJSONProvider(DefaultJSONProvider):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    def default(self, o):
        if isinstance(o, Activity):
            o.due_date = o.due_date.strftime("%Y-%m-%d") if isinstance(o.due_date, datetime) else o.due_date
            o.created_at = o.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(o.created_at, datetime) else o.created_at
            o.updated_at = o.updated_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(o.updated_at, datetime) else o.updated_at
            return o.__dict__

        if isinstance(o, Project):
            o.created_at = o.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(o.created_at, datetime) else o.created_at
            o.updated_at = o.updated_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(o.updated_at, datetime) else o.updated_at
            return o.__dict__

        return super().default(o)
