# Configuration Guide - DevHamid Portfolio

This directory manages environment variables and runtime settings for the DevHamid portfolio.

## Files

- `.env.example`: Template showing all required and optional environment keys.
- `.env`: Active local environment file (automatically ignored by git for security).

---

## 🔑 How to Set Up Email for Contact Form

The contact form sends inquiries directly to `8090hamid@gmail.com`.

### Setting Up Gmail App Password:
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Enable **2-Step Verification** if not already enabled.
3. In the search bar at the top of Google Account, search for **"App Passwords"** (or visit [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
4. Enter an app name like `DevHamid Portfolio` and click **Create**.
5. Copy the generated **16-character password** (e.g., `abcd efgh ijkl mnop`).
6. In `config/.env`, set:
   ```env
   EMAIL_USER=8090hamid@gmail.com
   EMAIL_PASS=abcdefghijklmnop
   ```

> **Note:** If `EMAIL_PASS` is empty during local testing, the backend will automatically use an **Ethereal test account** or log the email to the console without crashing.

---

## 🌐 Deploying Environment Variables to Render

When deploying the backend on [Render.com](https://render.com):
1. In your Render Dashboard, go to your Web Service.
2. Click **Environment**.
3. Add the following variables:
   - `PORT`: `10000`
   - `NODE_ENV`: `production`
   - `GITHUB_USERNAME`: `hamid9889`
   - `RECEIVER_EMAIL`: `8090hamid@gmail.com`
   - `EMAIL_SERVICE`: `gmail`
   - `EMAIL_USER`: `8090hamid@gmail.com`
   - `EMAIL_PASS`: `<your-16-char-app-password>`
   - `FRONTEND_URL`: `https://your-portfolio.vercel.app`
