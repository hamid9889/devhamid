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
  - /contact    : Contact form email dispatch via SendGrid API
  - /test-email : Simple test route for SendGrid email verification
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
backend_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables
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

# SendGrid imports
try:
    from sendgrid import SendGridAPIClient  # type: ignore
    from sendgrid.helpers.mail import Mail, Email, ReplyTo  # type: ignore
except ImportError:
    SendGridAPIClient = None  # type: ignore
    Mail = None  # type: ignore
    Email = None  # type: ignore
    ReplyTo = None  # type: ignore

# Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Supabase Client
supabase = None
try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[INFO] Supabase client initialized.")
except Exception as e:
    print(f"[WARN] Supabase initialization skipped: {e}")

# In-memory baseline counter fallback
BASELINE_VISITS = 1482
_local_store = {"count": BASELINE_VISITS}

# Root
@app.route("/")
def home():
    return "Backend running successfully!"

# Health Check
@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

# Projects (GitHub repos)
try:
    from backend.services.github_service import get_github_projects
except ImportError:
    from services.github_service import get_github_projects  # type: ignore

@app.route("/projects", methods=["GET"])
def get_projects():
    try:
        projects = get_github_projects(username="hamid9889")
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Blog Posts (Supabase)
@app.route("/posts", methods=["GET"])
def get_posts():
    if supabase:
        try:
            response = supabase.table("blog_posts").select("*").execute()
            return jsonify(response.data or []), 200
        except Exception as e:
            print(f"[WARN] Supabase blog_posts error: {e}")
    return jsonify([]), 200

# Contacts (Supabase)
@app.route("/contacts", methods=["GET"])
def get_contacts():
    if supabase:
        try:
            response = supabase.table("contacts").select("*").execute()
            return jsonify(response.data or []), 200
        except Exception as e:
            print(f"[WARN] Supabase contacts error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify([]), 200

# Visits Counter
@app.route("/visits", methods=["GET", "POST"])
def get_visits():
    return increment_visits()

@app.route("/visits/increment", methods=["POST"])
def increment_visits():
    now_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    new_count = _local_store["count"] + 1
    if supabase:
        try:
            response = supabase.table("visits").select("*").limit(1).execute()
            if response.data:
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

# Contact Form Email Dispatch via SendGrid API
@app.route("/contact", methods=["POST"])
@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not message:
        return jsonify({"status": "error", "message": "Name, email, and message are required."}), 400

    # Save to Supabase (if available)
    if supabase:
        try:
            supabase.table("contacts").insert({
                "name": name,
                "email": email,
                "message": message,
                "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }).execute()
            print(f"[INFO] Contact from {name} saved to Supabase.")
        except Exception as e:
            print(f"[WARN] Supabase contact save error: {e}")

    # Send Email via SendGrid API
    try:
        if app.config.get("TESTING"):
            return jsonify({"status": "success", "message": "Email sent successfully!"}), 200

        sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "").strip()
        sender_email = os.getenv("EMAIL_USER", "").strip()
        target_email = os.getenv("TARGET_EMAIL", "").strip() or sender_email

        if not sendgrid_api_key:
            return jsonify({"status": "error", "message": "SENDGRID_API_KEY environment variable is not configured."}), 500

        if not sender_email:
            return jsonify({"status": "error", "message": "EMAIL_USER environment variable is not configured."}), 500

        if not SendGridAPIClient or not Mail:
            return jsonify({"status": "error", "message": "sendgrid package is not installed."}), 500

        mail_msg = Mail(
            from_email=Email(sender_email, "DevHamid Portfolio"),
            to_emails=target_email,
            subject=f"🚀 Portfolio Inquiry from {name}",
            plain_text_content=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f8fafc; border-radius: 12px; overflow: hidden; border: 1px solid #1e293b;">
              <div style="background: linear-gradient(135deg, #00d4ff, #8b5cf6, #ec4899); padding: 24px; text-align: center;">
                <h2 style="margin: 0; color: #ffffff; font-size: 22px;">New Portfolio Inquiry</h2>
                <p style="margin: 4px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">from DevHamid Portfolio Website</p>
              </div>
              <div style="padding: 24px;">
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> <a href="mailto:{email}" style="color: #00d4ff;">{email}</a></p>
                <div style="background: #1e293b; padding: 18px; border-radius: 8px; border-left: 4px solid #00d4ff; margin-top: 12px;">
                  <p style="margin: 0; color: #f8fafc; white-space: pre-wrap;">{message}</p>
                </div>
              </div>
            </div>
            """
        )
        if ReplyTo:
            mail_msg.reply_to = ReplyTo(email, name)

        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(mail_msg)

        if 200 <= response.status_code < 300:
            return jsonify({"status": "success", "message": "Email sent successfully!"}), 200
        else:
            return jsonify({"status": "error", "message": f"SendGrid error: status code {response.status_code}"}), 500

    except Exception as e:
        print(f"[ERROR] SendGrid dispatch failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Test Email Route via SendGrid
@app.route("/test-email", methods=["GET", "POST"])
@app.route("/api/test-email", methods=["GET", "POST"])
def test_email():
    try:
        if app.config.get("TESTING"):
            return jsonify({"status": "success", "message": "Test email sent successfully!"}), 200

        sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "").strip()
        sender_email = os.getenv("EMAIL_USER", "").strip()
        target_email = os.getenv("TARGET_EMAIL", "").strip() or sender_email

        if not sendgrid_api_key:
            return jsonify({"status": "error", "message": "SENDGRID_API_KEY environment variable is not configured."}), 500

        if not sender_email:
            return jsonify({"status": "error", "message": "EMAIL_USER environment variable is not configured."}), 500

        if not SendGridAPIClient or not Mail:
            return jsonify({"status": "error", "message": "sendgrid package is not installed."}), 500

        mail_msg = Mail(
            from_email=Email(sender_email, "DevHamid Portfolio"),
            to_emails=target_email,
            subject="Test Email from DevHamid Portfolio Backend",
            plain_text_content="This is a test email sent via SendGrid API from DevHamid Portfolio Backend.",
            html_content="<p>This is a <strong>test email</strong> sent via <strong>SendGrid API</strong> from DevHamid Portfolio Backend.</p>"
        )

        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(mail_msg)

        if 200 <= response.status_code < 300:
            return jsonify({"status": "success", "message": "Test email sent successfully!"}), 200
        else:
            return jsonify({"status": "error", "message": f"SendGrid error: status code {response.status_code}"}), 500

    except Exception as e:
        print(f"[ERROR] SendGrid test email failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Entrypoint
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Starting DevHamid Flask Backend on port {port}...")
    app.run(host="0.0.0.0", port=port)
