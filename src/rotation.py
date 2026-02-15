"""Rotation calculation logic for Instagram chat bot."""

from datetime import date
from typing import Dict, List


def calculate_current_week(start_date: date) -> int:
    """
    Calculate week number since start date.

    Args:
        start_date: The starting date for week 1

    Returns:
        Week number (1-indexed). Returns 1 if current date is before start_date.

    Examples:
        >>> from datetime import date
        >>> calculate_current_week(date(2026, 2, 17))  # If today is 2026-02-17
        1
        >>> calculate_current_week(date(2026, 2, 17))  # If today is 2026-02-24
        2
    """
    today = date.today()

    # If current date is before start date, default to week 1
    if today < start_date:
        return 1

    days_since = (today - start_date).days
    week_number = (days_since // 7) + 1

    return week_number


def get_rotation(week_number: int, participants: List[str]) -> Dict[str, List[str]]:
    """
    Calculate rotation for given week based on participant count.

    Rules:
    - If len(participants) < 5: All participants in one group
    - If len(participants) >= 5: Split into main group (n-1) and solo (1)
      - Solo person rotates: week 1 → last person, week 2 → first person, etc.

    Args:
        week_number: Current week number (1-indexed)
        participants: List of participant names (max 8)

    Returns:
        Dictionary with rotation:
        - For < 5 participants: {"all": [all participants]}
        - For >= 5 participants: {"main": [n-1 people], "solo": [1 person]}

    Raises:
        ValueError: If participants list is empty or has more than 8 participants

    Examples:
        >>> get_rotation(1, ["Alice", "Bob", "Charlie"])
        {'all': ['Alice', 'Bob', 'Charlie']}

        >>> get_rotation(1, ["Alice", "Bob", "Charlie", "Diana", "Eve"])
        {'main': ['Alice', 'Bob', 'Charlie', 'Diana'], 'solo': ['Eve']}

        >>> get_rotation(2, ["Alice", "Bob", "Charlie", "Diana", "Eve"])
        {'main': ['Bob', 'Charlie', 'Diana', 'Eve'], 'solo': ['Alice']}
    """
    n = len(participants)

    # Validation
    if n == 0:
        raise ValueError("Participants list cannot be empty")
    if n > 8:
        raise ValueError(f"Maximum 8 participants allowed, got {n}")

    # Less than 5: everyone in one group
    if n < 5:
        return {"all": participants.copy()}

    # 5 or more: rotate who is solo
    # Week 1 → index 0 solo, Week 2 → index 1 solo, etc.
    solo_index = (week_number - 1) % n
    solo_person = participants[solo_index]

    # Main group is everyone except the solo person
    main_group = [p for i, p in enumerate(participants) if i != solo_index]

    return {"main": main_group, "solo": [solo_person]}


def validate_participants(participants: List[str]) -> None:
    """
    Validate participants list.

    Args:
        participants: List of participant names

    Raises:
        ValueError: If validation fails
    """
    if not participants:
        raise ValueError("Participants list cannot be empty")

    if len(participants) > 8:
        raise ValueError(f"Maximum 8 participants allowed, got {len(participants)}")

    # Check for duplicates
    if len(participants) != len(set(participants)):
        raise ValueError("Participants list contains duplicates")

    # Check for empty names
    if any(not p.strip() for p in participants):
        raise ValueError("Participants list contains empty names")
