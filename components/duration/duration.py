"""
Duration Calculator Module

Handles duration-specific calculations and bonuses in the reimbursement system.
Based on analysis of trip duration patterns and potential duration-based bonuses.

Key Hypotheses:
- Certain trip durations may have special bonuses (e.g., 5-day trips)
- Very short trips (1-2 days) might have different base calculations
- Long trips (8+ days) might have diminishing returns or caps
- Weekend vs weekday duration effects

AI Agent Focus Areas:
1. Identify duration-specific bonuses and penalties
2. Analyze patterns for specific trip lengths (especially 5-day trips)
3. Investigate minimum/maximum duration thresholds
4. Check for weekend/weekday effects on duration calculations
5. Explore interaction effects between duration and other components
"""


class DurationCalculator:
    """
    Calculates duration-specific adjustments and bonuses.

    This component handles any special logic related to trip duration
    that isn't covered by the base per diem calculation.
    """

    def __init__(self):
        # HYPOTHESIS: Special duration bonuses
        self.five_day_bonus_enabled = True
        self.five_day_bonus_amount = -150  # Flat penalty for 5-day trips (optimized)

        # HYPOTHESIS: Short trip adjustments
        self.short_trip_threshold = 2  # Days
        self.short_trip_multiplier = 1.0  # Multiplier for short trips

        # HYPOTHESIS: Long trip adjustments
        self.long_trip_threshold = 8  # Days
        self.long_trip_diminishing_factor = 0.95  # Diminishing returns factor

        # HYPOTHESIS: Weekend effects
        self.weekend_bonus_enabled = False
        self.weekend_bonus_per_day = 10.0  # Additional bonus per weekend day

        # Potential future parameters for AI agents to explore:
        # self.three_day_bonus = 25.0
        # self.seven_day_bonus = 75.0
        # self.minimum_trip_duration = 0.5
        # self.maximum_trip_duration = 30.0
        # self.business_day_multiplier = 1.05

    def calculate(self, days: float) -> float:
        """
        Calculate duration-specific adjustments and bonuses.

        Args:
            days: Number of trip days (can be fractional)

        Returns:
            Duration-specific adjustment amount (can be positive or negative)
        """
        if days <= 0:
            return 0.0

        total_adjustment = 0.0

        # Apply 5-day bonus (most commonly referenced in analysis)
        if self.five_day_bonus_enabled and days == 5:
            total_adjustment += self.five_day_bonus_amount

        # Apply short trip adjustments
        if days <= self.short_trip_threshold:
            # Could be a penalty or bonus - to be optimized
            adjustment = (
                (self.short_trip_multiplier - 1.0) * days * 100
            )  # Base rate assumption
            total_adjustment += adjustment

        # Apply long trip diminishing returns
        if days >= self.long_trip_threshold:
            # Diminishing returns for very long trips
            excess_days = days - self.long_trip_threshold
            penalty = excess_days * (1.0 - self.long_trip_diminishing_factor) * 100
            total_adjustment -= penalty

        # Apply weekend bonuses (if enabled)
        if self.weekend_bonus_enabled:
            # Simplified assumption: ~2/7 of days are weekends
            estimated_weekend_days = days * (2.0 / 7.0)
            weekend_bonus = estimated_weekend_days * self.weekend_bonus_per_day
            total_adjustment += weekend_bonus

        # TODO for AI agents:
        # - Analyze data for specific duration patterns (3-day, 7-day bonuses)
        # - Check for step functions at certain day thresholds
        # - Investigate business day vs calendar day calculations
        # - Look for seasonal or date-specific effects
        # - Analyze interaction with other components (receipts, mileage)
        # - Check for rounding rules specific to duration

        return total_adjustment

    def get_duration_category(self, days: float) -> str:
        """
        Categorize trip duration for analysis purposes.

        Args:
            days: Number of trip days

        Returns:
            Duration category string
        """
        if days <= 0:
            return "invalid"
        elif days <= 2:
            return "short"
        elif days <= 4:
            return "medium"
        elif days == 5:
            return "five_day_special"
        elif days <= 7:
            return "week_long"
        else:
            return "extended"

    def is_special_duration(self, days: float) -> bool:
        """
        Check if this duration has special handling.

        Args:
            days: Number of trip days

        Returns:
            True if this duration has special bonuses/penalties
        """
        # 5-day trips are commonly mentioned as special
        if days == 5:
            return True

        # Very short or very long trips might have special handling
        if days <= self.short_trip_threshold or days >= self.long_trip_threshold:
            return True

        return False

    def get_parameters(self) -> dict:
        """Return current parameters for optimization."""
        return {
            "five_day_bonus_enabled": self.five_day_bonus_enabled,
            "five_day_bonus_amount": self.five_day_bonus_amount,
            "short_trip_threshold": self.short_trip_threshold,
            "short_trip_multiplier": self.short_trip_multiplier,
            "long_trip_threshold": self.long_trip_threshold,
            "long_trip_diminishing_factor": self.long_trip_diminishing_factor,
            "weekend_bonus_enabled": self.weekend_bonus_enabled,
            "weekend_bonus_per_day": self.weekend_bonus_per_day,
        }

    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        for param_name, param_value in params.items():
            if hasattr(self, param_name):
                setattr(self, param_name, param_value)
