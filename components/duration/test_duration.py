"""
Test file for the Duration Calculator module.

This file contains basic tests to verify the duration module functionality.
"""

from duration import DurationCalculator


def test_duration_calculator():
    """Test basic duration calculator functionality."""
    calc = DurationCalculator()

    print("=== Duration Calculator Tests ===")

    # Test 5-day bonus
    five_day_adjustment = calc.calculate(5.0)
    print(f"5-day trip adjustment: ${five_day_adjustment}")

    # Test regular days
    three_day_adjustment = calc.calculate(3.0)
    print(f"3-day trip adjustment: ${three_day_adjustment}")

    # Test short trip
    one_day_adjustment = calc.calculate(1.0)
    print(f"1-day trip adjustment: ${one_day_adjustment}")

    # Test long trip
    ten_day_adjustment = calc.calculate(10.0)
    print(f"10-day trip adjustment: ${ten_day_adjustment}")

    # Test duration categories
    print("\n=== Duration Categories ===")
    test_days = [1, 2, 3, 5, 7, 10]
    for days in test_days:
        category = calc.get_duration_category(days)
        is_special = calc.is_special_duration(days)
        print(f"{days} days: {category} (special: {is_special})")

    # Test parameter management
    print("\n=== Parameter Management ===")
    params = calc.get_parameters()
    print(f"Current parameters: {params}")

    # Test parameter modification
    calc.set_parameters({"five_day_bonus_amount": 75.0})
    new_five_day_adjustment = calc.calculate(5.0)
    print(f"5-day adjustment with $75 bonus: ${new_five_day_adjustment}")


if __name__ == "__main__":
    test_duration_calculator()
