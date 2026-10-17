"""
Contact Route Blueprint
Handles contact form submissions via POST /contact.
Sends notifications via Flask-Mail to TARGET_EMAIL.
Returns JSON {status: "success"} or {status: "error"}.
"""

import re
from flask import Blueprint, request, jsonify

try:
    from backend.services.email_service import send_contact_email
    from backend.services.supabase_service import save_contact, get_contacts
except ImportError:
    from services.email_service import send_contact_email  # type: ignore
    from services.supabase_service import save_contact, get_contacts  # type: ignore

contact_bp = Blueprint('contact', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

@contact_bp.route('/contacts', methods=['GET'])
@contact_bp.route('/api/contacts', methods=['GET'])
def list_contacts():
    """GET /contacts: Retrieve stored contacts from Supabase."""
    try:
        contacts = get_contacts()
        return jsonify(contacts), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@contact_bp.route('/contact', methods=['POST'])
@contact_bp.route('/contacts', methods=['POST'])
@contact_bp.route('/api/contact', methods=['POST'])
def handle_contact():
    """
    POST /contact
    Body: { "name": "...", "email": "...", "message": "..." }
    Returns:
      Success: { "status": "success", "message": "Email sent successfully!" }
      Error:   { "status": "error", "message": "..." }
    """
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()

    # Input validation
    if not name or len(name) < 2:
        return jsonify({
            "status": "error",
            "message": "Name must be at least 2 characters long."
        }), 400

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({
            "status": "error",
            "message": "Please provide a valid email address."
        }), 400

    if not message or len(message) < 5:
        return jsonify({
            "status": "error",
            "message": "Message must be at least 5 characters long."
        }), 400

    # Persist contact to Supabase
    save_contact(name, email, message)

    # Dispatch email via Flask-Mail service
    success, msg = send_contact_email(name, email, message)

    if success:
        return jsonify({
            "status": "success",
            "message": "Email sent and recorded successfully!"
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": msg or "Failed to dispatch email."
        }), 500
