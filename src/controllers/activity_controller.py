from flask import request
from flask import current_app as app
from flask import jsonify
from flask import abort
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from mysql.connector.errors import Error, IntegrityError, DataError

from src.models.activity import Activity
from src.services.activity_service import ActivityService, ActivityOwnerError
from src.repositories.activity_repository import ActivityRepository

activity_routes_bp = Blueprint('activity_bp', __name__, url_prefix="/api/activities")

@activity_routes_bp.route("/", methods=["GET"])
@jwt_required()
def get_activities():
    claims = get_jwt()
    role = claims["role"]
    activity_service = ActivityService(app.db)
    if role == "student":
        professor_id = request.args.get("professor_id")
    else:
        professor_id = claims["professor_id"]
    activities = activity_service.get_activities(professor_id)

    if activities:
        return jsonify(activities), 200
    else:
        abort(404)

@activity_routes_bp.route("/<int:activity_id>", methods=["GET"])
def get_activity(activity_id: int):
    """DEPRECATED. nadie me usa :("""
    app.logger.warning("Deprecation warning: get_activity. This endpoint might go away in the future.")
    activity= ActivityRepository(app.db).find_by_id(activity_id)
    if activity.id:
        response = {"Deprecation warning": "This endpoint might go away in the future."}
        response.update(activity.__dict__)
        return jsonify(response), 200
    else:
        abort(404)

@activity_routes_bp.route("/", methods=["POST"])
@jwt_required()
def create_activity():
    claims = get_jwt()
    if claims["role"] != "professor":
        abort(403)
    activity = Activity(name=request.form.get("name"),
                        description=request.form.get("description"),
                        due_date=request.form.get("due_date"),
                        min_grade=request.form.get("min_grade"),
                        professor_id=claims["professor_id"])
    try:
        activity = ActivityService(app.db).create(activity)
    except ValueError as err:
        return jsonify({"message": f"Value error: {err}"}), 422
    except DataError as err:
        return jsonify({"message": "Wrong size/format data."}), 422
    except IntegrityError as err:
        return jsonify({"message": "Bad professor id."}), 422
    except Error as err:
        app.logger.error("MySQL error. %s - %s", err.errno, err.msg)
        abort(500)
    else:
        if activity.id:
            return jsonify(activity.__dict__), 200
        else:
            abort(500)

@activity_routes_bp.route("/<int:activity_id>", methods=["PATCH"])
@jwt_required()
def update_activity(activity_id: int):
    claims = get_jwt()
    if claims["role"] != "professor":
        abort(403)
    activity = Activity(id=activity_id,
                        name=request.form.get("name"),
                        description=request.form.get("description"),
                        due_date=request.form.get("due_date"),
                        min_grade=request.form.get("min_grade"),
                        professor_id=claims["professor_id"])
    try:
        activity = ActivityService(app.db).update(activity)
    except ActivityOwnerError as err:
        return jsonify({"message": f"{err}"}), 403
    except ValueError as err:
        return jsonify({"message": f"Value error: {err}"}), 422
    except IntegrityError:
        return jsonify({"message": "Bad professor id."}), 422
    except DataError as err:
        return jsonify({"message": "Wrong size/format data."}), 422
    except Error as err:
        app.logger.error("MySQL error. %s - %s", err.errno, err.msg)
        abort(500)
    else:
        if activity.id is None:
            abort(404)
        else:
            return jsonify(activity.__dict__), 200

@activity_routes_bp.route("/<int:activity_id>", methods=["DELETE"])
@jwt_required()
def delete_activity(activity_id):
    claims = get_jwt()
    if claims["role"] != "professor":
        abort(403)
    try:
        ActivityService(app.db).delete(activity_id, claims["professor_id"])
    except ValueError as err:
        return jsonify({"message": f"Value error. {err}"}), 422
    except ActivityOwnerError as err:
        return jsonify({"message": f"Unable to delete. {err}"}), 403
    except Error as err:
        app.logger.error("MySQL error. %s - %s", err.errno, err.msg)
        abort(500)
    else:
        return '', 204
