"""Configuration management for rotation bot."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class EmailConfig:
    """Email notification configuration."""

    enabled: bool
    recipient: List[str]  # Can be single email or list of emails
    smtp_server: str
    smtp_port: int

    def __post_init__(self):
        """Normalize recipient to always be a list."""
        if isinstance(self.recipient, str):
            self.recipient = [self.recipient]


@dataclass
class RotationConfig:
    """Rotation settings configuration."""

    start_date: datetime
    participants: List[str]
    unavailable_this_week: List[str]


@dataclass
class MessageConfig:
    """Message template configuration."""

    single_group_template: str
    split_group_template: str


@dataclass
class BotConfig:
    """Complete bot configuration."""

    email: EmailConfig
    rotation: RotationConfig
    message: MessageConfig

    @classmethod
    def from_yaml(cls, config_path: Path) -> "BotConfig":
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config.yaml file

        Returns:
            BotConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        # Validate and parse email config
        email_data = data.get("email", {})
        email_config = EmailConfig(
            enabled=email_data.get("enabled", False),
            recipient=email_data.get("recipient", ""),
            smtp_server=email_data.get("smtp_server", "smtp.gmail.com"),
            smtp_port=email_data.get("smtp_port", 587),
        )

        # Validate and parse rotation config
        rotation_data = data.get("rotation", {})
        if not rotation_data:
            raise ValueError("Missing 'rotation' section in config")

        start_date_str = rotation_data.get("start_date")
        if not start_date_str:
            raise ValueError("Missing 'rotation.start_date' in config")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format for start_date: {e}")

        participants = rotation_data.get("participants", [])
        if not participants:
            raise ValueError("Missing or empty 'rotation.participants' in config")

        if len(participants) > 8:
            raise ValueError(f"Maximum 8 participants allowed, got {len(participants)}")

        rotation_config = RotationConfig(
            start_date=start_date,
            participants=participants,
            unavailable_this_week=rotation_data.get("unavailable_this_week", []),
        )

        # Validate and parse message config
        message_data = data.get("message", {})
        if not message_data:
            raise ValueError("Missing 'message' section in config")

        message_config = MessageConfig(
            single_group_template=message_data.get("single_group_template", ""),
            split_group_template=message_data.get("split_group_template", ""),
        )

        if not message_config.single_group_template:
            raise ValueError("Missing 'message.single_group_template' in config")

        if not message_config.split_group_template:
            raise ValueError("Missing 'message.split_group_template' in config")

        return cls(
            email=email_config,
            rotation=rotation_config,
            message=message_config,
        )

    def validate(self) -> None:
        """
        Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate participants
        if not self.rotation.participants:
            raise ValueError("Participants list cannot be empty")

        if len(self.rotation.participants) != len(set(self.rotation.participants)):
            raise ValueError("Participants list contains duplicates")

        # Validate unavailable participants are in the list
        for person in self.rotation.unavailable_this_week:
            if person not in self.rotation.participants:
                raise ValueError(
                    f"Unavailable person '{person}' not in participants list"
                )

        # Validate email config if enabled
        if self.email.enabled:
            if not self.email.recipient:
                raise ValueError("Email recipient is required when email is enabled")

            # Validate each recipient email
            for recipient in self.email.recipient:
                if "@" not in recipient:
                    raise ValueError(f"Invalid email address: {recipient}")
