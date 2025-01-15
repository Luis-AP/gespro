from flask import Blueprint
from src.controllers.student_controller import StudentController

student_routes = Blueprint('student_bp', __name__, url_prefix="/api/user/students")

student_routes.route('/<int:user_id>', methods = ['GET'])(StudentController.get_student)
