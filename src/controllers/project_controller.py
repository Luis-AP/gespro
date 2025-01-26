from flask import request, jsonify, abort, Blueprint
from flask import current_app as app
from flask_jwt_extended import jwt_required, get_jwt

from src.services.project_service import (
    ProjectService, ProjectServiceError, ProjectValueError, ProjectOwnerError, NotFoundError)
from src.models.project import Project

project_routes_bp = Blueprint('project_bp', __name__, url_prefix="/api/projects")

@project_routes_bp.route("/", methods=["POST"])
@jwt_required()
def create_project():
    claims = get_jwt()
    if claims.get("role") != "student":
        abort(403, description="Only students can create projects")

    try:
        project = Project(
            title = request.json.get("title"),
            repository_url = request.json.get("repository_url"),
            activity_id = request.json.get("activity_id")
        )
        
        project = ProjectService(app.db).create_project(project, claims.get("student_id"))
        return jsonify(project), 201
        
    except ProjectValueError as e:
        abort(400, description=str(e))
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except Exception as e:
        app.logger.error(f"Error creating project: {str(e)}")
        abort(500, description=str(e))

@project_routes_bp.route("/<int:project_id>/members", methods=["POST"])
@jwt_required()
def add_member(project_id: int):
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"message": "Only students can add members to projects"}), 403

    try:
        member = ProjectService(app.db).add_member(
            project_id=project_id,
            student_id=request.json.get("student_id"),
            requesting_student_id=claims.get("student_id")
        )
        return jsonify({"message": "Member added successfully", "id": member.id}), 201
    except ProjectValueError as e:
        abort(400, description=str(e))
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except ProjectOwnerError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except Exception as e:
        app.logger.error("Error adding member: %s", e)
        abort(500)

@project_routes_bp.route("/", methods=["GET"])
@jwt_required()
def get_projects():
    # Controlamos que solo los estudiantes y profesores puedan ver los proyectos
    claims = get_jwt()
    
    filters = {}
    if claims.get("role") == "student":
        filters["student_id"] = claims.get("student_id")
    elif claims.get("role") == "professor":
        filters["professor_id"] = claims.get("professor_id")
    else:
        return jsonify({"message": "Unauthorized role"}), 403
    
    # Filtramos por id de actividad si se proporciona
    activity_id = request.args.get("activity_id")
    if activity_id:
        filters["activity_id"] = activity_id

    try:
        projects = ProjectService(app.db).get_projects(filters)
        return jsonify(projects), 200
    except Exception as e:
        app.logger.error(f"Error retrieving projects: {str(e)}")
        abort(500, description=str(e))

@project_routes_bp.route("/<int:project_id>/members/<int:student_id>", methods=["DELETE"])
@jwt_required()
def remove_member(project_id: int, student_id: int):
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"message": "Only students can remove members from projects"}), 403

    try:
        ProjectService(app.db).remove_member(
            project_id=project_id,
            student_id=student_id,
            requesting_student_id=claims.get("student_id")
        )
        return jsonify({"message": "Member removed successfully"}), 200
    except ProjectValueError as e:
        abort(401, description=str(e))
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except ProjectOwnerError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except Exception as e:
        app.logger.error("Error removing member: %s", e)
        abort(500, description=str(e))

@project_routes_bp.route("/<int:project_id>", methods=["PATCH"])
@jwt_required()
def update_project(project_id: int):
    claims = get_jwt()
    if claims["role"] != "student":
        abort(403, description="Only students can update projects")

    project = Project(
        id=project_id,
        title=request.json.get("title"),
        repository_url=request.json.get("repository_url"),
    )

    student_id = claims["student_id"]
    try:
        project = ProjectService(app.db).update(project, student_id)
    except ProjectValueError as e:
        abort(400, description=str(e))
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except ProjectOwnerError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except Exception as e:
        app.logger.error(f"Error updating project: {str(e)}")
        abort(500, description=str(e))
    else:
        return jsonify(project), 200

@project_routes_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id: int):
    claims = get_jwt()
    if claims["role"] != "student":
        abort(403, description="Only students can delete projects")

    try:
        ProjectService(app.db).delete(project_id, claims["student_id"])
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except ProjectOwnerError as e:
        abort(403, description=str(e))
    except Exception as e:
        app.logger.error(f"Error deleting project: {str(e)}")
        abort(500, description=str(e))
    else:
        return "", 204