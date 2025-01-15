from datetime import datetime

from flask import request
from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint

from src.models.activity import Activity
from src.repositories.activity_repository import ActivityRepository
from mysql.connector.errors import IntegrityError

activity_routes_bp = Blueprint('activity_bp', __name__, url_prefix="/api/activities")

@activity_routes_bp.route("/", methods=["GET"])
def get_activities():
    professor_id = request.args.get("professor_id", '')
    if professor_id:
        print("get_activities_by_professor -> ?professor_id: ", professor_id)
        user_repository = ActivityRepository(app.db)
        activities = user_repository.find_by_professor(professor_id)
    else:
        user_repository = ActivityRepository(app.db)
        activities = user_repository.find_all()
    if activities:
        return jsonify(activities), 200
    else:
        abort(404)

@activity_routes_bp.route("/<int:activity_id>", methods=["GET"])
def get_activity(activity_id: int):
    user_repository = ActivityRepository(app.db)
    activity = user_repository.find_by_id(activity_id)
    if activity.id:
        return jsonify(activity.__dict__), 200
    else:
        abort(404)

@activity_routes_bp.route("/", methods=["POST"])
def create_activity():
    activity_to_register = Activity(
        name=request.form.get("name", ''),
        description=request.form.get("description", ''),
        due_date=datetime.strptime(request.form.get("due_date", ''), "%Y-%m-%d %H:%M:%S.%f"),
        min_grade=request.form.get("min_grade", ''),
        professor_id=request.form.get("professor_id", '')
    )
    try:
        activity = ActivityRepository(app.db).save(activity_to_register)
    except IntegrityError:
        # fk de professor_id debe ser erronea
        abort(500)
    else:
        if activity.id:
            return jsonify({"message": f"Activity {activity.name} successfully saved"}), 200
        else:
            abort(500)
