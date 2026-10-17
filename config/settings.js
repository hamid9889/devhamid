/**
 * Central Configuration & Settings
 * Loads and validates environment parameters for the DevHamid Portfolio Backend.
 */

const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// Check config/.env first, then root .env
const envPaths = [
  path.join(__dirname, '.env'),
  path.join(__dirname, '..', '.env'),
  path.join(__dirname, '..', 'backend', '.env')
];

for (const p of envPaths) {
  if (fs.existsSync(p)) {
    dotenv.config({ path: p });
    break;
  }
}
dotenv.config();

const settings = {
  // Server
  port: parseInt(process.env.PORT || '5000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  isProduction: process.env.NODE_ENV === 'production',

  // Email
  targetEmail: process.env.TARGET_EMAIL || process.env.RECEIVER_EMAIL || '8090hamid@gmail.com',
  emailUser: process.env.EMAIL_USER || '',
  emailPass: process.env.EMAIL_PASS || '',
  smtpHost: process.env.EMAIL_HOST || 'smtp.gmail.com',
  smtpPort: parseInt(process.env.EMAIL_PORT || '587', 10),
  smtpSecure: process.env.EMAIL_SECURE === 'true',

  // GitHub
  githubUsername: process.env.GITHUB_USERNAME || 'hamid9889',
  githubToken: process.env.GITHUB_TOKEN || '',

  // Supabase
  supabaseUrl: process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  supabaseKey: process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_KEY || process.env.SUPABASE_ANON_KEY || '',

  // Frontend
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:5000',
  allowedOrigins: [
    'http://localhost:3000',
    'http://localhost:5000',
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8080',
    process.env.FRONTEND_URL
  ].filter(Boolean)
};

module.exports = settings;
