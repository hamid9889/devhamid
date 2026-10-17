"""
Posts Route Blueprint
Handles fetching blog posts via GET /posts.
Queries Supabase 'blog_posts' table with fallback to local posts.json.
"""

from flask import Blueprint, jsonify

try:
    from backend.services.supabase_service import get_blog_posts
except ImportError:
    from services.supabase_service import get_blog_posts  # type: ignore

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
@posts_bp.route('/api/posts', methods=['GET'])
def list_posts():
    """GET /posts: Fetch blog posts from Supabase or local fallback."""
    try:
        posts = get_blog_posts()
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
