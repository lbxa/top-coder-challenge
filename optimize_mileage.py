#!/usr/bin/env python3
"""
Optimize mileage calculator parameters using grid search
"""

import json
import subprocess
from itertools import product

def test_parameters(tier1_threshold, tier1_rate, tier2_rate):
    """Test a specific set of parameters"""
    
    # Update the mileage calculator
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
        self.tier_1_threshold = {tier1_threshold}  # Miles at which rate changes
        self.tier_1_rate = {tier1_rate}  # Rate for first tier ($/mile)
        self.tier_2_rate = {tier2_rate}  # Rate for second tier ($/mile)

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
    with open('components/mileage/mileage.py', 'w') as f:
        f.write(mileage_code)
    
    # Run eval.sh and capture the average error
    result = subprocess.run(['./eval.sh'], capture_output=True, text=True)
    
    # Parse the average error from output
    for line in result.stdout.split('\n'):
        if 'Average error:' in line:
            error_str = line.split('$')[1].strip()
            return float(error_str)
    
    return float('inf')

def optimize_mileage():
    """Find optimal mileage parameters"""
    
    # Define search space
    thresholds = [50, 75, 100, 125, 150, 200]
    tier1_rates = [0.40, 0.45, 0.50, 0.55, 0.58, 0.60, 0.65]
    tier2_rates = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    
    best_error = float('inf')
    best_params = None
    
    print("Starting mileage parameter optimization...")
    print("="*70)
    
    total_tests = len(thresholds) * len(tier1_rates) * len(tier2_rates)
    test_count = 0
    
    for threshold, rate1, rate2 in product(thresholds, tier1_rates, tier2_rates):
        test_count += 1
        
        # Skip if tier2 rate is higher than tier1 (doesn't make sense)
        if rate2 >= rate1:
            continue
        
        print(f"\nTest {test_count}/{total_tests}: Threshold={threshold}, Rate1=${rate1}, Rate2=${rate2}")
        
        try:
            error = test_parameters(threshold, rate1, rate2)
            print(f"  Average error: ${error:.2f}")
            
            if error < best_error:
                best_error = error
                best_params = {
                    'threshold': threshold,
                    'rate1': rate1,
                    'rate2': rate2
                }
                print(f"  *** NEW BEST! ***")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"\nBest parameters found:")
    print(f"  Tier 1 threshold: {best_params['threshold']} miles")
    print(f"  Tier 1 rate: ${best_params['rate1']}/mile")
    print(f"  Tier 2 rate: ${best_params['rate2']}/mile")
    print(f"  Average error: ${best_error:.2f}")
    
    # Apply best parameters
    test_parameters(best_params['threshold'], best_params['rate1'], best_params['rate2'])
    
    return best_params

if __name__ == "__main__":
    optimize_mileage()