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


def get_rotation(
    week_number: int, participants: List[str], unavailable: List[str] = None
) -> Dict[str, List[str]]:
    """
    Calculate rotation for given week based on participant count.

    Rules:
    - If len(participants) < 5: All participants in one group
    - If len(participants) >= 5: Split into main group (n-1) and solo (1)
      - Solo person rotates: week 1 → last person, week 2 → first person, etc.
    - Unavailable participants are excluded from the rotation for this week

    Args:
        week_number: Current week number (1-indexed)
        participants: List of participant names (max 8)
        unavailable: Optional list of participants unavailable this week

    Returns:
        Dictionary with rotation:
        - For < 5 participants: {"all": [all participants], "unavailable": [...]}
        - For >= 5 participants: {"main": [n-1 people], "solo": [1 person], "unavailable": [...]}

    Raises:
        ValueError: If participants list is empty or has more than 8 participants

    Examples:
        >>> get_rotation(1, ["Alice", "Bob", "Charlie"])
        {'all': ['Alice', 'Bob', 'Charlie'], 'unavailable': []}

        >>> get_rotation(1, ["Alice", "Bob", "Charlie"], ["Bob"])
        {'all': ['Alice', 'Charlie'], 'unavailable': ['Bob']}

        >>> get_rotation(1, ["Alice", "Bob", "Charlie", "Diana", "Eve"])
        {'main': ['Alice', 'Bob', 'Charlie', 'Diana'], 'solo': ['Eve'], 'unavailable': []}

        >>> get_rotation(2, ["Alice", "Bob", "Charlie", "Diana", "Eve"])
        {'main': ['Bob', 'Charlie', 'Diana', 'Eve'], 'solo': ['Alice'], 'unavailable': []}
    """
    n = len(participants)

    # Validation
    if n == 0:
        raise ValueError("Participants list cannot be empty")
    if n > 8:
        raise ValueError(f"Maximum 8 participants allowed, got {n}")

    # Handle unavailable participants
    if unavailable is None:
        unavailable = []

    # Filter out unavailable participants for this week
    available_participants = [p for p in participants if p not in unavailable]

    # Track who's unavailable
    unavailable_list = [p for p in participants if p in unavailable]

    # If no one is available, return empty
    if len(available_participants) == 0:
        raise ValueError("No participants available this week")

    n_available = len(available_participants)

    # Less than 5 available: everyone in one group
    if n_available < 5:
        return {
            "all": available_participants.copy(),
            "unavailable": unavailable_list
        }

    # 5 or more: rotate who is solo
    # Week 1 → index 0 solo, Week 2 → index 1 solo, etc.
    solo_index = (week_number - 1) % n_available
    solo_person = available_participants[solo_index]

    # Main group is everyone except the solo person
    main_group = [p for i, p in enumerate(available_participants) if i != solo_index]

    return {
        "main": main_group,
        "solo": [solo_person],
        "unavailable": unavailable_list
    }


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
