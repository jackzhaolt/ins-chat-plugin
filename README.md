# Instagram Rotation Bot (Simple Copy-Paste Version)

Automated rotation message generator that calculates weekly team groupings. Run the script, copy the output, and paste it into your Instagram group chat - no API setup required!

## Features

- 📅 **Automated Calculation**: Determines current week and rotation automatically
- 🔄 **Intelligent Grouping**:
  - If < 5 participants: Everyone stays together in one group
  - If ≥ 5 participants: Splits into main group (n-1) and solo person with weekly rotation
- 📋 **Copy-Paste Ready**: Generates formatted messages ready to paste into Instagram
- ⚙️ **Easy Configuration**: Simple YAML file for participants and settings
- 🤖 **GitHub Actions**: Optional weekly reminder (message appears in logs)
- ✅ **No Authentication**: No Instagram API, no login issues, no blocking

## How It Works

### Rotation Logic

**For groups with < 5 participants:**
- All participants stay in one group every week
- No rotation needed

**For groups with ≥ 5 participants:**
- Splits into two groups: main group (n-1 people) and solo person
- Solo position rotates through all participants:
  - Week 1: Person 1 solo, others in main group
  - Week 2: Person 2 solo, others in main group
  - Week 3: Person 3 solo, others in main group
  - And so on...

### Example

With 5 participants: `[Alice, Bob, Charlie, Diana, Eve]`

- **Week 1**: Main: [Bob, Charlie, Diana, Eve], Solo: [Alice]
- **Week 2**: Main: [Alice, Charlie, Diana, Eve], Solo: [Bob]
- **Week 3**: Main: [Alice, Bob, Diana, Eve], Solo: [Charlie]
- **Week 4**: Main: [Alice, Bob, Charlie, Eve], Solo: [Diana]
- **Week 5**: Main: [Alice, Bob, Charlie, Diana], Solo: [Eve]
- **Week 6**: Repeats Week 1 pattern

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Rotation

Edit `config/config.yaml`:

```yaml
rotation:
  start_date: "2026-02-17"  # Monday of week 1 (YYYY-MM-DD)
  participants:
    - "Alice"
    - "Bob"
    - "Charlie"
    - "Diana"
    - "Eve"
    # Add up to 8 participants

message:
  single_group_template: |
    📅 Week {week_number} - All Together!

    👥 Team: {all_members}

    Have a great week!

  split_group_template: |
    📅 Week {week_number} Rotation

    🏢 Main Group: {main_group}
    🌟 Solo: {solo_person}

    Have a great week!
```

### 3. Generate Your Message

```bash
python -m src.bot_simple
```

**Output:**
```
================================================================================
📱 Instagram Rotation Message Generator
================================================================================

📅 Today: 2026-02-15
📆 Start date: 2026-02-17
🔢 Week number: 1

👥 Participants: Alice, Bob, Charlie, Diana, Eve

📋 Rotation: Two groups (≥ 5 people)
   🏢 Main group: Bob, Charlie, Diana, Eve
   🌟 Solo: Alice

================================================================================
📋 MESSAGE TO COPY (between the lines below)
================================================================================

📅 Week 1 Rotation

🏢 Main Group: Bob, Charlie, Diana, Eve
🌟 Solo: Alice

Have a great week!

================================================================================
✅ Copy the message above and paste it into your Instagram group chat!
================================================================================
```

### 4. Copy and Paste

Copy the message between the lines and paste it into your Instagram group chat!

## Configuration

### Start Date

The `start_date` should be the **Monday of your first week** in `YYYY-MM-DD` format.

```yaml
rotation:
  start_date: "2026-02-17"  # Week 1 begins this Monday
```

The bot will automatically calculate the current week number based on this date.

### Participants

Add 1-8 participant names:

```yaml
rotation:
  participants:
    - "Name 1"
    - "Name 2"
    - "Name 3"
```

**Important Notes:**
- Order matters! Rotation cycles through this list in order
- Maximum 8 participants
- Names can be anything (real names, nicknames, @handles)

### Message Templates

Customize the message format:

```yaml
message:
  # Used when < 5 participants
  single_group_template: |
    Your message here
    Use {week_number} and {all_members}

  # Used when >= 5 participants
  split_group_template: |
    Your message here
    Use {week_number}, {main_group}, and {solo_person}
```

**Available variables:**
- `{week_number}` - Current week number
- `{all_members}` - Comma-separated list of all members (single group only)
- `{main_group}` - Comma-separated list of main group (split group only)
- `{solo_person}` - Name of solo person (split group only)

## GitHub Actions (Optional)

Get automatic weekly reminders via GitHub Actions!

### Setup

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Setup rotation bot"
   git push origin main
   ```

2. **Enable GitHub Actions:**
   - Go to your repository on GitHub
   - Click the **Actions** tab
   - Enable workflows if prompted

### How It Works

- **Automatic**: Runs every Monday at 9 AM UTC
- **Message in logs**: The rotation message appears in the workflow logs
- **Manual run**: You can trigger it anytime from the Actions tab

### To Use the Message

1. Go to **Actions** tab in your GitHub repository
2. Click on the latest **"Weekly Rotation Message Generator"** run
3. Expand the **"Generate rotation message"** step
4. Copy the message from the logs
5. Paste into your Instagram group chat

### Adjust Schedule

Edit `.github/workflows/weekly-message.yml` to change the time:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
```

Common schedules:
- Every Monday at 5 PM UTC: `'0 17 * * 1'`
- Every Friday at 12 PM UTC: `'0 12 * * 5'`
- Every Sunday at 8 PM UTC: `'0 20 * * 0'`

**Note**: GitHub Actions uses UTC timezone.

## Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

All 26 tests should pass! ✅

### Test With Different Dates

You can temporarily change the start date in `config/config.yaml` to test different week calculations.

## Updating Participants

To add or remove participants:

1. Edit `config/config.yaml`
2. Update the `participants` list
3. Run `python -m src.bot_simple` to verify

```bash
git add config/config.yaml
git commit -m "Update participants"
git push
```

**Important**: Changing the participant order or count resets the rotation cycle.

## Project Structure

```
ins-chat-plugin/
├── .github/
│   └── workflows/
│       └── weekly-message.yml     # GitHub Actions workflow (optional)
├── src/
│   ├── __init__.py
│   ├── rotation.py                # Core rotation calculation logic
│   └── bot_simple.py              # Message generator
├── config/
│   └── config.yaml                # Configuration file
├── tests/
│   ├── __init__.py
│   └── test_rotation.py           # Unit tests
├── .gitignore
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── QUICKSTART.md                  # Quick start guide
```

## Troubleshooting

### Wrong Week Number

**Problem**: Bot shows incorrect week number

**Solution**: Verify `start_date` in `config/config.yaml`:
- Should be the Monday of your first week
- Format: `YYYY-MM-DD`
- Week 1 starts on this date

### Rotation Seems Wrong

**Problem**: Wrong person is solo or groups look incorrect

**Solutions**:
1. Check the participant order in `config/config.yaml`
2. Verify you haven't changed the list recently (changes reset the cycle)
3. Run the bot to see the current rotation calculation

### GitHub Actions Not Running

**Problem**: Workflow doesn't run on schedule

**Solutions**:
1. Verify GitHub Actions is enabled in your repository
2. Check the workflow file syntax
3. GitHub Actions can be delayed by up to 10-15 minutes
4. Try running manually first to test

## Why This Approach?

**Simple**: No API keys, no authentication, no complex setup

**Reliable**: Can't get blocked by Instagram, no rate limits

**Transparent**: You see exactly what will be posted before posting it

**Flexible**: Easy to customize messages and manually adjust if needed

**Portable**: Works locally, on GitHub Actions, or anywhere Python runs

## FAQ

**Q: Can I automate posting to Instagram?**
A: Instagram's API has restrictions and authentication issues. Manual copy-paste is simpler and more reliable.

**Q: Can I use this for other messaging platforms?**
A: Yes! Copy-paste works everywhere - Slack, Discord, Telegram, WhatsApp, etc.

**Q: What if I need to skip a week?**
A: Just don't post that week. The bot will calculate the correct week when you run it again.

**Q: Can I have different groups each week?**
A: The rotation is deterministic based on the week number. For custom groupings, edit the message manually.

**Q: How do I change the rotation order?**
A: Reorder the participants in `config/config.yaml`. Note: This resets the rotation cycle.

## Support

If you encounter issues:
1. Check that `config/config.yaml` is properly formatted
2. Verify your start date is correct
3. Run tests with `pytest tests/ -v`
4. Check GitHub Actions logs if using automation
