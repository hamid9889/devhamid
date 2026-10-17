const express = require('express');
const router = express.Router();
const { sendContactEmail, verifySmtpConnection } = require('../services/emailService');
const { contactModel } = require('../models');

// Regex for standard RFC 5322 compliant email format validation
const EMAIL_REGEX = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;

/**
 * GET /contact/diagnostic or /api/contact/diagnostic
 * Health check & SMTP transporter diagnostic verification
 */
router.get('/diagnostic', async (req, res) => {
  try {
    const status = await verifySmtpConnection();
    return res.status(200).json(status);
  } catch (err) {
    return res.status(500).json({
      status: 'error',
      message: err.message || 'Diagnostic check failed'
    });
  }
});

/**
 * POST /contact or /api/contact
 * Handles contact form submissions, dispatches emails, and archives to Supabase
 * Returns:
 *   Success: { status: "success", message: "Email sent successfully!" }
 *   Failure: { status: "error", message: "Error details" }
 */
router.post('/', async (req, res) => {
  try {
    const { name, email, message, timestamp } = req.body || {};

    // 1. Validation: Required name and length
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
      return res.status(400).json({
        status: 'error',
        success: false,
        message: 'Name is required.'
      });
    }

    if (name.trim().length < 2) {
      return res.status(400).json({
        status: 'error',
        success: false,
        message: 'Name must be at least 2 characters.'
      });
    }

    // 2. Validation: Email format
    if (!email || typeof email !== 'string' || email.trim().length === 0) {
      return res.status(400).json({
        status: 'error',
        success: false,
        message: 'Email address is required.'
      });
    }

    if (!EMAIL_REGEX.test(email.trim())) {
      return res.status(400).json({
        status: 'error',
        success: false,
        message: 'Invalid email address format (e.g. user@example.com).'
      });
    }

    // 3. Validation: Message
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return res.status(400).json({
        status: 'error',
        success: false,
        message: 'Message is required.'
      });
    }

    if (message.trim().length < 10) {
      return res.status(400).json({
        status: 'error',
        success: false,
        message: 'Message must be at least 10 characters long.'
      });
    }

    // Sanitize input
    const cleanPayload = {
      name: name.trim().slice(0, 100),
      email: email.trim().toLowerCase().slice(0, 120),
      message: message.trim().slice(0, 3000),
      timestamp: timestamp || new Date().toISOString()
    };

    // Dispatch email via Nodemailer
    const emailResult = await sendContactEmail(cleanPayload);

    // Save message to Supabase asynchronously
    contactModel.saveMessage({
      name: cleanPayload.name,
      email: cleanPayload.email,
      message: cleanPayload.message,
      status: 'delivered'
    }).catch(err => console.warn('Supabase archive notice:', err.message));

    return res.status(200).json({
      status: 'success',
      success: true,
      message: 'Email sent successfully!',
      target: emailResult.targetEmail,
      messageId: emailResult.messageId,
      previewUrl: emailResult.previewUrl
    });
  } catch (error) {
    console.error('Contact email dispatch failed:', error);

    const errorMessage = error.message || 'Failed to send message due to an internal server error.';
    return res.status(500).json({
      status: 'error',
      success: false,
      message: errorMessage,
      code: error.code || 'SMTP_ERROR',
      remedy: error.remedy || 'Please verify your SMTP credentials in config/.env.'
    });
  }
});

module.exports = router;
