"""
Visits Route Blueprint
Handles visitor analytics via GET /visits.
Stores visit count in Supabase 'site_analytics' table and increments on each request.
Returns JSON { "count": current_count }.
"""

from flask import Blueprint, jsonify

try:
    from backend.services.supabase_service import increment_and_get_visits
except ImportError:
    from services.supabase_service import increment_and_get_visits  # type: ignore

visits_bp = Blueprint('visits', __name__)

@visits_bp.route('/visits', methods=['GET'])
@visits_bp.route('/api/visits', methods=['GET'])
@visits_bp.route('/api/analytics/visitor', methods=['GET', 'POST'])
@visits_bp.route('/api/analytics/visit', methods=['GET', 'POST'])
def handle_visits():
    """
    GET /visits
    Increments persistent visitor count in Supabase and returns JSON { "count": current_count }.
    """
    try:
        count = increment_and_get_visits()
        return jsonify({
            "count": count
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
