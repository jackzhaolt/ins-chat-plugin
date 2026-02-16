"""Email sender for rotation messages."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class EmailSender:
    """Simple email sender using SMTP."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
    ):
        """
        Initialize email sender.

        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (usually 587 for TLS)
            sender_email: Email address to send from
            sender_password: Email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        message: str,
    ) -> bool:
        """
        Send an email.

        Args:
            recipient_email: Email address to send to
            subject: Email subject line
            message: Email message body (plain text)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject

            # Add message body
            msg.attach(MIMEText(message, "plain"))

            # Connect to server and send
            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure connection
                logger.info("Logging in to email account...")
                server.login(self.sender_email, self.sender_password)
                logger.info(f"Sending email to {recipient_email}...")
                server.send_message(msg)

            logger.info("✓ Email sent successfully!")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("✗ Email authentication failed!")
            logger.error("  Make sure you're using an App Password for Gmail")
            logger.error("  See: https://support.google.com/accounts/answer/185833")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"✗ SMTP error: {e}")
            return False

        except Exception as e:
            logger.error(f"✗ Unexpected error sending email: {e}")
            return False
