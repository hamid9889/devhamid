"""
Email Service using SendGrid API
Handles contact form email notifications to TARGET_EMAIL.
Uses environment variables:
  - SENDGRID_API_KEY: SendGrid API key
  - EMAIL_USER: Sender email address (verified sender in SendGrid)
  - TARGET_EMAIL: Destination inbox (default: 8090hamid@gmail.com)
"""

import os
from typing import Tuple

try:
    from sendgrid import SendGridAPIClient  # type: ignore
    from sendgrid.helpers.mail import Mail, Email, ReplyTo  # type: ignore
except ImportError:
    SendGridAPIClient = None  # type: ignore
    Mail = None  # type: ignore
    Email = None  # type: ignore
    ReplyTo = None  # type: ignore


def send_contact_email(name: str, sender_email: str, message_text: str) -> Tuple[bool, str]:
    """
    Sends contact email via SendGrid API to TARGET_EMAIL.
    Returns (success: bool, error_message: str).
    """
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "").strip()
    email_user = os.getenv("EMAIL_USER", "").strip()
    target_email = os.getenv("TARGET_EMAIL", "").strip() or os.getenv("RECEIVER_EMAIL", "8090hamid@gmail.com")

    # If SendGrid API key is missing or dummy/placeholder, handle accordingly
    if not sendgrid_api_key or "<" in sendgrid_api_key or "your_" in sendgrid_api_key:
        print(f"[SIMULATED EMAIL] To: {target_email} | From: {name} ({sender_email}) | Message: {message_text[:80]}...")
        return True, "Mock email dispatched (SENDGRID_API_KEY placeholder or unconfigured)"

    if not email_user:
        return False, "EMAIL_USER (sender email) not configured"

    if SendGridAPIClient is None or Mail is None:
        return False, "sendgrid package is not installed"

    try:
        subject = f"🚀 Portfolio Inquiry from {name}"
        msg = Mail(
            from_email=Email(email_user, "DevHamid Portfolio"),
            to_emails=target_email,
            subject=subject,
            plain_text_content=f"New Portfolio Inquiry:\n\nName: {name}\nEmail: {sender_email}\n\nMessage:\n{message_text}",
            html_content=f"""
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
        )
        if ReplyTo:
            msg.reply_to = ReplyTo(sender_email, name)

        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(msg)
        if 200 <= response.status_code < 300:
            return True, "Email sent successfully!"
        return False, f"SendGrid error: status code {response.status_code}"
    except Exception as e:
        print(f"[ERROR] SendGrid dispatch failed: {e}")
        return False, str(e)
