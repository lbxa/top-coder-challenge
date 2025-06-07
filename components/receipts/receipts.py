"""
Receipt Processor Module

Handles the most complex component of the reimbursement system - receipt processing.
Based on intelligence from Kevin (Procurement), Dave (Marketing), and system observations.

Key Hypotheses (REFINED based on analysis):
- Penalties for very high spending per day (trip-length dependent thresholds)
- Penalties for very low spending per day  
- Complex tier system: 1-3 days (>$100/day), 4-7 days (>$150/day), 8+ days (>$120/day)
- Small receipt penalty for receipts < $20/day (results in near-zero reimbursement)
- Receipt amount cannot reduce base pay below zero
- Processing ratios vary by trip length and spending amount

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
        self.short_trip_threshold = 100.0  # $/day threshold for 1-3 day trips
        self.medium_trip_threshold = 150.0  # $/day threshold for 4-7 day trips
        self.long_trip_threshold = 120.0  # $/day threshold for 8+ day trips

        # HYPOTHESIS: Penalty factors for overspending
        self.short_trip_penalty_factor = 0.45  # Penalty multiplier for 1-3 days (~57% retention)
        self.medium_trip_penalty_factor = 0.40  # Penalty multiplier for 4-7 days (~60% retention)
        self.long_trip_penalty_factor = 0.50  # Penalty multiplier for 8+ days (~50% retention)

        # HYPOTHESIS: Small receipt penalty (severe for very low spending)
        self.small_receipt_threshold = 20.0  # $/day threshold for small receipts
        self.small_receipt_penalty_factor = 0.95  # Penalty factor (5% reimbursement)
        
        # Additional parameters for refined model
        self.moderate_spending_threshold = 50.0  # $/day for moderate spending
        self.moderate_spending_factor = 0.8  # 80% reimbursement for moderate spending

        # Potential future parameters for AI agents to explore:
        # self.zero_receipt_penalty = 0.0  # No penalty for zero receipts
        # self.maximum_daily_reimbursement = 150.0  # Cap on daily reimbursement
        # self.very_high_spending_threshold = 200.0  # Threshold for extreme spending
        # self.weekend_receipt_bonus = 1.1  # Weekend receipt multiplier

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
            # Apply severe penalty for very low spending (results in ~5% reimbursement)
            receipt_pay = receipts * (1 - self.small_receipt_penalty_factor)
        elif receipts_per_day < self.moderate_spending_threshold:
            # Apply moderate penalty for low-moderate spending
            receipt_pay = receipts * self.moderate_spending_factor

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
            "small_receipt_penalty_factor": self.small_receipt_penalty_factor,
            "moderate_spending_threshold": self.moderate_spending_threshold,
            "moderate_spending_factor": self.moderate_spending_factor,
        }

    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        for param_name, param_value in params.items():
            if hasattr(self, param_name):
                setattr(self, param_name, param_value)
