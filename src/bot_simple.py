"""Simple CLI interface for rotation bot."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed")
    print("Install it with: pip install PyYAML")
    sys.exit(1)

from src.bot import RotationBot
from src.config import BotConfig
from src.services import NotificationServiceFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


def print_rotation_info(bot: RotationBot, message: str) -> None:
    """Print rotation information in a user-friendly format."""
    rotation = bot.generate_rotation()
    config = bot.config

    print("=" * 80)
    print("📱 Instagram Rotation Message Generator")
    print("=" * 80)
    print()
    print(f"📅 Today: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📆 Start date: {config.rotation.start_date.strftime('%Y-%m-%d')}")
    print(f"🔢 Week number: {rotation.week_number}")
    print()
    print("👥 Participants:", ", ".join(config.rotation.participants))

    if rotation.unavailable:
        print(f"⚠️  Unavailable this week: {', '.join(rotation.unavailable)}")

    print()

    if rotation.is_single_group:
        print("📋 Rotation: Single group (< 5 people)")
        print(f"   All together: {', '.join(rotation.main_group)}")
    else:
        print("📋 Rotation: Two groups (≥ 5 people)")
        print(f"   🏢 Main group: {', '.join(rotation.main_group)}")
        print(f"   🌟 Solo: {rotation.solo_person[0]}")

    print()
    print("=" * 80)
    print("📋 MESSAGE TO COPY (between the lines below)")
    print("=" * 80)
    print()
    print(message)
    print()
    print("=" * 80)
    print("✅ Copy the message above and paste it into your Instagram group chat!")
    print("=" * 80)


def main():
    """Main entry point for simple CLI bot."""
    # Get project root and config path
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config" / "config.yaml"

    try:
        # Load config
        config = BotConfig.from_yaml(config_path)
        config.validate()

        # Create notification service if email is enabled
        notification_service = None
        if config.email.enabled:
            # Get credentials from environment
            sender_email = os.getenv("EMAIL_SENDER")
            sender_password = os.getenv("EMAIL_PASSWORD")

            if sender_email and sender_password:
                notification_service = NotificationServiceFactory.create_email_service(
                    smtp_server=config.email.smtp_server,
                    smtp_port=config.email.smtp_port,
                    sender_email=sender_email,
                    sender_password=sender_password,
                    recipient_email=config.email.recipient,
                )
                logger.info("Email notifications enabled")
            else:
                logger.warning(
                    "Email enabled but credentials not found in environment variables"
                )
                logger.warning("Set EMAIL_SENDER and EMAIL_PASSWORD to enable email")

        # Create bot
        bot = RotationBot.from_config_file(
            config_path=config_path,
            notification_service=notification_service,
        )

        # Run bot
        message = bot.run(send_notification=notification_service is not None)

        # Print results
        print_rotation_info(bot, message)

        # Print email status
        if config.email.enabled and notification_service:
            print()
            print("=" * 80)
            print("📧 Email Notifications")
            print("=" * 80)
            recipients_str = ", ".join(config.email.recipient)
            print(f"✅ Email sent to {len(config.email.recipient)} recipient(s):")
            for recipient in config.email.recipient:
                print(f"   • {recipient}")
            print("=" * 80)
        elif config.email.enabled:
            print()
            print("=" * 80)
            print("⚠️  Email notifications enabled but credentials not provided")
            print("Set EMAIL_SENDER and EMAIL_PASSWORD environment variables")
            print("=" * 80)

        print()

    except FileNotFoundError as e:
        logger.error(f"❌ Configuration file not found: {e}")
        sys.exit(1)

    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.exception("Full traceback:")
        sys.exit(99)


if __name__ == "__main__":
    main()
