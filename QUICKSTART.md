# Quick Start Guide - 2 Minutes!

Get your rotation message in 2 minutes - no complex setup!

## Step 1: Install (30 seconds)

```bash
pip install -r requirements.txt
```

That's it! No Instagram API needed.

## Step 2: Configure (1 minute)

Edit `config/config.yaml`:

```yaml
rotation:
  start_date: "2026-02-17"  # Set to your desired Monday
  participants:
    - "Your Name 1"
    - "Your Name 2"
    - "Your Name 3"
    - "Your Name 4"
    - "Your Name 5"
```

## Step 3: Generate Message (5 seconds)

```bash
python -m src.bot_simple
```

## Step 4: Copy and Paste (30 seconds)

Copy the message from the output and paste it into your Instagram group chat!

---

## That's It! 🎉

Every week:
1. Run `python -m src.bot_simple`
2. Copy the message
3. Paste into Instagram

---

## Optional: GitHub Actions Auto-Reminder

Want a weekly reminder? Push to GitHub:

```bash
git add .
git commit -m "Setup rotation bot"
git push
```

Every Monday:
- Go to **Actions** tab on GitHub
- Click latest workflow run
- Copy message from logs
- Paste into Instagram

---

## Examples

### Example 1: 4 People (Single Group)

```
📅 Week 5 - All Together!

👥 Team: Alice, Bob, Charlie, Diana

Have a great week!
```

### Example 2: 5+ People (Two Groups)

```
📅 Week 5 Rotation

🏢 Main Group: Alice, Bob, Charlie, Diana
🌟 Solo: Eve

Have a great week!
```

---

## Tips

- **Customize messages**: Edit templates in `config/config.yaml`
- **Change schedule**: Week 1 starts on your `start_date`
- **Add/remove people**: Just edit the participants list
- **Test it**: Run the command anytime to see the current week's message

---

## Troubleshooting

**"Module not found"**
```bash
pip install PyYAML
```

**Wrong week number**
- Check your `start_date` in config.yaml
- Should be a Monday in YYYY-MM-DD format

**Need help?**
- Read the full README.md
- Check that config.yaml is valid YAML syntax

---

## That's All!

No complex API setup, no authentication issues, just simple copy-paste! 📋✨
