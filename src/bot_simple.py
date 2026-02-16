"""Simple bot that just prints the message for manual copy-paste."""

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

from src.rotation import calculate_current_week, get_rotation
from src.email_sender import EmailSender


def main():
    """Generate and print rotation message for manual posting."""
    print("=" * 80)
    print("📱 Instagram Rotation Message Generator")
    print("=" * 80)
    print()

    # Load config
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Get rotation info
    start_date = datetime.strptime(config["rotation"]["start_date"], "%Y-%m-%d").date()
    participants = config["rotation"]["participants"]
    unavailable = config["rotation"].get("unavailable_this_week", [])

    # Calculate current week and rotation
    week_number = calculate_current_week(start_date)
    rotation = get_rotation(week_number, participants, unavailable)

    # Format message
    unavailable_note = ""
    if rotation.get("unavailable"):
        unavailable_note = f"\n\n⚠️ Unavailable this week: {', '.join(rotation['unavailable'])}"

    if "all" in rotation:
        # Single group
        template = config["message"]["single_group_template"]
        all_members = ", ".join(rotation["all"])
        message = template.format(week_number=week_number, all_members=all_members)
    else:
        # Two groups
        template = config["message"]["split_group_template"]
        main_group = ", ".join(rotation["main"])
        solo_person = rotation["solo"][0]
        message = template.format(
            week_number=week_number, main_group=main_group, solo_person=solo_person
        )

    # Add unavailable note if there are any
    message += unavailable_note

    # Print info
    print(f"📅 Today: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📆 Start date: {start_date}")
    print(f"🔢 Week number: {week_number}")
    print()
    print("👥 Participants:", ", ".join(participants))

    if rotation.get("unavailable"):
        print(f"⚠️  Unavailable this week: {', '.join(rotation['unavailable'])}")

    print()

    if "all" in rotation:
        print("📋 Rotation: Single group (< 5 people)")
        print(f"   All together: {', '.join(rotation['all'])}")
    else:
        print("📋 Rotation: Two groups (≥ 5 people)")
        print(f"   🏢 Main group: {', '.join(rotation['main'])}")
        print(f"   🌟 Solo: {rotation['solo'][0]}")

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

    # Optional: Send email if configured
    email_config = config.get("email")
    if email_config and email_config.get("enabled"):
        print()
        print("=" * 80)
        print("📧 Sending email notification...")
        print("=" * 80)

        try:
            # Get email credentials from environment variables
            sender_email = os.getenv("EMAIL_SENDER")
            sender_password = os.getenv("EMAIL_PASSWORD")
            recipient_email = email_config.get("recipient")
            smtp_server = email_config.get("smtp_server", "smtp.gmail.com")
            smtp_port = email_config.get("smtp_port", 587)

            if not sender_email or not sender_password:
                print("⚠️  Email credentials not found in environment variables")
                print("   Set EMAIL_SENDER and EMAIL_PASSWORD")
            elif not recipient_email:
                print("⚠️  Recipient email not configured in config.yaml")
            else:
                # Send email
                email_sender = EmailSender(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    sender_email=sender_email,
                    sender_password=sender_password,
                )

                subject = f"Training Rotation - Week {week_number}"
                success = email_sender.send_email(
                    recipient_email=recipient_email,
                    subject=subject,
                    message=message,
                )

                if success:
                    print(f"✅ Email sent to {recipient_email}!")
                else:
                    print("❌ Failed to send email. Check logs above.")

        except Exception as e:
            print(f"❌ Error sending email: {e}")

    print()


if __name__ == "__main__":
    main()
