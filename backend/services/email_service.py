"""
Email Service using Flask-Mail
Handles contact form email notifications to TARGET_EMAIL.
Uses environment variables:
  - EMAIL_USER: Sender email address (e.g., Gmail)
  - EMAIL_PASS: SMTP password or App Password
  - TARGET_EMAIL: Destination inbox (default: 8090hamid@gmail.com)
"""

import os
from typing import Tuple, Dict, Any

try:
    from flask_mail import Mail, Message  # type: ignore
except ImportError:
    Mail = None
    Message = None

# Global Mail instance
mail = Mail() if Mail is not None else None

def init_mail(app):
    """Initialize Flask-Mail extension with app configuration."""
    app.config['MAIL_SERVER'] = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('EMAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('EMAIL_SECURE', 'false').lower() != 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('EMAIL_SECURE', 'false').lower() == 'true' or int(os.getenv('EMAIL_PORT', 587)) == 465
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
    app.config['MAIL_DEFAULT_SENDER'] = (
        f"DevHamid Portfolio <{os.getenv('EMAIL_USER')}>"
        if os.getenv('EMAIL_USER')
        else "DevHamid Portfolio <noreply@devhamid.com>"
    )

    if mail is not None:
        mail.init_app(app)
        print("[INFO] Flask-Mail initialized.")
    return mail

def send_contact_email(name: str, sender_email: str, message_text: str) -> Tuple[bool, str]:
    """
    Sends contact email via Flask-Mail to TARGET_EMAIL.
    Returns (success: bool, error_message: str).
    """
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    target_email = os.getenv('TARGET_EMAIL') or os.getenv('RECEIVER_EMAIL', '8090hamid@gmail.com')

    # If SMTP credentials are not configured or contain template placeholders, log a simulated dispatch
    if not email_user or not email_pass or "<" in email_pass or "your-" in email_pass:
        print(f"[SIMULATED EMAIL] To: {target_email} | From: {name} ({sender_email}) | Message: {message_text[:80]}...")
        return True, "Mock email dispatched (EMAIL_USER / EMAIL_PASS not configured in .env)"

    if Message is None:
        return False, "Flask-Mail library not available"

    try:
        subject = f"🚀 Portfolio Inquiry from {name}"
        msg = Message(
            subject=subject,
            sender=(f"DevHamid Portfolio", email_user),
            recipients=[target_email],
            reply_to=sender_email
        )

        msg.body = f"New Portfolio Inquiry:\n\nName: {name}\nEmail: {sender_email}\n\nMessage:\n{message_text}"
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f8fafc; border-radius: 12px; overflow: hidden; border: 1px solid #1e293b;">
          <div style="background: linear-gradient(135deg, #00d4ff, #8b5cf6, #ec4899); padding: 24px; text-align: center;">
            <h2 style="margin: 0; color: #ffffff; font-size: 22px;">New Portfolio Inquiry</h2>
            <p style="margin: 4px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">from DevHamid Portfolio Website</p>
          </div>
          <div style="padding: 24px;">
            <p><strong>Sender:</strong> {name} ({sender_email})</p>
            <div style="background: #1e293b; padding: 18px; border-radius: 8px; border-left: 4px solid #00d4ff;">
              <p style="margin: 0; color: #f8fafc; white-space: pre-wrap;">{message_text}</p>
            </div>
          </div>
        </div>
        """

        mail.send(msg)
        return True, "Email sent successfully!"
    except Exception as e:
        print(f"[ERROR] Flask-Mail dispatch failed: {e}")
        return False, str(e)
