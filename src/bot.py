"""Main rotation bot with clean architecture."""

import logging
from pathlib import Path
from typing import Optional

from src.config import BotConfig
from src.services import (
    MessageService,
    NotificationService,
    RotationResult,
    RotationService,
)

logger = logging.getLogger(__name__)


class RotationBot:
    """
    Main rotation bot orchestrator.

    Uses dependency injection for all services to maintain loose coupling
    and enable easy testing and extensibility.
    """

    def __init__(
        self,
        config: BotConfig,
        rotation_service: RotationService,
        message_service: MessageService,
        notification_service: Optional[NotificationService] = None,
    ):
        """
        Initialize rotation bot.

        Args:
            config: Bot configuration
            rotation_service: Service for calculating rotations
            message_service: Service for formatting messages
            notification_service: Optional service for sending notifications
        """
        self.config = config
        self.rotation_service = rotation_service
        self.message_service = message_service
        self.notification_service = notification_service

    def generate_rotation(self) -> RotationResult:
        """
        Generate rotation for current week.

        Returns:
            RotationResult with current rotation details
        """
        return self.rotation_service.calculate_rotation(
            unavailable=self.config.rotation.unavailable_this_week
        )

    def format_message(self, rotation: RotationResult) -> str:
        """
        Format rotation into a message.

        Args:
            rotation: Rotation result to format

        Returns:
            Formatted message string
        """
        return self.message_service.format_message(rotation)

    def send_notification(self, message: str, subject: str) -> bool:
        """
        Send notification if service is configured.

        Args:
            message: Message to send
            subject: Subject/title of notification

        Returns:
            True if sent successfully (or no service configured)
        """
        if self.notification_service is None:
            logger.info("No notification service configured")
            return True

        return self.notification_service.send(message, subject)

    def run(self, send_notification: bool = True) -> str:
        """
        Run the bot: generate rotation, format message, optionally send notification.

        Args:
            send_notification: Whether to send notification

        Returns:
            Formatted message string
        """
        logger.info("Starting rotation bot")

        # Generate rotation
        rotation = self.generate_rotation()
        logger.info(f"Calculated rotation for week {rotation.week_number}")

        # Format message
        message = self.format_message(rotation)
        logger.info("Formatted message")

        # Send notification if requested
        if send_notification and self.notification_service:
            subject = f"Training Rotation - Week {rotation.week_number}"
            success = self.send_notification(message, subject)

            if success:
                logger.info("Notification sent successfully")
            else:
                logger.error("Failed to send notification")

        return message

    @classmethod
    def from_config_file(
        cls,
        config_path: Path,
        notification_service: Optional[NotificationService] = None,
    ) -> "RotationBot":
        """
        Create bot from configuration file.

        Args:
            config_path: Path to config.yaml
            notification_service: Optional notification service

        Returns:
            RotationBot instance
        """
        # Load and validate config
        config = BotConfig.from_yaml(config_path)
        config.validate()

        # Create services
        rotation_service = RotationService(
            start_date=config.rotation.start_date,
            participants=config.rotation.participants,
        )

        message_service = MessageService(
            single_group_template=config.message.single_group_template,
            split_group_template=config.message.split_group_template,
        )

        return cls(
            config=config,
            rotation_service=rotation_service,
            message_service=message_service,
            notification_service=notification_service,
        )
