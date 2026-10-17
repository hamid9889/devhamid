"""
DevHamid Portfolio - Production Flask Backend
Features:
  1. Contact Form API (/contact) - Dispatches emails via Flask-Mail to TARGET_EMAIL
  2. Projects API (/projects) - Real-time repository fetcher from GitHub for @hamid9889
  3. Visitor Counter API (/visits) - Cloud visitor tracking stored in Supabase
  4. AI/ML Pipelines & Health Check (/health, /api/health)
  5. Static Frontend Single-Page Serving
Production-ready for Render deployment with Gunicorn: gunicorn app:app
"""

import os
import sys
import json
import time
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from dotenv import load_dotenv

try:
    from flask_cors import CORS
except ImportError:
    CORS = lambda app, **kwargs: app

# Ensure root and backend directories are in sys.path for clean module imports
root_dir = Path(__file__).parent.parent
backend_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment configuration from backend/.env, config/.env, or root .env
env_candidates = [
    backend_dir / '.env',
    root_dir / 'config' / '.env',
    root_dir / '.env'
]
for p in env_candidates:
    if p.exists():
        load_dotenv(p)
        print(f"[INFO] Loaded environment from: {p}")
        break

# Initialize Flask Application
app = Flask(__name__, static_folder="../frontend")

# Configure Cross-Origin Resource Sharing (CORS)
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    os.getenv("FRONTEND_URL")
]
CORS(app, origins=[o for o in allowed_origins if o], supports_credentials=True)

# Initialize Flask-Mail Extension
try:
    from backend.services.email_service import init_mail
except ImportError:
    from services.email_service import init_mail  # type: ignore

init_mail(app)

# Register Blueprints for Core Endpoints
try:
    from backend.routes.contact import contact_bp
    from backend.routes.projects import projects_bp
    from backend.routes.visits import visits_bp
except ImportError:
    from routes.contact import contact_bp  # type: ignore
    from routes.projects import projects_bp  # type: ignore
    from routes.visits import visits_bp  # type: ignore

app.register_blueprint(contact_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(visits_bp)

# Health Check Endpoint
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Service health check returning server uptime and status."""
    return jsonify({
        "status": "healthy",
        "service": "DevHamid Portfolio Flask API",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }), 200

# Blog Posts Endpoint
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Serves Machine Learning & Mathematics Blog data."""
    posts_path = root_dir / 'frontend' / 'data' / 'posts.json'
    if posts_path.exists():
        with open(posts_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f)), 200
    return jsonify([]), 200

# AI/ML Pipeline Endpoints
try:
    from backend.services.face_recognition_service import face_pipeline
    from backend.services.speech_service import speech_pipeline
    from backend.services.genai_service import generate_chat_response

    @app.route('/api/ai/health', methods=['GET'])
    def ai_health():
        return jsonify({
            "status": "operational",
            "modules": {
                "face_recognition": "ready",
                "speech_recognition": "ready",
                "generative_ai": "ready"
            }
        }), 200

    @app.route('/api/ai/chat', methods=['POST'])
    def ai_chat():
        data = request.get_json(silent=True) or {}
        prompt = (data.get('prompt') or '').strip()
        user_name = (data.get('name') or 'Visitor').strip()
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        return jsonify(generate_chat_response(prompt, user_name)), 200

except Exception as e:
    print(f"[WARN] AI modules initialization note: {e}")

# Frontend Single-Page Serving
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serves static frontend files with index.html fallback for client-side routing."""
    static_dir = root_dir / 'frontend'
    if path != "" and (static_dir / path).exists():
        return send_from_directory(static_dir, path)
    return send_from_directory(static_dir, 'index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[INFO] Starting DevHamid Flask Backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
