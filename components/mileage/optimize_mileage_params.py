#!/usr/bin/env python3
"""
Optimize ONLY the mileage calculator parameters
This script modifies only components/mileage/mileage.py
"""

import subprocess
import os
import sys

# Add parent directory to path to import main
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def update_mileage_params(threshold, rate1, rate2):
    """Update only the mileage.py file with new parameters"""

    mileage_code = f'''"""
Mileage Calculator Module

Handles the tiered mileage rate calculation component of the reimbursement system.
Based on intelligence from Kevin (Procurement) - Tier 1 source.

Key Hypothesis:
- Tiered system with rate drop-off after ~100 miles
- Higher rate for first 100 miles, lower rate for additional miles
- Rates approximately 0.58 and 0.45 based on current implementation

AI Agent Focus Areas:
1. Determine exact tier thresholds and rates through data analysis
2. Investigate if there are more than 2 tiers
3. Check for any caps or maximum mileage limits
4. Analyze edge cases around the tier boundaries
"""


class MileageCalculator:
    """
    Calculates mileage payments based on tiered rate structure.

    This component handles the complexity of different rates for different
    mileage ranges, allowing an AI agent to focus on optimizing the tier
    structure independently.
    """

    def __init__(self):
        # HYPOTHESIS: Tiered rate structure (to be optimized)
        self.tier_1_threshold = {threshold}  # Miles at which rate changes
        self.tier_1_rate = {rate1}  # Rate for first tier ($/mile)
        self.tier_2_rate = {rate2}  # Rate for second tier ($/mile)

        # Potential future parameters for AI agents to explore:
        # self.tier_3_threshold = 500.0
        # self.tier_3_rate = 0.30
        # self.max_reimbursable_miles = 1000.0
        # self.minimum_miles_for_payment = 5.0

    def calculate(self, miles: float) -> float:
        """
        Calculate mileage payment for given miles traveled.

        Args:
            miles: Total miles traveled

        Returns:
            Mileage payment amount
        """
        if miles <= 0:
            return 0.0

        # Tier 1: First portion of miles
        tier_1_miles = min(miles, self.tier_1_threshold)
        tier_1_pay = tier_1_miles * self.tier_1_rate

        # Tier 2: Remaining miles (if any)
        tier_2_miles = max(0, miles - self.tier_1_threshold)
        tier_2_pay = tier_2_miles * self.tier_2_rate

        total_mileage_pay = tier_1_pay + tier_2_pay

        # TODO for AI agents:
        # - Analyze data for additional tier breakpoints
        # - Check for maximum mileage caps
        # - Investigate minimum mileage thresholds
        # - Look for special cases (e.g., round-trip vs one-way)
        # - Check for interaction with trip duration (miles/day effects)

        return total_mileage_pay

    def get_parameters(self) -> dict:
        """Return current parameters for optimization."""
        return {{
            "tier_1_threshold": self.tier_1_threshold,
            "tier_1_rate": self.tier_1_rate,
            "tier_2_rate": self.tier_2_rate,
        }}

    def set_parameters(self, params: dict) -> None:
        """Set parameters from optimization process."""
        if "tier_1_threshold" in params:
            self.tier_1_threshold = params["tier_1_threshold"]
        if "tier_1_rate" in params:
            self.tier_1_rate = params["tier_1_rate"]
        if "tier_2_rate" in params:
            self.tier_2_rate = params["tier_2_rate"]
'''

    # Write the updated mileage calculator
    mileage_path = os.path.join(os.path.dirname(__file__), "mileage.py")
    with open(mileage_path, "w") as f:
        f.write(mileage_code)


def test_parameters(threshold, rate1, rate2):
    """Test specific mileage parameters and return average error"""

    # Update the mileage.py file
    update_mileage_params(threshold, rate1, rate2)

    # Run eval.sh from the root directory
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    os.chdir(root_dir)

    result = subprocess.run(["./eval.sh"], capture_output=True, text=True)

    # Parse average error from output
    for line in result.stdout.split("\n"):
        if "Average error:" in line:
            try:
                error_str = line.split("$")[1].strip()
                return float(error_str)
            except:
                pass

    # If we can't parse the error, return a large value
    return 999999.0


def optimize_mileage():
    """Find optimal mileage parameters through grid search"""

    print("Starting mileage parameter optimization...")
    print("This will ONLY modify components/mileage/mileage.py")
    print("=" * 70)

    # Define search space
    thresholds = [50, 75, 100, 125, 150]
    tier1_rates = [0.40, 0.45, 0.50, 0.55, 0.58, 0.60]
    tier2_rates = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45]

    best_error = float("inf")
    best_params = None

    total_tests = len(thresholds) * len(tier1_rates) * len(tier2_rates)
    test_count = 0

    for threshold in thresholds:
        for rate1 in tier1_rates:
            for rate2 in tier2_rates:
                # Skip if tier2 rate is higher than tier1 (doesn't make sense)
                if rate2 >= rate1:
                    continue

                test_count += 1
                print(
                    f"\nTest {test_count}: Threshold={threshold}, Rate1=${rate1:.2f}, Rate2=${rate2:.2f}"
                )

                try:
                    error = test_parameters(threshold, rate1, rate2)
                    print(f"  Average error: ${error:.2f}")

                    if error < best_error:
                        best_error = error
                        best_params = {
                            "threshold": threshold,
                            "rate1": rate1,
                            "rate2": rate2,
                        }
                        print(f"  *** NEW BEST! ***")
                except Exception as e:
                    print(f"  Error: {e}")

    if best_params:
        print("\n" + "=" * 70)
        print("OPTIMIZATION COMPLETE")
        print("=" * 70)
        print(f"\nBest mileage parameters found:")
        print(f"  Tier 1 threshold: {best_params['threshold']} miles")
        print(f"  Tier 1 rate: ${best_params['rate1']:.2f}/mile")
        print(f"  Tier 2 rate: ${best_params['rate2']:.2f}/mile")
        print(f"  Average error: ${best_error:.2f}")

        # Apply best parameters
        update_mileage_params(
            best_params["threshold"], best_params["rate1"], best_params["rate2"]
        )
        print("\nBest parameters have been applied to components/mileage/mileage.py")
    else:
        print("\nNo valid parameters found!")

    return best_params


if __name__ == "__main__":
    optimize_mileage()
