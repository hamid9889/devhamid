const nodemailer = require('nodemailer');

let cachedTransporter = null;

/**
 * Diagnostic helper: Classifies SMTP errors with actionable guidance
 */
function diagnoseSmtpError(err) {
  const code = err.code || err.responseCode || 'UNKNOWN';
  let message = err.message || 'Unknown SMTP error occurred.';
  let remedy = 'Check server logs and environment configuration.';

  if (code === 'EAUTH' || message.includes('Username and Password not accepted') || message.includes('Invalid login')) {
    remedy = 'SMTP Authentication failed. For Gmail, you MUST generate and use a 16-character Google App Password (https://myaccount.google.com/apppasswords), NOT your personal Google account password.';
  } else if (code === 'ECONNECTION' || code === 'ETIMEDOUT' || code === 'ESOCKET') {
    remedy = 'Network connection to SMTP server timed out or was blocked by a firewall. Check your internet connection, proxy settings, or try switching between port 587 (STARTTLS) and 465 (SSL).';
  } else if (code === 'EDNS' || code === 'ENOTFOUND') {
    remedy = 'SMTP host could not be resolved via DNS. Check EMAIL_HOST (e.g. smtp.gmail.com).';
  } else if (code === 'EENVELOPE') {
    remedy = 'Invalid sender or recipient email format. Ensure EMAIL_USER and TARGET_EMAIL are valid email addresses.';
  }

  return {
    code,
    message,
    remedy
  };
}

/**
 * Initializes and verifies the email transporter.
 * If credentials are missing, falls back to Ethereal Test Account.
 */
async function getTransporter() {
  if (cachedTransporter) return cachedTransporter;

  const {
    EMAIL_SERVICE,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_SECURE,
    EMAIL_USER,
    EMAIL_PASS
  } = process.env;

  // Real SMTP credentials provided
  if (EMAIL_USER && EMAIL_PASS) {
    const config = {
      auth: {
        user: EMAIL_USER.trim(),
        pass: EMAIL_PASS.trim()
      }
    };

    if (EMAIL_SERVICE) {
      config.service = EMAIL_SERVICE;
    } else {
      config.host = EMAIL_HOST || 'smtp.gmail.com';
      config.port = parseInt(EMAIL_PORT || '587', 10);
      config.secure = EMAIL_SECURE === 'true' || EMAIL_PORT === '465';
    }

    const transporter = nodemailer.createTransport(config);

    try {
      await transporter.verify();
      console.log('✅ Nodemailer: Connected to SMTP server successfully.');
      cachedTransporter = transporter;
      return cachedTransporter;
    } catch (err) {
      const diag = diagnoseSmtpError(err);
      console.error(`❌ SMTP Connection Failed [${diag.code}]:`, diag.message);
      console.error(`💡 Diagnostic Remedy: ${diag.remedy}`);
      throw err;
    }
  }

  // Fallback: Ethereal test account for development/preview mode
  console.log('ℹ️ Nodemailer: No EMAIL_USER/PASS configured in .env. Initializing Ethereal test account...');
  try {
    const testAccount = await nodemailer.createTestAccount();
    cachedTransporter = nodemailer.createTransport({
      host: 'smtp.ethereal.email',
      port: 587,
      secure: false,
      auth: {
        user: testAccount.user,
        pass: testAccount.pass
      }
    });
    console.log(`✅ Ethereal Test Account ready: ${testAccount.user}`);
    return cachedTransporter;
  } catch (err) {
    console.warn('Failed to create Ethereal account, falling back to mock transporter:', err.message);
    return {
      sendMail: async (options) => {
        console.log('📧 [MOCK EMAIL DISPATCHED]');
        console.log('To:', options.to);
        console.log('Subject:', options.subject);
        return { messageId: 'mock-' + Date.now() };
      },
      verify: async () => true
    };
  }
}

/**
 * Verify SMTP connection status without sending an email (used by diagnostic tests)
 */
async function verifySmtpConnection() {
  const { EMAIL_USER, EMAIL_PASS } = process.env;
  if (!EMAIL_USER || !EMAIL_PASS) {
    return {
      configured: false,
      message: 'EMAIL_USER or EMAIL_PASS is not set in .env. Running in preview/test mode.'
    };
  }

  try {
    const transporter = await getTransporter();
    await transporter.verify();
    return {
      configured: true,
      status: 'connected',
      message: 'SMTP credentials verified successfully.'
    };
  } catch (err) {
    const diag = diagnoseSmtpError(err);
    return {
      configured: true,
      status: 'error',
      code: diag.code,
      message: diag.message,
      remedy: diag.remedy
    };
  }
}

/**
 * Send inquiry message to target email
 */
async function sendContactEmail({ name, email, message, timestamp }) {
  try {
    const transporter = await getTransporter();
    const targetEmail = process.env.TARGET_EMAIL || process.env.RECEIVER_EMAIL || '8090hamid@gmail.com';
    const sender = process.env.EMAIL_USER || 'no-reply@devhamid.com';

    const formattedDate = timestamp ? new Date(timestamp).toLocaleString() : new Date().toLocaleString();

    const mailOptions = {
      from: `"DevHamid Portfolio" <${sender}>`,
      to: targetEmail,
      replyTo: `"${name}" <${email}>`,
      subject: `🚀 Portfolio Message from ${name} (${email})`,
      text: `You have received a new contact message from your portfolio website!\n\nName: ${name}\nEmail: ${email}\nDate: ${formattedDate}\n\nMessage:\n${message}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f8fafc; border-radius: 12px; overflow: hidden; border: 1px solid #1e293b;">
          <div style="background: linear-gradient(135deg, #00d4ff, #8b5cf6, #ec4899); padding: 24px; text-align: center;">
            <h2 style="margin: 0; color: #ffffff; font-size: 22px; letter-spacing: -0.5px;">New Portfolio Inquiry</h2>
            <p style="margin: 4px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">from DevHamid Portfolio Website</p>
          </div>
          <div style="padding: 24px;">
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
              <tr>
                <td style="padding: 8px 0; color: #94a3b8; width: 100px; font-weight: bold;">Sender Name:</td>
                <td style="padding: 8px 0; color: #f8fafc; font-weight: bold;">${name}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #94a3b8; font-weight: bold;">Sender Email:</td>
                <td style="padding: 8px 0; color: #00d4ff;"><a href="mailto:${email}" style="color: #00d4ff; text-decoration: none;">${email}</a></td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #94a3b8; font-weight: bold;">Received:</td>
                <td style="padding: 8px 0; color: #cbd5e1;">${formattedDate}</td>
              </tr>
            </table>

            <div style="background: #1e293b; padding: 18px; border-radius: 8px; border-left: 4px solid #00d4ff; margin-bottom: 24px;">
              <p style="margin: 0 0 8px; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Message Content:</p>
              <p style="margin: 0; color: #f8fafc; line-height: 1.6; white-space: pre-wrap;">${message}</p>
            </div>

            <div style="text-align: center;">
              <a href="mailto:${email}?subject=Re:%20Portfolio%20Inquiry" style="display: inline-block; background: #00d4ff; color: #050a1a; padding: 12px 24px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                Reply to ${name} (${email})
              </a>
            </div>
          </div>
          <div style="background: #090d16; padding: 14px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #1e293b;">
            Sent to ${targetEmail} via DevHamid Portfolio Email Service
          </div>
        </div>
      `
    };

    const info = await transporter.sendMail(mailOptions);
    const previewUrl = nodemailer.getTestMessageUrl(info);

    if (previewUrl) {
      console.log(`🔗 Preview Ethereal email here: ${previewUrl}`);
    }

    return {
      status: 'success',
      success: true,
      message: 'Email sent successfully!',
      messageId: info.messageId,
      targetEmail,
      previewUrl: previewUrl || null
    };
  } catch (err) {
    const diag = diagnoseSmtpError(err);
    throw {
      status: 'error',
      success: false,
      message: diag.message,
      code: diag.code,
      remedy: diag.remedy
    };
  }
}

module.exports = {
  sendContactEmail,
  verifySmtpConnection,
  diagnoseSmtpError
};
