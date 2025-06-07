"""
Receipt Processor Module

Handles the most complex component of the reimbursement system - receipt processing.
Based on intelligence from Kevin (Procurement), Dave (Marketing), and system observations.

Key Hypotheses:
- Penalties for very high spending per day (trip-length dependent thresholds)
- Penalties for very low spending per day
- Complex tier system: 1-3 days (>$75/day), 4-7 days (>$120/day), 8+ days (>$90/day)
- Small receipt penalty (~$50) for receipts < $20/day
- Receipt amount cannot reduce base pay below zero

AI Agent Focus Areas:
1. Optimize penalty thresholds and factors for each trip length category
2. Investigate the exact small receipt penalty amount and threshold
3. Analyze edge cases around tier boundaries
4. Determine if there are additional receipt processing rules
5. Check for interaction effects with other components
"""


class ReceiptProcessor:
    """
    Processes receipt amounts with penalties and caps based on trip duration.

    This is the most complex component, requiring careful analysis of
    trip-length dependent thresholds and penalty structures.
    """

    def __init__(self):
        # HYPOTHESIS: Trip-length dependent spending thresholds
        self.short_trip_days = (1, 3)  # 1-3 days
        self.medium_trip_days = (4, 7)  # 4-7 days
        self.long_trip_days = 8  # 8+ days

        # HYPOTHESIS: Spending thresholds per day for each trip length
        self.short_trip_threshold = 75.0  # $/day threshold for 1-3 day trips
        self.medium_trip_threshold = 120.0  # $/day threshold for 4-7 day trips
        self.long_trip_threshold = 90.0  # $/day threshold for 8+ day trips

        # HYPOTHESIS: Penalty factors for overspending
        self.short_trip_penalty_factor = 0.5  # Penalty multiplier for 1-3 days
        self.medium_trip_penalty_factor = 0.75  # Penalty multiplier for 4-7 days
        self.long_trip_penalty_factor = 1.0  # Penalty multiplier for 8+ days

        # HYPOTHESIS: Small receipt penalty
        self.small_receipt_threshold = 20.0  # $/day threshold for small receipts
        self.small_receipt_penalty = 50.0  # Flat penalty amount

        # Potential future parameters for AI agents to explore:
        # self.zero_receipt_penalty = 25.0
        # self.maximum_daily_reimbursement = 200.0
        # self.receipt_rounding_threshold = 0.50

    def process(self, days: float, receipts: float) -> float:
        """
        Process receipt amount with penalties and caps.

        Args:
            days: Number of trip days
            receipts: Total receipt amount

        Returns:
            Processed receipt payment amount
        """
        if days <= 0:
            return 0.0

        # Start with full receipt amount
        receipt_pay = receipts
        receipts_per_day = receipts / days if days > 0 else 0

        # Apply overspending penalties based on trip length
        receipt_pay = self._apply_overspending_penalties(
            receipt_pay, days, receipts_per_day
        )

        # Apply small receipt penalty
        receipt_pay = self._apply_small_receipt_penalty(
            receipt_pay, receipts, receipts_per_day
        )

        # Ensure receipt pay cannot go negative (old system constraint)
        receipt_pay = max(0, receipt_pay)

        return receipt_pay

    def _apply_overspending_penalties(
        self, receipt_pay: float, days: float, receipts_per_day: float
    ) -> float:
        """Apply penalties for overspending based on trip length."""

        # Short trips (1-3 days)
        if (
            self.short_trip_days[0] <= days <= self.short_trip_days[1]
            and receipts_per_day > self.short_trip_threshold
        ):
            overage = receipts_per_day - self.short_trip_threshold
            penalty = overage * days * self.short_trip_penalty_factor
            receipt_pay -= penalty

        # Medium trips (4-7 days)
        elif (
            self.medium_trip_days[0] <= days <= self.medium_trip_days[1]
            and receipts_per_day > self.medium_trip_threshold
        ):
            overage = receipts_per_day - self.medium_trip_threshold
            penalty = overage * days * self.medium_trip_penalty_factor
            receipt_pay -= penalty

        # Long trips (8+ days)
        elif (
            days >= self.long_trip_days and receipts_per_day > self.long_trip_threshold
        ):
            overage = receipts_per_day - self.long_trip_threshold
            penalty = overage * days * self.long_trip_penalty_factor
            receipt_pay -= penalty

        return receipt_pay

    def _apply_small_receipt_penalty(
        self, receipt_pay: float, receipts: float, receipts_per_day: float
    ) -> float:
        """Apply penalty for very small receipt amounts."""

        if 0 < receipts and receipts_per_day < self.small_receipt_threshold:
            receipt_pay -= self.small_receipt_penalty

        return receipt_pay

    def get_parameters(self) -> dict:
        """Return current parameters for optimization."""
        return {
            "short_trip_threshold": self.short_trip_threshold,
            "medium_trip_threshold": self.medium_trip_threshold,
            "long_trip_threshold": self.long_trip_threshold,
            "short_trip_penalty_factor": self.short_trip_penalty_factor,
            "medium_trip_penalty_factor": self.medium_trip_penalty_factor,
            "long_trip_penalty_factor": self.long_trip_penalty_factor,
            "small_receipt_threshold": self.small_receipt_threshold,
            "small_receipt_penalty": self.small_receipt_penalty,
        }

    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        for param_name, param_value in params.items():
            if hasattr(self, param_name):
                setattr(self, param_name, param_value)
