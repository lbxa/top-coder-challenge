"""
Bonus Calculator Module

Handles all bonus calculations in the reimbursement system.
Based on intelligence from Lisa (Accounting) and Kevin (Procurement) - Tier 1 sources.

Key Hypotheses:
- 5-day trip "sweet spot" bonus (~$75)
- Efficiency "hustle" bonus for optimal miles/day ratio (180-220 miles/day, ~$65)
- Bonuses are applied after base calculations

AI Agent Focus Areas:
1. Optimize the exact 5-day bonus amount
2. Determine precise efficiency bonus range and amount
3. Investigate if there are other trip-length bonuses
4. Check for interaction effects between bonuses
5. Analyze if bonuses have caps or diminishing returns
"""


class BonusCalculator:
    """
    Calculates all bonus payments based on trip characteristics.

    This component handles the "positive" adjustments to reimbursement,
    allowing an AI agent to focus on optimizing bonus conditions and amounts.
    """

    def __init__(self):
        # HYPOTHESIS: 5-day trip bonus (Lisa's tip)
        self.five_day_bonus_amount = 75.0

        # HYPOTHESIS: Efficiency bonus parameters (Kevin's insight)
        self.efficiency_bonus_min_miles_per_day = 180.0
        self.efficiency_bonus_max_miles_per_day = 220.0
        self.efficiency_bonus_amount = 65.0

        # Potential future parameters for AI agents to explore:
        # self.weekend_trip_bonus = 25.0
        # self.long_trip_bonus_threshold = 10  # days
        # self.long_trip_bonus_amount = 100.0
        # self.high_mileage_bonus_threshold = 500  # miles
        # self.perfect_receipt_bonus = 15.0  # for receipts ending in .00

    def calculate_all_bonuses(
        self, days: float, miles: float, receipts: float
    ) -> float:
        """
        Calculate total bonus amount for the trip.

        Args:
            days: Number of trip days
            miles: Total miles traveled
            receipts: Total receipt amount

        Returns:
            Total bonus amount
        """
        total_bonus = 0.0

        # 5-day trip bonus
        total_bonus += self._calculate_five_day_bonus(days)

        # Efficiency bonus
        total_bonus += self._calculate_efficiency_bonus(days, miles)

        # TODO for AI agents:
        # - Investigate weekend trip bonuses
        # - Check for long trip bonuses
        # - Analyze high mileage bonuses
        # - Look for receipt-based bonuses (beyond the cents bug)
        # - Check for seasonal or time-based bonuses

        return total_bonus

    def _calculate_five_day_bonus(self, days: float) -> float:
        """Calculate bonus for 5-day trips."""
        if days == 5:
            return self.five_day_bonus_amount
        return 0.0

    def _calculate_efficiency_bonus(self, days: float, miles: float) -> float:
        """Calculate efficiency bonus for optimal miles/day ratio."""
        if days <= 0:
            return 0.0

        miles_per_day = miles / days

        if (
            self.efficiency_bonus_min_miles_per_day
            <= miles_per_day
            <= self.efficiency_bonus_max_miles_per_day
        ):
            return self.efficiency_bonus_amount

        return 0.0

    def get_parameters(self) -> dict:
        """Return current parameters for optimization."""
        return {
            "five_day_bonus_amount": self.five_day_bonus_amount,
            "efficiency_bonus_min_miles_per_day": self.efficiency_bonus_min_miles_per_day,
            "efficiency_bonus_max_miles_per_day": self.efficiency_bonus_max_miles_per_day,
            "efficiency_bonus_amount": self.efficiency_bonus_amount,
        }

    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        for param_name, param_value in params.items():
            if hasattr(self, param_name):
                setattr(self, param_name, param_value)
