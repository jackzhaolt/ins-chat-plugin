"""Instagram client wrapper for authentication and messaging."""

import logging
import time
from pathlib import Path
from typing import Optional

try:
    from instagrapi import Client
    from instagrapi.exceptions import (
        BadPassword,
        ChallengeRequired,
        ClientError,
        LoginRequired,
        PleaseWaitFewMinutes,
        RateLimitError,
        TwoFactorRequired,
    )
except ImportError:
    # Allow import in environments where instagrapi is not installed
    # (e.g., for testing on Python 3.7)
    Client = None
    BadPassword = Exception
    ChallengeRequired = Exception
    ClientError = Exception
    LoginRequired = Exception
    PleaseWaitFewMinutes = Exception
    RateLimitError = Exception
    TwoFactorRequired = Exception

logger = logging.getLogger(__name__)


class InstagramClient:
    """Wrapper around instagrapi for Instagram authentication and messaging."""

    def __init__(self, username: str, password: str, session_file: Optional[str] = None):
        """
        Initialize Instagram client.

        Args:
            username: Instagram username
            password: Instagram password
            session_file: Optional path to session file for persistence
        """
        if Client is None:
            raise ImportError("instagrapi is required but not installed")

        self.username = username
        self.password = password
        self.session_file = Path(session_file) if session_file else None
        self.client = Client()

        # Configure client settings
        self.client.delay_range = [1, 3]  # Delay between requests

    def login(self) -> bool:
        """
        Login to Instagram with error handling.

        Tries to load saved session first, then falls back to username/password login.

        Returns:
            True if login successful, False otherwise

        Raises:
            TwoFactorRequired: If 2FA is required (cannot be handled automatically)
            ChallengeRequired: If Instagram challenge is required
            BadPassword: If credentials are invalid
        """
        logger.info(f"Attempting to login as {self.username}")

        # Try loading saved session first
        if self.session_file and self.session_file.exists():
            try:
                logger.info(f"Loading session from {self.session_file}")
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)

                # Verify session is valid
                self.client.get_timeline_feed()
                logger.info("Successfully loaded session from file")
                return True

            except Exception as e:
                logger.warning(f"Failed to load session: {e}")
                logger.info("Attempting fresh login")

        # Fresh login
        try:
            self.client.login(self.username, self.password)

            # Save session for future use
            if self.session_file:
                self.client.dump_settings(self.session_file)
                logger.info(f"Session saved to {self.session_file}")

            logger.info("Successfully logged in")
            return True

        except TwoFactorRequired:
            logger.error("2FA is required for this account")
            logger.error("Please disable 2FA or provide 2FA code handling")
            raise

        except ChallengeRequired as e:
            logger.error(f"Instagram challenge required: {e}")
            logger.error("Please complete the challenge in the Instagram app")
            raise

        except BadPassword:
            logger.error("Invalid username or password")
            raise

        except LoginRequired:
            logger.error("Login required but credentials may be invalid")
            raise

        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise

    def send_message_to_thread(
        self, thread_id: str, message: str, max_retries: int = 3
    ) -> bool:
        """
        Send a message to an Instagram group chat thread.

        Implements exponential backoff retry for rate limits.

        Args:
            thread_id: Instagram thread ID (e.g., "123456789012345678")
            message: Message text to send
            max_retries: Maximum number of retry attempts

        Returns:
            True if message sent successfully, False otherwise

        Raises:
            ValueError: If thread_id or message is empty
            ClientError: If message sending fails after all retries
        """
        if not thread_id or not thread_id.strip():
            raise ValueError("thread_id cannot be empty")

        if not message or not message.strip():
            raise ValueError("message cannot be empty")

        logger.info(f"Sending message to thread {thread_id}")
        logger.debug(f"Message preview: {message[:100]}...")

        for attempt in range(max_retries):
            try:
                # Send message
                self.client.direct_send(message, thread_ids=[thread_id])
                logger.info(f"Message sent successfully to thread {thread_id}")
                return True

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Rate limited, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Rate limited after {max_retries} attempts: {e}")
                    raise

            except PleaseWaitFewMinutes as e:
                logger.error(f"Instagram is asking to wait: {e}")
                raise

            except ClientError as e:
                # Check if it's a thread not found error
                if "thread" in str(e).lower() or "not found" in str(e).lower():
                    logger.error(f"Thread {thread_id} not found or not accessible")
                    raise ValueError(f"Invalid thread_id: {thread_id}")

                logger.error(f"Client error sending message: {e}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error sending message: {e}")
                raise

        return False

    def get_thread_info(self, thread_id: str) -> dict:
        """
        Get information about a thread.

        Args:
            thread_id: Instagram thread ID

        Returns:
            Dictionary with thread information

        Raises:
            ValueError: If thread not found
        """
        try:
            thread = self.client.direct_thread(thread_id)
            return {
                "thread_id": thread.id,
                "title": thread.thread_title,
                "users": [u.username for u in thread.users],
            }
        except Exception as e:
            logger.error(f"Error getting thread info: {e}")
            raise ValueError(f"Thread {thread_id} not found or not accessible")

    def list_threads(self, limit: int = 20) -> list:
        """
        List direct message threads.

        Args:
            limit: Maximum number of threads to return

        Returns:
            List of thread dictionaries with id, title, and participants
        """
        try:
            threads = self.client.direct_threads(amount=limit)
            return [
                {
                    "thread_id": thread.id,
                    "title": thread.thread_title or "No title",
                    "participants": [u.username for u in thread.users],
                }
                for thread in threads
            ]
        except Exception as e:
            logger.error(f"Error listing threads: {e}")
            raise
