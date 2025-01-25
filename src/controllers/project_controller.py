from flask import request, jsonify, abort, Blueprint
from flask import current_app as app
from flask_jwt_extended import jwt_required, get_jwt

from src.services.project_service import ProjectService, ProjectServiceError

project_routes_bp = Blueprint('project_bp', __name__, url_prefix="/api/projects")

@project_routes_bp.route("/", methods=["POST"])
@jwt_required()
def create_project():
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"message": "Only students can create projects"}), 403

    try:
        project_data = {
            "title": request.form.get("title"),
            "repository_url": request.form.get("repository_url"),
            "activity_id": request.form.get("activity_id")
        }
        
        project = ProjectService(app.db).create_project(project_data, claims.get("student_id"))
        return jsonify({"message": f"Project {project.title} created successfully", "id": project.id}), 201
        
    except ProjectServiceError as e:
        return jsonify({"message": str(e)}), 401
    except Exception as e:
        app.logger.error(f"Error creating project: {str(e)}")
        abort(500)

@project_routes_bp.route("/<int:project_id>/members", methods=["POST"])
@jwt_required()
def add_member(project_id):
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"message": "Only students can be added to projects"}), 403

    try:
        member = ProjectService(app.db).add_member(
            project_id=project_id,
            student_id=request.form.get("student_id"),
            requesting_student_id=claims.get("student_id")
        )
        return jsonify({"message": "Member added successfully", "id": member.id}), 201
    except ProjectServiceError as e:
        return jsonify({"message": str(e)}), 401
    except Exception as e:
        app.logger.error(f"Error adding member: {str(e)}")
        abort(500)

@project_routes_bp.route("/", methods=["GET"])
@jwt_required()
def get_projects():
    filters = {}
    activity_id = request.args.get("activity_id")
    if activity_id:
        filters["activity_id"] = activity_id

    claims = get_jwt()
    if claims.get("role") == "student":
        filters["student_id"] = claims.get("student_id")
    elif claims.get("role") == "professor":
        filters["professor_id"] = claims.get("professor_id")
    else:
        return jsonify({"message": "Unauthorized role"}), 403

    try:
        projects = ProjectService(app.db).get_projects(filters)
        return jsonify(projects), 200
    except Exception as e:
        app.logger.error(f"Error retrieving projects: {str(e)}")
        abort(500)