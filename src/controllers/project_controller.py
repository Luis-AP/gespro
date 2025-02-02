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
        abort(403, description="Solo los estudiantes pueden crear proyectos.")

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
        app.logger.error(f"Error al crear el proyecto: {str(e)}")
        abort(500, description=str(e))

@project_routes_bp.route("/<int:project_id>/members", methods=["POST"])
@jwt_required()
def add_member(project_id: int):
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"message": "Solo los estudiantes pueden añadir miembros a proyectos."}), 403

    try:
        member = ProjectService(app.db).add_member(
            project_id=project_id,
            student_id=request.json.get("student_id"),
            requesting_student_id=claims.get("student_id")
        )
        return jsonify({"message": "Miembro añadido con éxito.", "id": member.id}), 201
    except ProjectValueError as e:
        abort(400, description=str(e))
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except ProjectOwnerError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except Exception as e:
        app.logger.error("Error al añadir un miembro: %s", e)
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
        return jsonify({"message": "Rol no autorizado."}), 403
    
    # Filtramos por id de actividad si se proporciona
    activity_id = request.args.get("activity_id")
    if activity_id:
        filters["activity_id"] = activity_id

    try:
        projects = ProjectService(app.db).get_projects(filters)
        return jsonify(projects), 200
    except Exception as e:
        app.logger.error(f"Error al obtener los proyectos: {str(e)}")
        abort(500, description=str(e))

@project_routes_bp.route("/<int:project_id>/members/<int:student_id>", methods=["DELETE"])
@jwt_required()
def remove_member(project_id: int, student_id: int):
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"message": "Solo los estudiantes pueden eliminar miembros del proyecto."}), 403

    try:
        ProjectService(app.db).remove_member(
            project_id=project_id,
            student_id=student_id,
            requesting_student_id=claims.get("student_id")
        )
        return jsonify({"message": "Miembro eliminado con éxito."}), 200
    except ProjectValueError as e:
        abort(401, description=str(e))
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except ProjectOwnerError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except Exception as e:
        app.logger.error("Error al eliminar miembro: %s", e)
        abort(500, description=str(e))

@project_routes_bp.route("/<int:project_id>", methods=["PATCH"])
@jwt_required()
def update_project(project_id: int):
    claims = get_jwt()
    if claims["role"] != "student":
        abort(403, description="Solo los estudiantes pueden actualizar proyectos.")

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
        app.logger.error(f"Error al actualizar el proyecto: {str(e)}")
        abort(500, description=str(e))
    else:
        return jsonify(project), 200

@project_routes_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id: int):
    claims = get_jwt()
    if claims["role"] != "student":
        abort(403, description="Solo los estudiantes pueden eliminar proyectos.")

    try:
        ProjectService(app.db).delete(project_id, claims["student_id"])
    except ProjectServiceError as e:
        abort(403, description=str(e))
    except NotFoundError as e:
        abort(404, description=str(e))
    except ProjectOwnerError as e:
        abort(403, description=str(e))
    except Exception as e:
        app.logger.error(f"Error al eliminar el proyecto: {str(e)}")
        abort(500, description=str(e))
    else:
        return "", 204

@project_routes_bp.route("/<int:project_id>/grades", methods=["POST"])
@jwt_required()
def grade(project_id):
    """Calificar un proyecto."""
    claims = get_jwt()
    if claims["role"] != "professor":
        abort(403)
    grade = request.json.get("grade")
    if grade is None:
        abort(400)
    try:
        graded = ProjectService(app.db).grade(project_id, claims["professor_id"], grade)
    except ValueError as err:
        return jsonify({"message": f"{err}"}), 422
    except Exception as err:
        app.logger.error("MySQL error. %s - %s", err.errno, err.msg)
        abort(500)
    else:
        return jsonify(graded), 200
