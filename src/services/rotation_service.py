"""Rotation calculation service."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List

from src.rotation import calculate_current_week, get_rotation


@dataclass
class RotationResult:
    """Result of rotation calculation."""

    week_number: int
    main_group: List[str]
    solo_person: List[str]
    unavailable: List[str]
    is_single_group: bool

    @property
    def all_members(self) -> List[str]:
        """Get all members (for single group mode)."""
        if self.is_single_group:
            return self.main_group
        return self.main_group + self.solo_person


class RotationService:
    """Service for calculating rotation schedules."""

    def __init__(self, start_date: datetime, participants: List[str]):
        """
        Initialize rotation service.

        Args:
            start_date: Start date for week 1
            participants: List of all participants
        """
        self.start_date = start_date.date() if isinstance(start_date, datetime) else start_date
        self.participants = participants

    def calculate_rotation(
        self, unavailable: List[str] = None, target_date: date = None
    ) -> RotationResult:
        """
        Calculate rotation for a given date.

        Args:
            unavailable: List of unavailable participants for this week
            target_date: Date to calculate for (defaults to today)

        Returns:
            RotationResult with rotation details
        """
        if target_date is None:
            target_date = date.today()

        # Calculate week number
        week_number = calculate_current_week(self.start_date)

        # Get rotation from core logic
        rotation = get_rotation(week_number, self.participants, unavailable)

        # Convert to structured result
        if "all" in rotation:
            # Single group mode
            return RotationResult(
                week_number=week_number,
                main_group=rotation["all"],
                solo_person=[],
                unavailable=rotation.get("unavailable", []),
                is_single_group=True,
            )
        else:
            # Two groups mode
            return RotationResult(
                week_number=week_number,
                main_group=rotation["main"],
                solo_person=rotation["solo"],
                unavailable=rotation.get("unavailable", []),
                is_single_group=False,
            )

    def get_schedule(self, weeks: int = 5) -> List[RotationResult]:
        """
        Get rotation schedule for multiple weeks.

        Args:
            weeks: Number of weeks to calculate

        Returns:
            List of RotationResult for each week
        """
        from datetime import timedelta

        schedule = []
        for week_offset in range(weeks):
            target_date = self.start_date + timedelta(weeks=week_offset)
            result = self.calculate_rotation(target_date=target_date)
            schedule.append(result)

        return schedule
