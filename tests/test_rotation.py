"""Unit tests for rotation calculation logic."""

import pytest
from datetime import date, timedelta
from src.rotation import calculate_current_week, get_rotation, validate_participants


class TestCalculateCurrentWeek:
    """Tests for calculate_current_week function."""

    def test_week_1_on_start_date(self):
        """Test that start date is week 1."""
        start = date(2026, 2, 17)
        # Mock today as start date
        with pytest.MonkeyPatch.context() as m:
            m.setattr("src.rotation.date", type("MockDate", (), {
                "today": lambda: start
            }))
            assert calculate_current_week(start) == 1

    def test_week_2_after_7_days(self):
        """Test week 2 after 7 days."""
        start = date(2026, 2, 17)
        week_2_date = start + timedelta(days=7)
        with pytest.MonkeyPatch.context() as m:
            m.setattr("src.rotation.date", type("MockDate", (), {
                "today": lambda: week_2_date
            }))
            assert calculate_current_week(start) == 2

    def test_week_calculation_mid_week(self):
        """Test week calculation in the middle of a week."""
        start = date(2026, 2, 17)
        mid_week_date = start + timedelta(days=10)  # 10 days = still week 2
        with pytest.MonkeyPatch.context() as m:
            m.setattr("src.rotation.date", type("MockDate", (), {
                "today": lambda: mid_week_date
            }))
            assert calculate_current_week(start) == 2

    def test_week_3_after_14_days(self):
        """Test week 3 after 14 days."""
        start = date(2026, 2, 17)
        week_3_date = start + timedelta(days=14)
        with pytest.MonkeyPatch.context() as m:
            m.setattr("src.rotation.date", type("MockDate", (), {
                "today": lambda: week_3_date
            }))
            assert calculate_current_week(start) == 3

    def test_date_before_start_returns_week_1(self):
        """Test that dates before start date return week 1."""
        start = date(2026, 2, 17)
        before_start = start - timedelta(days=5)
        with pytest.MonkeyPatch.context() as m:
            m.setattr("src.rotation.date", type("MockDate", (), {
                "today": lambda: before_start
            }))
            assert calculate_current_week(start) == 1


class TestGetRotationSingleGroup:
    """Tests for get_rotation with < 5 participants (single group)."""

    def test_single_participant(self):
        """Test with 1 participant."""
        result = get_rotation(1, ["Alice"])
        assert result == {"all": ["Alice"]}

    def test_two_participants(self):
        """Test with 2 participants."""
        result = get_rotation(1, ["Alice", "Bob"])
        assert result == {"all": ["Alice", "Bob"]}

    def test_three_participants(self):
        """Test with 3 participants."""
        result = get_rotation(1, ["Alice", "Bob", "Charlie"])
        assert result == {"all": ["Alice", "Bob", "Charlie"]}

    def test_four_participants(self):
        """Test with 4 participants (boundary case)."""
        result = get_rotation(1, ["Alice", "Bob", "Charlie", "Diana"])
        assert result == {"all": ["Alice", "Bob", "Charlie", "Diana"]}

    def test_single_group_week_number_doesnt_matter(self):
        """Test that week number doesn't affect single group."""
        participants = ["Alice", "Bob", "Charlie"]
        week_1 = get_rotation(1, participants)
        week_2 = get_rotation(2, participants)
        week_10 = get_rotation(10, participants)

        assert week_1 == week_2 == week_10 == {"all": participants}


class TestGetRotationTwoGroups:
    """Tests for get_rotation with >= 5 participants (two groups)."""

    def test_five_participants_week_1(self):
        """Test 5 participants, week 1: last person solo."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        result = get_rotation(1, participants)

        assert "main" in result
        assert "solo" in result
        assert result["solo"] == ["Alice"]
        assert result["main"] == ["Bob", "Charlie", "Diana", "Eve"]
        assert len(result["main"]) == 4
        assert len(result["solo"]) == 1

    def test_five_participants_week_2(self):
        """Test 5 participants, week 2: first person solo."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        result = get_rotation(2, participants)

        assert result["solo"] == ["Bob"]
        assert result["main"] == ["Alice", "Charlie", "Diana", "Eve"]

    def test_five_participants_rotation_cycle(self):
        """Test that rotation cycles through all 5 participants."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve"]

        week_1 = get_rotation(1, participants)
        week_2 = get_rotation(2, participants)
        week_3 = get_rotation(3, participants)
        week_4 = get_rotation(4, participants)
        week_5 = get_rotation(5, participants)

        # Each person should be solo exactly once in 5 weeks
        solo_people = [
            week_1["solo"][0],
            week_2["solo"][0],
            week_3["solo"][0],
            week_4["solo"][0],
            week_5["solo"][0]
        ]

        assert set(solo_people) == set(participants)
        assert len(solo_people) == 5

    def test_five_participants_week_6_repeats_week_1(self):
        """Test that week 6 repeats week 1 pattern."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        week_1 = get_rotation(1, participants)
        week_6 = get_rotation(6, participants)

        assert week_1 == week_6

    def test_six_participants(self):
        """Test with 6 participants."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
        result = get_rotation(1, participants)

        assert len(result["main"]) == 5
        assert len(result["solo"]) == 1
        assert result["solo"][0] in participants

    def test_eight_participants(self):
        """Test with 8 participants (maximum)."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank"]
        result = get_rotation(1, participants)

        assert len(result["main"]) == 7
        assert len(result["solo"]) == 1
        assert result["solo"][0] in participants

    def test_eight_participants_full_cycle(self):
        """Test that 8 participants cycle through all in 8 weeks."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank"]

        solo_people = []
        for week in range(1, 9):
            result = get_rotation(week, participants)
            solo_people.append(result["solo"][0])

        # All 8 people should be solo once
        assert set(solo_people) == set(participants)
        assert len(solo_people) == 8


class TestValidateParticipants:
    """Tests for validate_participants function."""

    def test_valid_participants(self):
        """Test valid participants list."""
        validate_participants(["Alice", "Bob", "Charlie"])
        # Should not raise

    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_participants([])

    def test_too_many_participants_raises_error(self):
        """Test that > 8 participants raises ValueError."""
        participants = [f"Person{i}" for i in range(9)]
        with pytest.raises(ValueError, match="Maximum 8 participants"):
            validate_participants(participants)

    def test_duplicate_names_raises_error(self):
        """Test that duplicate names raise ValueError."""
        with pytest.raises(ValueError, match="duplicates"):
            validate_participants(["Alice", "Bob", "Alice"])

    def test_empty_names_raises_error(self):
        """Test that empty names raise ValueError."""
        with pytest.raises(ValueError, match="empty names"):
            validate_participants(["Alice", "", "Bob"])

        with pytest.raises(ValueError, match="empty names"):
            validate_participants(["Alice", "  ", "Bob"])


class TestGetRotationEdgeCases:
    """Tests for edge cases in get_rotation."""

    def test_empty_participants_raises_error(self):
        """Test that empty participants list raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            get_rotation(1, [])

    def test_too_many_participants_raises_error(self):
        """Test that > 8 participants raises ValueError."""
        participants = [f"Person{i}" for i in range(9)]
        with pytest.raises(ValueError, match="Maximum 8 participants"):
            get_rotation(1, participants)

    def test_large_week_number(self):
        """Test with large week number."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        result = get_rotation(100, participants)

        # Should still work and cycle correctly
        assert "main" in result
        assert "solo" in result
        assert len(result["main"]) == 4
        assert len(result["solo"]) == 1

    def test_rotation_preserves_participant_names(self):
        """Test that rotation doesn't modify participant names."""
        participants = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        original_participants = participants.copy()

        get_rotation(1, participants)

        # Original list should be unchanged
        assert participants == original_participants
