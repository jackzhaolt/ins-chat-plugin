"""Message formatting service."""

from abc import ABC, abstractmethod

from src.services.rotation_service import RotationResult


class MessageFormatter(ABC):
    """Abstract base class for message formatters."""

    @abstractmethod
    def format(self, rotation: RotationResult) -> str:
        """Format rotation result into a message."""
        pass


class SingleGroupFormatter:
    """Formatter for single group messages."""

    def __init__(self, template: str):
        """
        Initialize formatter.

        Args:
            template: Message template with {week_number} and {all_members} placeholders
        """
        self.template = template

    def format(self, rotation: RotationResult) -> str:
        """Format single group message."""
        all_members = ", ".join(rotation.main_group)
        message = self.template.format(
            week_number=rotation.week_number,
            all_members=all_members,
        )

        # Add unavailable note if needed
        if rotation.unavailable:
            message += f"\n\n⚠️ Unavailable this week: {', '.join(rotation.unavailable)}"

        return message


class SplitGroupFormatter:
    """Formatter for split group messages."""

    def __init__(self, template: str):
        """
        Initialize formatter.

        Args:
            template: Message template with placeholders
        """
        self.template = template

    def format(self, rotation: RotationResult) -> str:
        """Format split group message."""
        main_group = ", ".join(rotation.main_group)
        solo_person = rotation.solo_person[0] if rotation.solo_person else ""

        message = self.template.format(
            week_number=rotation.week_number,
            main_group=main_group,
            solo_person=solo_person,
        )

        # Add unavailable note if needed
        if rotation.unavailable:
            message += f"\n\n⚠️ Unavailable this week: {', '.join(rotation.unavailable)}"

        return message


class MessageService:
    """Service for formatting rotation messages."""

    def __init__(self, single_group_template: str, split_group_template: str):
        """
        Initialize message service.

        Args:
            single_group_template: Template for single group messages
            split_group_template: Template for split group messages
        """
        self.single_group_formatter = SingleGroupFormatter(single_group_template)
        self.split_group_formatter = SplitGroupFormatter(split_group_template)

    def format_message(self, rotation: RotationResult) -> str:
        """
        Format rotation result into a message.

        Automatically selects the appropriate formatter based on rotation type.

        Args:
            rotation: Rotation result to format

        Returns:
            Formatted message string
        """
        if rotation.is_single_group:
            return self.single_group_formatter.format(rotation)
        else:
            return self.split_group_formatter.format(rotation)
