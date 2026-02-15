"""Main bot orchestration script for Instagram Chat Plugin Bot."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    import yaml
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Required dependencies not installed: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(99)

from src.instagram_client import InstagramClient
from src.rotation import (
    calculate_current_week,
    get_rotation,
    validate_participants,
)

# Exit codes
EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 1
EXIT_AUTH_ERROR = 2
EXIT_MESSAGE_ERROR = 3
EXIT_UNKNOWN_ERROR = 99

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> Dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        ValueError: If config validation fails
    """
    logger.info(f"Loading configuration from {config_path}")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Validate configuration
    validate_config(config)

    logger.info("Configuration loaded and validated successfully")
    return config


def validate_config(config: Dict) -> None:
    """
    Validate configuration structure and values.

    Args:
        config: Configuration dictionary

    Raises:
        ValueError: If validation fails
    """
    # Check required top-level keys
    required_keys = ["instagram", "rotation", "message"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration section: {key}")

    # Validate instagram section
    if "thread_id" not in config["instagram"]:
        raise ValueError("Missing required field: instagram.thread_id")

    thread_id = config["instagram"]["thread_id"]
    if not thread_id or not str(thread_id).strip():
        raise ValueError("instagram.thread_id cannot be empty")

    # Validate rotation section
    if "start_date" not in config["rotation"]:
        raise ValueError("Missing required field: rotation.start_date")

    if "participants" not in config["rotation"]:
        raise ValueError("Missing required field: rotation.participants")

    # Validate start_date format
    try:
        datetime.strptime(config["rotation"]["start_date"], "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            "rotation.start_date must be in YYYY-MM-DD format "
            f"(got: {config['rotation']['start_date']})"
        )

    # Validate participants
    participants = config["rotation"]["participants"]
    if not isinstance(participants, list):
        raise ValueError("rotation.participants must be a list")

    validate_participants(participants)

    # Validate message templates
    if "single_group_template" not in config["message"]:
        raise ValueError("Missing required field: message.single_group_template")

    if "split_group_template" not in config["message"]:
        raise ValueError("Missing required field: message.split_group_template")


def format_message(
    week_number: int, rotation: Dict[str, List[str]], templates: Dict[str, str]
) -> str:
    """
    Format message based on rotation type.

    Args:
        week_number: Current week number
        rotation: Rotation dictionary from get_rotation()
        templates: Message templates from config

    Returns:
        Formatted message string
    """
    if "all" in rotation:
        # Single group (< 5 participants)
        template = templates["single_group_template"]
        all_members = ", ".join(rotation["all"])

        message = template.format(week_number=week_number, all_members=all_members)

    else:
        # Two groups (>= 5 participants)
        template = templates["split_group_template"]
        main_group = ", ".join(rotation["main"])
        solo_person = rotation["solo"][0]

        message = template.format(
            week_number=week_number, main_group=main_group, solo_person=solo_person
        )

    return message


def get_credentials() -> tuple:
    """
    Get Instagram credentials from environment variables.

    Returns:
        Tuple of (username, password)

    Raises:
        ValueError: If credentials are missing
    """
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if not username:
        raise ValueError("INSTAGRAM_USERNAME environment variable not set")

    if not password:
        raise ValueError("INSTAGRAM_PASSWORD environment variable not set")

    return username, password


def main() -> int:
    """
    Main bot execution function.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    logger.info("=" * 80)
    logger.info("Instagram Chat Plugin Bot - Starting")
    logger.info("=" * 80)

    try:
        # Load environment variables
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded environment variables from {env_file}")

        # Check for dry run mode
        dry_run = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No message will be sent")

        # Load configuration
        config_path = project_root / "config" / "config.yaml"
        config = load_config(config_path)

        # Get credentials
        username, password = get_credentials()
        logger.info(f"Using Instagram account: {username}")

        # Parse start date
        start_date = datetime.strptime(
            config["rotation"]["start_date"], "%Y-%m-%d"
        ).date()
        logger.info(f"Rotation start date: {start_date}")

        # Calculate current week
        week_number = calculate_current_week(start_date)
        logger.info(f"Current week number: {week_number}")

        # Get participants and calculate rotation
        participants = config["rotation"]["participants"]
        logger.info(f"Participants ({len(participants)}): {', '.join(participants)}")

        rotation = get_rotation(week_number, participants)
        logger.info(f"Rotation type: {'Single group' if 'all' in rotation else 'Two groups'}")

        # Format message
        message = format_message(week_number, rotation, config["message"])
        logger.info("\nMessage to send:")
        logger.info("-" * 80)
        logger.info(message)
        logger.info("-" * 80)

        # Send message (or skip if dry run)
        if dry_run:
            logger.info("\n✓ DRY RUN: Message formatted successfully (not sent)")
            logger.info("=" * 80)
            return EXIT_SUCCESS

        # Initialize Instagram client
        logger.info("\nConnecting to Instagram...")
        thread_id = str(config["instagram"]["thread_id"])

        # Use session file for persistence (helps avoid 2FA prompts)
        session_file = project_root / "session.json"
        client = InstagramClient(username, password, str(session_file))

        # Login
        logger.info("Logging in...")
        client.login()

        # Send message
        logger.info(f"Sending message to thread {thread_id}...")
        success = client.send_message_to_thread(thread_id, message)

        if success:
            logger.info("✓ Message sent successfully!")
            logger.info("=" * 80)
            return EXIT_SUCCESS
        else:
            logger.error("✗ Failed to send message")
            logger.info("=" * 80)
            return EXIT_MESSAGE_ERROR

    except FileNotFoundError as e:
        logger.error(f"✗ Configuration error: {e}")
        logger.info("=" * 80)
        return EXIT_CONFIG_ERROR

    except ValueError as e:
        logger.error(f"✗ Configuration or validation error: {e}")
        logger.info("=" * 80)
        return EXIT_CONFIG_ERROR

    except (
        Exception
    ) as e:  # This will catch Instagram-related exceptions from instagram_client
        error_msg = str(e).lower()

        # Check for authentication errors
        if any(
            keyword in error_msg
            for keyword in ["2fa", "two factor", "challenge", "password", "login"]
        ):
            logger.error(f"✗ Authentication error: {e}")
            logger.error("\nTroubleshooting:")
            logger.error("  1. Verify your Instagram credentials are correct")
            logger.error("  2. If 2FA is enabled, consider disabling it for automation")
            logger.error("  3. Complete any Instagram challenges in the mobile app")
            logger.info("=" * 80)
            return EXIT_AUTH_ERROR

        # Check for message sending errors
        elif "thread" in error_msg or "message" in error_msg:
            logger.error(f"✗ Message sending error: {e}")
            logger.error("\nTroubleshooting:")
            logger.error("  1. Verify the thread_id in config.yaml is correct")
            logger.error("  2. Run 'python scripts/find_thread.py' to find thread IDs")
            logger.error("  3. Ensure you have access to the thread")
            logger.info("=" * 80)
            return EXIT_MESSAGE_ERROR

        # Unknown error
        else:
            logger.error(f"✗ Unexpected error: {e}")
            logger.exception("Full traceback:")
            logger.info("=" * 80)
            return EXIT_UNKNOWN_ERROR


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
