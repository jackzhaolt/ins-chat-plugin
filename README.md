# Instagram Chat Plugin Bot

Automated Instagram bot that posts weekly rotation messages to a group chat. The bot reads a list of names and groups them based on a deterministic rotation schedule, eliminating the need for manual weekly coordination.

## Features

- 📅 **Automated Weekly Messages**: Posts rotation schedules every Monday via GitHub Actions
- 🔄 **Intelligent Grouping**:
  - If < 5 participants: Everyone stays together in one group
  - If ≥ 5 participants: Splits into main group (n-1) and solo person, with weekly rotation
- ⚙️ **Configurable**: Easy YAML configuration for participants, start date, and message templates
- 🧪 **Testable**: Dry run mode for testing without sending messages
- 🔒 **Secure**: Credentials stored as GitHub Secrets

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

## Prerequisites

- Python 3.8+ (for local testing)
- Instagram account (preferably without 2FA for automation)
- GitHub account (for GitHub Actions automation)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ins-chat-plugin
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Instagram credentials:

```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
DRY_RUN=false
```

⚠️ **Security Note**: Never commit the `.env` file to version control. It's already in `.gitignore`.

## Configuration

### 1. Find Your Instagram Thread ID

Run the helper script to list all your Instagram group chats:

```bash
python scripts/find_thread.py
```

This will output all your threads with their IDs. Copy the thread ID of your target group chat.

### 2. Configure the Bot

Edit `config/config.yaml`:

```yaml
instagram:
  thread_id: "123456789012345678"  # Paste your thread ID here

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

**Configuration Notes:**
- `thread_id`: Instagram group chat thread ID (find using `find_thread.py`)
- `start_date`: First Monday of your rotation (YYYY-MM-DD format)
- `participants`: List of 1-8 names (order matters for rotation)
- Message templates support formatting variables:
  - `{week_number}`: Current week number
  - `{all_members}`: Comma-separated list of all members
  - `{main_group}`: Comma-separated list of main group members
  - `{solo_person}`: Name of solo person

## Local Testing

### Test Configuration and Rotation Logic

Run in dry run mode (doesn't send messages):

```bash
export DRY_RUN=true
python -m src.bot
```

This will:
- Load and validate configuration
- Calculate current week number
- Determine rotation
- Format message
- Display the message without sending

### Test Actual Message Sending

To test sending a real message:

```bash
export DRY_RUN=false
python -m src.bot
```

### Run Unit Tests

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## GitHub Actions Setup

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit: Instagram rotation bot"
git push origin main
```

### 2. Add GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:
   - `INSTAGRAM_USERNAME`: Your Instagram username
   - `INSTAGRAM_PASSWORD`: Your Instagram password

### 3. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, enable GitHub Actions for your repository

### 4. Test the Workflow

**Manual test run:**

1. Go to **Actions** → **Weekly Instagram Rotation Bot**
2. Click **Run workflow**
3. Select branch (usually `main`)
4. Enable **Dry run mode** for first test
5. Click **Run workflow**

Check the logs to verify:
- Configuration loads correctly
- Week number calculates correctly
- Rotation is correct
- Message formats properly

**Test actual sending:**

Run workflow again without dry run mode to send a real message.

### 5. Verify Automated Schedule

The workflow is configured to run automatically every Monday at 9:00 AM UTC (see `.github/workflows/weekly-rotation.yml`).

To adjust the schedule, edit the cron expression:

```yaml
schedule:
  - cron: '0 9 * * 1'  # minute hour day-of-month month day-of-week
```

Common schedules:
- Every Monday at 9 AM UTC: `'0 9 * * 1'`
- Every Monday at 5 PM UTC: `'0 17 * * 1'`
- Every Friday at 12 PM UTC: `'0 12 * * 5'`

**Note**: GitHub Actions uses UTC time. Convert your local timezone to UTC.

## Troubleshooting

### 2FA / Authentication Issues

**Problem**: Bot fails with "2FA required" or "Challenge required"

**Solutions**:
1. Disable 2FA on your Instagram account (for automation)
2. Complete any Instagram security challenges in the mobile app
3. Use a dedicated Instagram account without 2FA

### Session Expiration

**Problem**: Bot fails with login errors after working previously

**Solution**: Instagram sessions expire after ~90 days. The bot will automatically re-authenticate, but you may need to:
1. Complete any security challenges in Instagram app
2. Verify credentials are still correct in GitHub Secrets

### Thread ID Not Found

**Problem**: Bot fails with "Thread not found" or "not accessible"

**Solutions**:
1. Run `python scripts/find_thread.py` to get the current thread ID
2. Update `thread_id` in `config/config.yaml`
3. Ensure your Instagram account has access to the group chat

### Wrong Week Number

**Problem**: Bot shows incorrect week number

**Solution**: Verify `start_date` in `config/config.yaml`:
- Should be the Monday of your first week
- Format: `YYYY-MM-DD`
- Week 1 starts on this date

### Rate Limiting

**Problem**: Bot fails with rate limit errors

**Solution**: The bot includes automatic retry with exponential backoff. If issues persist:
1. Ensure you're only running once per week
2. Don't manually trigger the workflow multiple times in quick succession
3. Wait a few hours and try again

## Modifying Participants

To add or remove participants:

1. Edit `config/config.yaml`
2. Update the `participants` list
3. Commit and push changes

```bash
git add config/config.yaml
git commit -m "Update participants list"
git push
```

**Important Notes**:
- Changing the participant list resets the rotation
- The order of participants matters (determines rotation sequence)
- Maximum 8 participants
- Minimum 1 participant

## Project Structure

```
ins-chat-plugin/
├── .github/
│   └── workflows/
│       └── weekly-rotation.yml    # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── bot.py                     # Main orchestration
│   ├── rotation.py                # Rotation calculation logic
│   └── instagram_client.py        # Instagram API wrapper
├── config/
│   └── config.yaml                # Configuration file
├── scripts/
│   └── find_thread.py             # Helper to find thread IDs
├── tests/
│   ├── __init__.py
│   ├── test_rotation.py           # Unit tests
│   └── test_bot.py                # Bot tests
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment variable template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Exit Codes

The bot uses the following exit codes:

- `0`: Success
- `1`: Configuration error
- `2`: Authentication error
- `3`: Message sending error
- `99`: Unknown error

These help with debugging failed GitHub Actions runs.

## Security Considerations

- ✅ Credentials stored as GitHub Secrets (encrypted)
- ✅ `.env` file excluded from version control
- ✅ Session files excluded from version control
- ⚠️ Consider using a dedicated Instagram account for automation
- ⚠️ Instagram may restrict automated access if detected

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_rotation.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Structure

- **src/rotation.py**: Pure Python logic for rotation calculation (no external dependencies)
- **src/instagram_client.py**: Instagram API wrapper with error handling and retry logic
- **src/bot.py**: Main orchestration that ties everything together
- **scripts/find_thread.py**: Utility script for finding thread IDs

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review GitHub Actions logs for error messages
3. Run locally with `DRY_RUN=true` to debug
4. Open an issue with logs and error messages

## Acknowledgments

Built with:
- [instagrapi](https://github.com/subzeroid/instagrapi) - Instagram Private API wrapper
- [PyYAML](https://pyyaml.org/) - YAML parser
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management
