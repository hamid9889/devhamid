"""
DevHamid Portfolio - Python Flask Backend
Production-Ready API providing:
- POST /api/contact               (Email dispatch via smtplib & Supabase message logging)
- GET  /api/github/repos          (GitHub API proxy with caching)
- GET/POST /api/analytics/visitor (Visitor counter backed by Supabase Cloud Database)
- GET  /api/posts                 (Modular Machine Learning Blog posts)
- GET  /api/health                (Service health check)
- AI/ML & Generative AI Endpoints:
  - GET  /api/ai/health           (AI modules diagnostic status)
  - POST /api/ai/chat             (Generative AI Portfolio Assistant)
  - POST /api/ai/face-verify      (Face Recognition CV pipeline)
  - POST /api/ai/speech-transcribe(SpeechRecognition & PyDub audio pipeline)
"""

import os
import sys
import re
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# Ensure root and backend paths are in sys.path
root_dir = Path(__file__).parent.parent
backend_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Supabase database service & AI/ML Pipeline services
try:
    from backend.services.supabase_client import (
        get_visitor_count,
        record_visit,
        save_contact_message,
        is_supabase_connected
    )
    from backend.services.face_recognition_service import face_pipeline
    from backend.services.speech_service import speech_pipeline
    from backend.services.genai_service import generate_chat_response
except ImportError:
    from services.supabase_client import (  # type: ignore
        get_visitor_count,
        record_visit,
        save_contact_message,
        is_supabase_connected
    )
    from services.face_recognition_service import face_pipeline  # type: ignore
    from services.speech_service import speech_pipeline  # type: ignore
    from services.genai_service import generate_chat_response  # type: ignore

# Load environment configuration
env_candidates = [
    Path(__file__).parent.parent / 'config' / '.env',
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent / '.env'
]
for p in env_candidates:
    if p.exists():
        load_dotenv(p)
        print(f"Loaded environment from: {p}")
        break

app = Flask(__name__, static_folder="../frontend")
CORS(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# In-memory GitHub cache
github_cache = {
    'repos': None,
    'timestamp': 0
}
CACHE_TTL = 900  # 15 minutes

def send_smtp_email(name: str, email: str, message: str) -> bool:
    """Send portfolio message via SMTP (e.g. Gmail App Password)."""
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    receiver = os.getenv('TARGET_EMAIL') or os.getenv('RECEIVER_EMAIL', '8090hamid@gmail.com')
    smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('EMAIL_PORT', 587))
    use_ssl = os.getenv('EMAIL_SECURE', 'false').lower() == 'true' or smtp_port == 465

    if email_user and email_pass:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚀 Portfolio Inquiry from {name}"
        msg['From'] = f"DevHamid Portfolio <{email_user}>"
        msg['To'] = receiver
        msg['Reply-To'] = email

        text_content = f"New Portfolio Inquiry:\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f8fafc; border-radius: 12px; overflow: hidden; border: 1px solid #1e293b;">
          <div style="background: linear-gradient(135deg, #00d4ff, #8b5cf6, #ec4899); padding: 24px; text-align: center;">
            <h2 style="margin: 0; color: #ffffff; font-size: 22px;">New Portfolio Inquiry</h2>
            <p style="margin: 4px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">from DevHamid Portfolio Website</p>
          </div>
          <div style="padding: 24px;">
            <p><strong>Sender:</strong> {name} ({email})</p>
            <div style="background: #1e293b; padding: 18px; border-radius: 8px; border-left: 4px solid #00d4ff;">
              <p style="margin: 0; color: #f8fafc; white-space: pre-wrap;">{message}</p>
            </div>
          </div>
        </div>
        """
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        if use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12) as server:
                server.login(email_user, email_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
                server.starttls()
                server.login(email_user, email_pass)
                server.send_message(msg)
        return True
    else:
        print(f"[MOCK EMAIL - FLASK] To: {receiver} | From: {name} ({email}) | Body: {message}")
        return True

@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'DevHamid Portfolio Flask API',
        'database': 'Supabase Cloud PostgreSQL' if is_supabase_connected() else 'In-Memory Cache (Supabase not configured)',
        'ai_modules': {
            'face_recognition': 'active',
            'speech_recognition': 'active',
            'generative_ai': 'active'
        },
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    })

@app.route('/api/contact', methods=['POST'])
@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()

    if not name or len(name) < 2:
        return jsonify({'status': 'error', 'success': False, 'message': 'Name must be at least 2 characters.'}), 400

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({'status': 'error', 'success': False, 'message': 'Please provide a valid email address.'}), 400

    if not message or len(message) < 10:
        return jsonify({'status': 'error', 'success': False, 'message': 'Message must be at least 10 characters.'}), 400

    try:
        send_smtp_email(name, email, message)
        # Log to Supabase
        save_contact_message(name, email, message)

        return jsonify({
            'status': 'success',
            'success': True,
            'message': 'Email sent successfully!'
        })
    except Exception as e:
        print(f"SMTP error in Flask app: {e}")
        return jsonify({
            'status': 'error',
            'success': False,
            'message': f'SMTP Error: {str(e)}'
        }), 500

@app.route('/api/github/repos', methods=['GET'])
def get_repos():
    username = os.getenv('GITHUB_USERNAME', 'hamid9889')
    now = time.time()

    if github_cache['repos'] and (now - github_cache['timestamp']) < CACHE_TTL:
        return jsonify(github_cache['repos'])

    headers = {'User-Agent': 'DevHamid-Portfolio-Flask'}
    token = os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f"Bearer {token}"

    try:
        url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=30"
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            repos = [r for r in res.json() if r.get('name') != username]
            github_cache['repos'] = repos
            github_cache['timestamp'] = now
            return jsonify(repos)
        elif github_cache['repos']:
            return jsonify(github_cache['repos'])
        else:
            return jsonify({'error': 'GitHub API error', 'status': res.status_code}), res.status_code
    except Exception as e:
        if github_cache['repos']:
            return jsonify(github_cache['repos'])
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/visitor', methods=['GET', 'POST'])
@app.route('/api/analytics/visit', methods=['GET', 'POST'])
def visitor():
    if request.method == 'POST':
        data = request.get_json() or {}
        visitor_id = data.get('visitorId')
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
        user_agent = request.headers.get('User-Agent', '')

        result = record_visit(visitor_id, ip_address, user_agent)
        return jsonify({
            'success': True,
            'count': result['count'],
            'isNewVisit': result['isNewVisit']
        })
    else:
        return jsonify({'count': get_visitor_count()})

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts_path = Path(__file__).parent.parent / 'frontend' / 'data' / 'posts.json'
    if posts_path.exists():
        with open(posts_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

# AI / ML & Generative AI Endpoints
@app.route('/api/ai/health', methods=['GET'])
def ai_health():
    return jsonify({
        'status': 'healthy',
        'face_recognition': 'ready (face_recognition + dlib + opencv-python-headless)',
        'speech_recognition': 'ready (SpeechRecognition + pydub)',
        'generative_ai': 'ready (Portfolio Assistant Engine)',
        'database': 'Supabase PostgreSQL'
    })

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.get_json() or {}
    prompt = (data.get('prompt') or '').strip()
    user_name = (data.get('name') or 'Visitor').strip()

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    response = generate_chat_response(prompt, user_name)
    return jsonify(response)

@app.route('/api/ai/face-verify', methods=['POST'])
def ai_face_verify():
    data = request.get_json() or {}
    image_base64 = data.get('imageBase64')
    target_name = data.get('targetName')
    tolerance = float(data.get('tolerance', 0.6))

    if not image_base64:
        return jsonify({'error': 'imageBase64 is required'}), 400

    res = face_pipeline.verify_face(image_base64, target_name, tolerance)
    return jsonify(res)

@app.route('/api/ai/speech-transcribe', methods=['POST'])
def ai_speech_transcribe():
    data = request.get_json() or {}
    audio_base64 = data.get('audioBase64')
    audio_format = data.get('format', 'wav')
    language = data.get('language', 'en-US')

    if not audio_base64:
        return jsonify({'error': 'audioBase64 is required'}), 400

    res = speech_pipeline.transcribe_audio(audio_base64, audio_format, language)
    return jsonify(res)

# Serve frontend statically
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    static_dir = Path(__file__).parent.parent / 'frontend'
    if path != "" and (static_dir / path).exists():
        return send_from_directory(static_dir, path)
    return send_from_directory(static_dir, 'index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[INFO] Starting DevHamid Flask Backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
