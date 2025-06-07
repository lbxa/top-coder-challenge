"""
Bug Processor Module

Handles system bugs and quirks in the reimbursement system.
Based on intelligence from Lisa (Accounting) - Tier 1 source.

Key Hypotheses:
- Cents rounding "glitch" that adds bonus for receipts ending in .49 or .99
- Small fixed bonus amount (~$7.50) for these cases
- This is a genuine bug in the legacy system that we need to replicate

AI Agent Focus Areas:
1. Optimize the exact bonus amount for the cents bug
2. Verify the exact cents values that trigger the bug
3. Investigate if there are other similar rounding bugs
4. Check for edge cases in the cents calculation
5. Analyze if the bug interacts with other components
"""


class BugProcessor:
    """
    Processes system bugs and quirks that affect reimbursement calculations.

    This component handles the "unintentional" features of the legacy system
    that we need to replicate exactly, including bugs and glitches.
    """

    def __init__(self):
        # HYPOTHESIS: Cents rounding bug parameters
        self.cents_bug_values = [49, 99]  # Cents values that trigger the bug
        self.cents_bug_bonus = 7.50  # Bonus amount for cents bug

        # Potential future parameters for AI agents to explore:
        # self.other_cents_bug_values = [19, 29, 39]  # Additional trigger values
        # self.rounding_error_threshold = 0.005       # Floating point precision issues
        # self.leap_year_bug_bonus = 1.00            # Hypothetical date-based bug
        # self.negative_receipt_bug_penalty = 10.0    # Edge case handling

    def apply_bugs(self, receipts: float) -> float:
        """
        Apply all known system bugs and quirks.

        Args:
            receipts: Total receipt amount

        Returns:
            Total adjustment amount from bugs
        """
        total_bug_adjustment = 0.0

        # Apply cents rounding bug
        total_bug_adjustment += self._apply_cents_bug(receipts)

        # TODO for AI agents:
        # - Investigate other rounding bugs
        # - Check for floating point precision issues
        # - Analyze edge cases with zero or negative values
        # - Look for date-based bugs (if timestamps were available)
        # - Check for overflow/underflow bugs with very large values

        return total_bug_adjustment

    def _apply_cents_bug(self, receipts: float) -> float:
        """Apply the cents rounding bug bonus."""

        # Extract cents from receipt amount
        cents = int((receipts * 100) % 100)

        # Check if cents value triggers the bug
        if cents in self.cents_bug_values:
            return self.cents_bug_bonus

        return 0.0

    def get_parameters(self) -> dict:
        """Return current parameters for optimization."""
        return {
            "cents_bug_values": self.cents_bug_values,
            "cents_bug_bonus": self.cents_bug_bonus,
        }

    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        if "cents_bug_values" in params:
            self.cents_bug_values = params["cents_bug_values"]
        if "cents_bug_bonus" in params:
            self.cents_bug_bonus = params["cents_bug_bonus"]
