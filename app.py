"""
DevHamid Portfolio - Full Flask Backend
Features:
  - /           : Root confirmation status
  - /health     : Service health check
  - /projects   : GitHub repos for @hamid9889
  - /posts      : Blog posts from Supabase (with fallback)
  - /contacts   : Contact entries from Supabase
  - /visits     : Visitor counter with Supabase
  - /visits/increment : Visitor counter increment
  - /contact    : Contact form email dispatch (Flask-Mail + Gmail App Password)
"""

import os
import sys
import time
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure backend and root paths are in sys.path
root_dir = Path(__file__).parent.parent
backend_dir = Path(__file__).parent / "backend" if (Path(__file__).parent / "backend").exists() else Path(__file__).parent
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables (.env in backend or config)
env_candidates = [
    backend_dir / '.env',
    Path(__file__).parent / '.env',
    Path(__file__).parent / 'config' / '.env'
]
for p in env_candidates:
    if p.exists():
        load_dotenv(p)
        print(f"[INFO] Loaded environment from: {p}")
        break

# Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Supabase Client
supabase = None
try:
    from supabase import create_client  # type: ignore
    SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip().strip('"\'')
    SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip().strip('"\'')
    if SUPABASE_URL and SUPABASE_KEY and "your-supabase" not in SUPABASE_URL:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[INFO] Supabase client initialized.")
except Exception as e:
    print(f"[WARN] Supabase initialization skipped: {e}")

# Flask-Mail Config (Gmail SMTP + App Password)
app.config['MAIL_SERVER'] = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('EMAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('EMAIL_SECURE', 'false').lower() != 'true'
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")

mail = None
try:
    from flask_mail import Mail, Message  # type: ignore
    mail = Mail(app)
    print("[INFO] Flask-Mail initialized.")
except Exception as e:
    print(f"[WARN] Flask-Mail initialization skipped: {e}")

# In-memory baseline counter fallback
BASELINE_VISITS = 1482
_local_store = {"count": BASELINE_VISITS}

# Root
@app.route("/")
def home():
    return "Backend running successfully!"

# Health Check
@app.route("/health")
@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "DevHamid Portfolio Flask Backend",
        "message": "Backend running successfully!"
    }), 200

# Projects (GitHub repos)
try:
    from backend.services.github_service import get_github_projects
except ImportError:
    from services.github_service import get_github_projects  # type: ignore

@app.route("/projects", methods=["GET"])
@app.route("/api/projects", methods=["GET"])
@app.route("/api/github/repos", methods=["GET"])
def get_projects():
    try:
        projects = get_github_projects(username="hamid9889")
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Blog Posts (Supabase)
@app.route("/posts", methods=["GET"])
@app.route("/api/posts", methods=["GET"])
def get_posts():
    if supabase:
        try:
            response = supabase.table("blog_posts").select("*").execute()
            if response.data:
                return jsonify(response.data), 200
        except Exception as e:
            print(f"[WARN] Supabase blog_posts error: {e}")

    # Fallback to local posts.json
    try:
        from backend.services.supabase_service import get_blog_posts
        return jsonify(get_blog_posts()), 200
    except Exception:
        return jsonify([]), 200

# Contacts (Supabase)
@app.route("/contacts", methods=["GET"])
@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    if supabase:
        try:
            response = supabase.table("contacts").select("*").execute()
            return jsonify(response.data or []), 200
        except Exception as e:
            print(f"[WARN] Supabase contacts error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify([]), 200

# Visits Counter (Supabase)
@app.route("/visits", methods=["GET", "POST"])
@app.route("/api/visits", methods=["GET", "POST"])
def get_visits():
    return increment_visits()

@app.route("/visits/increment", methods=["POST"])
@app.route("/api/visits/increment", methods=["POST"])
def increment_visits():
    now_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    new_count = _local_store["count"] + 1

    if supabase:
        try:
            response = supabase.table("visits").select("*").order("id", desc=False).limit(1).execute()
            if response.data and len(response.data) > 0:
                current = response.data[0]
                new_count = current.get("count", BASELINE_VISITS) + 1
                supabase.table("visits").update({
                    "count": new_count,
                    "last_updated": now_iso
                }).eq("id", current["id"]).execute()
            else:
                supabase.table("visits").insert({
                    "id": 1,
                    "count": BASELINE_VISITS + 1,
                    "last_updated": now_iso
                }).execute()
                new_count = BASELINE_VISITS + 1
        except Exception as e:
            print(f"[WARN] Supabase visits increment error: {e}")

    _local_store["count"] = new_count
    return jsonify({"count": new_count}), 200

# Contact Form Email (Flask-Mail + Supabase backup)
@app.route("/contact", methods=["POST"])
@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"status": "error", "message": "Name, email, and message are required."}), 400

    # Save to Supabase contacts table
    if supabase:
        try:
            supabase.table("contacts").insert({
                "name": name,
                "email": email,
                "message": message,
                "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }).execute()
        except Exception as e:
            print(f"[WARN] Supabase contact save error: {e}")

    # Dispatch email via Flask-Mail
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    target_email = os.getenv("TARGET_EMAIL") or email_user

    # If placeholder or SMTP credentials not configured, return safe simulated success
    if not email_user or not email_pass or "<" in str(email_pass):
        print(f"[SIMULATED EMAIL] To: {target_email} | From: {name} ({email}) | Message: {message[:80]}...")
        return jsonify({"status": "success", "message": "Email recorded successfully!"}), 200

    if mail:
        try:
            msg = Message(
                subject=f"🚀 Portfolio Inquiry from {name}",
                sender=email_user,
                recipients=[target_email],
                reply_to=email,
                body=f"New Portfolio Inquiry:\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            return jsonify({"status": "success", "message": "Email sent successfully!"}), 200
        except Exception as e:
            print(f"[ERROR] Flask-Mail dispatch failed: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "Message saved successfully!"}), 200

# Entrypoint for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Starting DevHamid Flask Backend on port {port}...")
    app.run(host="0.0.0.0", port=port)
