# Email Notification Setup Guide

Get weekly rotation reminders via email! Setup takes about 5 minutes.

## Overview

- **When**: Every Monday at 9 AM UTC (6 days before Sunday training)
- **What**: Email with rotation message you can copy-paste into Instagram
- **Cost**: Free (using Gmail)

---

## Step 1: Set Up Gmail App Password

You'll use Gmail to send emails. You need an "App Password" (not your regular Gmail password).

### Create Gmail App Password

1. **Go to your Google Account**: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", enable **2-Step Verification** (if not already enabled)
4. Once 2FA is enabled, go back to **Security**
5. Under "How you sign in to Google", click **App passwords**
6. You may need to sign in again
7. In the "Select app" dropdown, choose **Mail**
8. In the "Select device" dropdown, choose **Other (Custom name)**
9. Type: "Rotation Bot"
10. Click **Generate**
11. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
12. Save this password - you'll need it in the next step!

---

## Step 2: Configure config.yaml

Edit `config/config.yaml`:

### Single Recipient

```yaml
email:
  enabled: true
  recipient: "your.email@gmail.com"  # ← Your email address
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
```

### Multiple Recipients

To send to multiple people:

```yaml
email:
  enabled: true
  recipient:  # ← Use list format for multiple emails
    - "person1@gmail.com"
    - "person2@gmail.com"
    - "person3@gmail.com"
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
```

**Replace with your actual email address(es)!**

---

## Step 3: Test Locally (Optional but Recommended)

Before setting up GitHub Actions, test it locally to make sure it works.

### Create Local Environment Variables

```bash
# Set email credentials (use your Gmail and the App Password from Step 1)
export EMAIL_SENDER="your.gmail@gmail.com"
export EMAIL_PASSWORD="abcd efgh ijkl mnop"  # The 16-char App Password

# Run the bot
python -m src.bot_simple
```

Check your email - you should receive the rotation message!

---

## Step 4: Add GitHub Secrets

Now configure GitHub Actions to send emails automatically.

### Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

**Add two secrets:**

**Secret 1:**
- Name: `EMAIL_SENDER`
- Value: `your.gmail@gmail.com` (your Gmail address)

**Secret 2:**
- Name: `EMAIL_PASSWORD`
- Value: `abcd efgh ijkl mnop` (the 16-character App Password from Step 1)

---

## Step 5: Push and Test

```bash
# Commit your config changes
git add config/config.yaml
git commit -m "Enable email notifications"
git push
```

### Test the GitHub Action

1. Go to **Actions** tab on GitHub
2. Click **Weekly Rotation Email Reminder**
3. Click **Run workflow** → **Run workflow**
4. Wait ~30 seconds
5. Check your email!

---

## How It Works

### Schedule

- **Runs**: Every Monday at 9 AM UTC
- **Why Monday**: Training is Sunday, so you get the reminder 6 days early
- **Adjust time**: Edit `.github/workflows/weekly-message.yml` to change the schedule

### What You'll Receive

**Email Subject:** `Training Rotation - Week 1`

**Email Body:**
```
📅 Week 1 Rotation

🏢 Main Group: Jack, Joe, Sean, Jin
🌟 Solo: Eldon

Have a great week!
```

Just copy from email and paste into Instagram!

---

## Troubleshooting

### "Authentication failed" error

**Problem**: Wrong email or password

**Solutions:**
1. Make sure you're using an **App Password**, not your regular Gmail password
2. Verify the App Password is correct (no spaces)
3. Check that EMAIL_SENDER matches the Gmail account that generated the App Password

### Email not received

**Check spam folder** - First-time emails from new senders often go to spam

**Mark as "Not Spam"** - This trains Gmail to deliver future emails to inbox

### "Less secure app" error

**Solution**: Use an App Password (see Step 1) - this is the modern, secure way

### Want to change recipient email?

Edit `config/config.yaml`:
```yaml
email:
  recipient: "different.email@gmail.com"
```

---

## Using Different Email Providers

### Outlook/Hotmail

```yaml
email:
  smtp_server: "smtp-mail.outlook.com"
  smtp_port: 587
```

### Yahoo Mail

```yaml
email:
  smtp_server: "smtp.mail.yahoo.com"
  smtp_port: 587
```

You'll still need an app-specific password for these providers.

---

## Disable Email Notifications

To turn off emails but keep the code:

```yaml
email:
  enabled: false
```

Or remove the GitHub Secrets to prevent sending.

---

## Security Notes

✅ **App Passwords are secure** - They're designed for this purpose
✅ **GitHub Secrets are encrypted** - Only your workflows can access them
✅ **No credentials in code** - Everything is in environment variables
⚠️ **Never commit passwords** - Always use environment variables or secrets

---

## Summary

1. ✅ Create Gmail App Password
2. ✅ Update `config.yaml` with your email
3. ✅ Test locally (optional)
4. ✅ Add GitHub Secrets
5. ✅ Push and test

Every Monday, you'll get an email with the rotation message ready to copy into Instagram! 📧

---

Need help? Check the main README.md or the GitHub Actions logs for error messages.
