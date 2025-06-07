#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement System Replica
Based on reverse-engineering 1000 historical cases
"""

import random
from typing import Dict, Tuple


class ReimbursementCalculator:
    """Replicates ACME Corp's legacy reimbursement calculation logic."""
    
    def __init__(self):
        # Base parameters discovered from analysis
        self.base_per_diem = 100.0
        self.five_day_bonus = 15.0  # Extra per day for 5-day trips
        
        # Mileage tier rates (discovered from analysis)
        self.mileage_tiers = [
            (100, 0.58),   # 0-100 miles: $0.58/mile
            (300, 0.52),   # 100-300 miles: $0.52/mile
            (600, 0.48),   # 300-600 miles: $0.48/mile
            (float('inf'), 0.45)  # 600+ miles: $0.45/mile
        ]
        
        # Efficiency bonus parameters
        self.efficiency_sweet_spot = (180, 220)  # miles/day
        self.efficiency_bonus_rate = 0.08  # 8% bonus
        
        # Receipt penalty/coverage parameters
        self.small_receipt_threshold = 50
        self.small_receipt_penalty = 0.92  # 8% penalty
        self.high_receipt_threshold = 600
        self.receipt_coverage_base = 0.85  # 85% base coverage
        
        # Cluster-specific adjustments (simplified from 6 clusters)
        self.cluster_adjustments = {
            'road_warrior': 1.05,      # High mileage, short trips
            'optimal_business': 1.12,   # Sweet spot trips
            'extended_low': 0.95,       # Long trips, low activity
            'standard': 1.0,            # Normal business travel
            'local': 0.98,              # Short local trips
            'high_spend': 0.88          # High spending trips
        }
        
    def calculate_reimbursement(self, trip_duration_days: int, miles_traveled: float, 
                               total_receipts_amount: float) -> float:
        """
        Calculate reimbursement amount based on trip parameters.
        
        Args:
            trip_duration_days: Number of days of travel
            miles_traveled: Total miles traveled
            total_receipts_amount: Total dollar amount of receipts
            
        Returns:
            Total reimbursement amount in dollars
        """
        # Step 1: Classify trip into cluster
        cluster = self._classify_trip(trip_duration_days, miles_traveled, total_receipts_amount)
        
        # Step 2: Calculate base per diem
        per_diem_total = self._calculate_per_diem(trip_duration_days)
        
        # Step 3: Calculate mileage reimbursement
        mileage_total = self._calculate_mileage(miles_traveled)
        
        # Step 4: Calculate efficiency bonus
        efficiency_bonus = self._calculate_efficiency_bonus(
            trip_duration_days, miles_traveled, per_diem_total + mileage_total
        )
        
        # Step 5: Calculate receipt reimbursement with penalties
        receipt_reimbursement = self._calculate_receipt_reimbursement(
            total_receipts_amount, trip_duration_days
        )
        
        # Step 6: Sum components
        base_total = per_diem_total + mileage_total + efficiency_bonus + receipt_reimbursement
        
        # Step 7: Apply cluster-specific adjustment
        cluster_multiplier = self.cluster_adjustments.get(cluster, 1.0)
        adjusted_total = base_total * cluster_multiplier
        
        # Step 8: Add small random variation (±2%) to match system noise
        noise = random.uniform(-0.02, 0.02)
        final_total = adjusted_total * (1 + noise)
        
        # Step 9: Apply cents bug for receipts ending in .49 or .99
        if self._has_magic_cents(total_receipts_amount):
            final_total += random.uniform(2, 5)  # Small bonus
        
        return round(final_total, 2)
    
    def _classify_trip(self, days: int, miles: float, receipts: float) -> str:
        """Classify trip into one of the discovered clusters."""
        miles_per_day = miles / days if days > 0 else 0
        receipts_per_day = receipts / days if days > 0 else 0
        
        # High-mileage road warrior
        if miles_per_day > 400 and days <= 2:
            return 'road_warrior'
        
        # Optimal business travel (Kevin's sweet spot)
        if (days == 5 and 180 <= miles_per_day <= 220 and receipts_per_day < 100):
            return 'optimal_business'
        
        # Extended low-activity trips
        if days > 7 and miles_per_day < 100:
            return 'extended_low'
        
        # High spending trips
        if receipts_per_day > 150:
            return 'high_spend'
        
        # Local trips
        if miles < 50 and days <= 2:
            return 'local'
        
        # Default: standard business travel
        return 'standard'
    
    def _calculate_per_diem(self, days: int) -> float:
        """Calculate per diem with 5-day bonus."""
        base = self.base_per_diem * days
        
        # Apply 5-day bonus
        if days == 5:
            base += self.five_day_bonus * days
        
        return base
    
    def _calculate_mileage(self, miles: float) -> float:
        """Calculate tiered mileage reimbursement."""
        total = 0.0
        remaining_miles = miles
        prev_tier = 0
        
        for tier_limit, rate in self.mileage_tiers:
            tier_miles = min(remaining_miles, tier_limit - prev_tier)
            if tier_miles <= 0:
                break
            
            total += tier_miles * rate
            remaining_miles -= tier_miles
            prev_tier = tier_limit
        
        return total
    
    def _calculate_efficiency_bonus(self, days: int, miles: float, base_amount: float) -> float:
        """Calculate efficiency bonus for optimal miles/day."""
        if days == 0:
            return 0.0
        
        miles_per_day = miles / days
        
        # Check if in sweet spot
        if self.efficiency_sweet_spot[0] <= miles_per_day <= self.efficiency_sweet_spot[1]:
            return base_amount * self.efficiency_bonus_rate
        
        return 0.0
    
    def _calculate_receipt_reimbursement(self, receipts: float, days: int) -> float:
        """Calculate receipt reimbursement with penalties."""
        if receipts == 0:
            return 0.0
        
        # Small receipt penalty
        if 0 < receipts < self.small_receipt_threshold:
            return receipts * self.small_receipt_penalty * 0.7  # Extra penalty
        
        # High receipt diminishing returns
        if receipts > self.high_receipt_threshold:
            # First $600 at base rate
            base_amount = self.high_receipt_threshold * self.receipt_coverage_base
            # Remaining at diminishing rate
            excess = receipts - self.high_receipt_threshold
            excess_coverage = 0.5 * (1 - excess / 2000)  # Decreases with amount
            excess_coverage = max(0.2, excess_coverage)  # Floor at 20%
            return base_amount + (excess * excess_coverage)
        
        # Normal receipt coverage
        return receipts * self.receipt_coverage_base
    
    def _has_magic_cents(self, amount: float) -> bool:
        """Check if receipt amount ends in .49 or .99 (cents bug)."""
        cents = int(round(amount * 100)) % 100
        return cents in [49, 99]


def calculate_reimbursement(trip_duration_days: int, miles_traveled: float, 
                           total_receipts_amount: float) -> float:
    """
    Main entry point matching the PRD specification.
    
    Args:
        trip_duration_days: Number of days of travel
        miles_traveled: Total miles traveled
        total_receipts_amount: Total dollar amount of receipts
        
    Returns:
        Total reimbursement amount in dollars
    """
    calculator = ReimbursementCalculator()
    return calculator.calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)


if __name__ == "__main__":
    # Test with some example cases
    test_cases = [
        (3, 93, 1.42),    # From public_cases.json
        (5, 900, 450),    # 5-day optimal trip
        (1, 55, 3.60),    # Short local trip
        (8, 400, 1200),   # Extended high-spend trip
    ]
    
    print("Test Reimbursement Calculations:")
    print("-" * 50)
    for days, miles, receipts in test_cases:
        result = calculate_reimbursement(days, miles, receipts)
        print(f"Days: {days}, Miles: {miles}, Receipts: ${receipts:.2f}")
        print(f"  → Reimbursement: ${result:.2f}")
        print()