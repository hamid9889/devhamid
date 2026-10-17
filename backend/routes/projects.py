"""
Projects Route Blueprint
Handles fetching repositories for Hamid (@hamid9889) via GET /projects.
Returns JSON with project name, description, stars, forks, and repo link.
"""

from flask import Blueprint, jsonify

try:
    from backend.services.github_service import get_github_projects
except ImportError:
    from services.github_service import get_github_projects  # type: ignore

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
@projects_bp.route('/api/projects', methods=['GET'])
@projects_bp.route('/api/github/repos', methods=['GET'])
def get_projects():
    """
    GET /projects
    Fetches GitHub repositories for hamid9889 and returns list of project objects.
    """
    try:
        projects = get_github_projects(username="hamid9889")
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
