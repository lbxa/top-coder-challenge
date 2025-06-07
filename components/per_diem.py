"""
Per Diem Calculator Module

Handles the base daily rate calculation component of the reimbursement system.
Based on intelligence from Kevin (Procurement) and Lisa (Accounting) - Tier 1 sources.

Key Hypothesis:
- Base rate is ~$100/day (from multiple sources)
- This is the simplest component and should be linear

AI Agent Focus Areas:
1. Validate the exact daily rate through data analysis
2. Check for any edge cases or special day-based rules
3. Investigate if there are different rates for different trip lengths
"""


class PerDiemCalculator:
    """
    Calculates per diem payments based on trip duration.

    This component is designed to be simple and focused, allowing
    an AI agent to optimize just the per diem logic independently.
    """

    def __init__(self):
        # HYPOTHESIS: Base daily rate (to be optimized)
        self.daily_rate = 100.00

        # Potential future parameters for AI agents to explore:
        # self.weekend_rate_multiplier = 1.0
        # self.long_trip_bonus_threshold = 10
        # self.long_trip_bonus_rate = 1.05

    def calculate(self, days: float) -> float:
        """
        Calculate per diem payment for given number of days.

        Args:
            days: Number of trip days (can be fractional)

        Returns:
            Per diem payment amount
        """
        if days <= 0:
            return 0.0

        # Basic calculation - AI agents can enhance this
        base_pay = days * self.daily_rate

        # TODO for AI agents:
        # - Analyze if there are step functions at certain day thresholds
        # - Check for weekend/weekday differences (if data supports it)
        # - Investigate diminishing returns for very long trips
        # - Look for rounding rules specific to per diem

        return base_pay

    def get_parameters(self) -> dict:
        """Return current parameters for optimization."""
        return {"daily_rate": self.daily_rate}

    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        if "daily_rate" in params:
            self.daily_rate = params["daily_rate"]
