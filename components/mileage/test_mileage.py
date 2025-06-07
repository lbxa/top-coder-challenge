#!/usr/bin/env python3
"""
Test different mileage parameters to minimize error
"""

import os
import subprocess

def test_mileage_params(threshold, rate1, rate2):
    """Test specific mileage parameters"""
    
    # Update mileage.py with new parameters
    mileage_content = f'''"""
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
    
    # Write to mileage.py
    with open('components/mileage/mileage.py', 'w') as f:
        f.write(mileage_content)
    
    print(f"Testing: threshold={threshold}, rate1={rate1}, rate2={rate2}")
    
    # Run eval.sh and capture output
    result = subprocess.run(['./eval.sh'], capture_output=True, text=True)
    
    # Extract average error
    for line in result.stdout.split('\n'):
        if 'Average error:' in line:
            error = float(line.split('$')[1].strip())
            print(f"  Average error: ${error:.2f}")
            return error
    
    print("  Failed to parse error")
    return 99999

# Test a few parameter combinations
if __name__ == "__main__":
    print("Testing mileage parameters...")
    print("="*60)
    
    # Current parameters
    test_mileage_params(100.0, 0.55, 0.40)
    
    # Try different thresholds
    test_mileage_params(75.0, 0.55, 0.40)
    test_mileage_params(125.0, 0.55, 0.40)
    test_mileage_params(150.0, 0.55, 0.40)
    
    # Try different rates
    test_mileage_params(100.0, 0.50, 0.35)
    test_mileage_params(100.0, 0.60, 0.45)
    test_mileage_params(100.0, 0.58, 0.42)