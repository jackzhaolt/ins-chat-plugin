# Quick Start Guide

Get your Instagram rotation bot up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Requires Python 3.8+. If you see errors, check your Python version:
```bash
python --version
```

## Step 2: Set Up Credentials

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Instagram credentials
# INSTAGRAM_USERNAME=your_username
# INSTAGRAM_PASSWORD=your_password
```

## Step 3: Find Your Thread ID

Run the helper script to list all your Instagram group chats:

```bash
python scripts/find_thread.py
```

Copy the Thread ID of your target group chat.

## Step 4: Configure the Bot

Edit `config/config.yaml`:

1. Paste your thread ID:
   ```yaml
   instagram:
     thread_id: "YOUR_THREAD_ID_HERE"
   ```

2. Set your start date (first Monday of rotation):
   ```yaml
   rotation:
     start_date: "2026-02-17"  # YYYY-MM-DD format
   ```

3. Update participants list:
   ```yaml
   participants:
     - "Alice"
     - "Bob"
     - "Charlie"
     - "Diana"
     - "Eve"
   ```

## Step 5: Test Locally

**Dry run (doesn't send message):**
```bash
export DRY_RUN=true
python -m src.bot
```

**Send test message:**
```bash
export DRY_RUN=false
python -m src.bot
```

## Step 6: Deploy to GitHub Actions

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Setup Instagram rotation bot"
   git push origin main
   ```

2. **Add GitHub Secrets:**
   - Go to: Settings → Secrets and variables → Actions
   - Add `INSTAGRAM_USERNAME`
   - Add `INSTAGRAM_PASSWORD`

3. **Test the Workflow:**
   - Go to: Actions → Weekly Instagram Rotation Bot
   - Click "Run workflow"
   - Enable "Dry run mode"
   - Check logs

4. **Run for Real:**
   - Run workflow again without dry run
   - Verify message appears in Instagram

## Done! 🎉

Your bot will now run automatically every Monday at 9 AM UTC.

## Common Issues

### 2FA Required
- Solution: Disable 2FA on your Instagram account for automation

### Thread ID Not Found
- Solution: Re-run `python scripts/find_thread.py` and update config

### Wrong Week Number
- Solution: Verify `start_date` is the Monday of your first week

## Next Steps

- Customize message templates in `config/config.yaml`
- Adjust schedule in `.github/workflows/weekly-rotation.yml`
- Read full documentation in `README.md`

## Testing

Run unit tests to verify everything works:
```bash
pytest tests/ -v
```

All 26 tests should pass! ✅
