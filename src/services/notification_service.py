"""Notification service abstraction."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from src.email_sender import EmailSender

logger = logging.getLogger(__name__)


class NotificationService(ABC):
    """Abstract notification service."""

    @abstractmethod
    def send(self, message: str, subject: Optional[str] = None) -> bool:
        """
        Send a notification.

        Args:
            message: Message content
            subject: Optional subject/title

        Returns:
            True if sent successfully
        """
        pass


class EmailNotificationService(NotificationService):
    """Email-based notification service."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_email: list,
    ):
        """
        Initialize email notification service.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            sender_email: Sender email address
            sender_password: Sender email password
            recipient_email: Recipient email address(es) - string or list
        """
        # Normalize to list
        if isinstance(recipient_email, str):
            recipient_email = [recipient_email]
        self.recipient_email = recipient_email
        self.email_sender = EmailSender(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender_email=sender_email,
            sender_password=sender_password,
        )

    def send(self, message: str, subject: Optional[str] = None) -> bool:
        """Send email notification."""
        if subject is None:
            subject = "Rotation Reminder"

        recipients_str = ", ".join(self.recipient_email)
        logger.info(f"Sending email notification to {len(self.recipient_email)} recipient(s): {recipients_str}")
        return self.email_sender.send_email(
            recipient_email=self.recipient_email,
            subject=subject,
            message=message,
        )


class ConsoleNotificationService(NotificationService):
    """Console-based notification service (for testing/local use)."""

    def send(self, message: str, subject: Optional[str] = None) -> bool:
        """Print notification to console."""
        logger.info("=" * 80)
        if subject:
            logger.info(f"Subject: {subject}")
        logger.info("=" * 80)
        logger.info(message)
        logger.info("=" * 80)
        return True


class NotificationServiceFactory:
    """Factory for creating notification services."""

    @staticmethod
    def create_email_service(
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_email: str,
    ) -> EmailNotificationService:
        """Create email notification service."""
        return EmailNotificationService(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_email=recipient_email,
        )

    @staticmethod
    def create_console_service() -> ConsoleNotificationService:
        """Create console notification service."""
        return ConsoleNotificationService()
