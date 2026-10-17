"""
DevHamid Portfolio - Production Flask Backend Entrypoint
Features:
  - Route /         : Returns "Backend running successfully!"
  - Route /contact  : Contact Form API with Flask-Mail dispatch
  - Route /projects : Real-time GitHub repositories for @hamid9889
  - Route /visits   : Persistent visitor counter with Supabase
  - Route /health   : Service health check
Render Deployment:
  - Build command: pip install -r requirements.txt
  - Start command: gunicorn app:app
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Ensure backend and root paths are in sys.path
root_dir = Path(__file__).parent.parent
backend_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables (.env in backend or config)
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

# Initialize Flask Application Entrypoint
app = Flask(__name__)

# Configure Cross-Origin Resource Sharing (CORS)
try:
    from flask_cors import CORS
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        os.getenv("FRONTEND_URL")
    ]
    CORS(app, origins=[o for o in allowed_origins if o], supports_credentials=True)
except ImportError:
    pass

# Initialize Flask-Mail Extension
try:
    from backend.services.email_service import init_mail
except ImportError:
    from services.email_service import init_mail  # type: ignore

init_mail(app)

# Register Modular Blueprints
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

# Default Root Route
@app.route('/')
def home():
    """Default entry route confirming backend deployment status."""
    return "Backend running successfully!"

# Health Check Route
@app.route('/health')
@app.route('/api/health')
def health():
    """Service health check returning JSON status."""
    return jsonify({
        "status": "healthy",
        "service": "DevHamid Portfolio Flask Backend",
        "message": "Backend running successfully!"
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[INFO] Starting DevHamid Flask Backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Starting DevHamid Flask Backend on port {port}...")
    app.run(host="0.0.0.0", port=port)
