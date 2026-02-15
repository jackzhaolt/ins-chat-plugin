#!/usr/bin/env python
"""
Helper script to find Instagram group chat thread IDs.

This script lists all your Instagram direct message threads with their IDs
so you can identify the correct thread_id to use in config.yaml.

Usage:
    python scripts/find_thread.py

Requirements:
    - Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables
    - Or create a .env file with these variables
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    from src.instagram_client import InstagramClient
except ImportError as e:
    print(f"Error: Required dependencies not installed: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Main function to list Instagram threads."""
    # Load environment variables from .env file
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}\n")

    # Get credentials from environment
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if not username or not password:
        print("Error: Instagram credentials not found!")
        print("\nPlease set the following environment variables:")
        print("  INSTAGRAM_USERNAME=your_username")
        print("  INSTAGRAM_PASSWORD=your_password")
        print("\nOr create a .env file with these variables.")
        sys.exit(1)

    print(f"Logging in as: {username}")
    print("-" * 80)

    try:
        # Initialize client and login
        client = InstagramClient(username, password)
        client.login()

        print("\n✓ Successfully logged in!")
        print("-" * 80)

        # List threads
        print("\nFetching your direct message threads...\n")
        threads = client.list_threads(limit=20)

        if not threads:
            print("No threads found.")
            return

        print(f"Found {len(threads)} threads:\n")
        print("=" * 80)

        for i, thread in enumerate(threads, 1):
            print(f"\n{i}. {thread['title']}")
            print(f"   Thread ID: {thread['thread_id']}")
            print(f"   Participants: {', '.join(thread['participants'])}")
            print("-" * 80)

        print("\n✓ Done!")
        print("\nCopy the Thread ID of your group chat and paste it into config/config.yaml")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
