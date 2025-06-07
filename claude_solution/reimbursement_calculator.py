#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement System Replica
Based on reverse-engineering 1000 historical cases with k-means clustering analysis
"""

import random
from typing import Tuple


class ReimbursementCalculator:
    """
    Replicates ACME Corp's legacy reimbursement calculation logic.
    Uses 6 distinct calculation paths discovered through clustering analysis.
    """
    
    def __init__(self):
        # Base parameters discovered from analysis
        self.base_per_diem = 100.0
        self.five_day_bonus_rate = 0.15  # 15% bonus for 5-day trips
        
        # Mileage tier rates (discovered from analysis)
        self.mileage_tiers = [
            (100, 0.58),     # 0-100 miles: $0.58/mile (standard rate)
            (300, 0.52),     # 100-300 miles: $0.52/mile
            (600, 0.47),     # 300-600 miles: $0.47/mile
            (1000, 0.42),    # 600-1000 miles: $0.42/mile
            (float('inf'), 0.38)  # 1000+ miles: $0.38/mile
        ]
        
        # Efficiency bonus parameters (Kevin's sweet spot confirmed)
        self.efficiency_sweet_spot = (180, 220)  # miles/day
        self.efficiency_bonus_rate = 0.08  # 8% bonus
        self.high_efficiency_penalty = 0.95  # 5% penalty for >300 miles/day
        
        # Receipt parameters
        self.small_receipt_threshold = 50
        self.small_receipt_penalty_rate = 0.85  # Only 85% coverage
        self.medium_receipt_range = (50, 600)
        self.medium_receipt_coverage = 0.92  # 92% coverage
        self.high_receipt_threshold = 600
        self.high_receipt_base_coverage = 0.88  # 88% for first $600
        self.high_receipt_excess_decay = 0.0003  # Decay rate for excess
        
        # Cluster-specific parameters (from k-means analysis)
        self.cluster_configs = {
            'road_warrior': {
                'multiplier': 1.05,
                'per_diem_adj': 1.0,
                'mileage_adj': 1.08,
                'receipt_adj': 0.95
            },
            'optimal_business': {
                'multiplier': 1.15,
                'per_diem_adj': 1.12,
                'mileage_adj': 1.05,
                'receipt_adj': 1.0
            },
            'extended_low': {
                'multiplier': 0.92,
                'per_diem_adj': 0.95,
                'mileage_adj': 0.98,
                'receipt_adj': 0.9
            },
            'standard': {
                'multiplier': 1.0,
                'per_diem_adj': 1.0,
                'mileage_adj': 1.0,
                'receipt_adj': 1.0
            },
            'local': {
                'multiplier': 0.96,
                'per_diem_adj': 0.98,
                'mileage_adj': 0.95,
                'receipt_adj': 0.92
            },
            'high_spend': {
                'multiplier': 0.85,
                'per_diem_adj': 1.02,
                'mileage_adj': 0.98,
                'receipt_adj': 0.75
            }
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
        cluster, cluster_config = self._classify_trip(trip_duration_days, miles_traveled, total_receipts_amount)
        
        # Step 2: Calculate base per diem with adjustments
        per_diem_total = self._calculate_per_diem(trip_duration_days, cluster_config)
        
        # Step 3: Calculate mileage reimbursement with tiering
        mileage_total = self._calculate_mileage(miles_traveled, cluster_config)
        
        # Step 4: Calculate efficiency bonus/penalty
        efficiency_adjustment = self._calculate_efficiency_adjustment(
            trip_duration_days, miles_traveled, per_diem_total + mileage_total
        )
        
        # Step 5: Calculate receipt reimbursement with coverage rules
        receipt_reimbursement = self._calculate_receipt_reimbursement(
            total_receipts_amount, trip_duration_days, cluster_config
        )
        
        # Step 6: Sum components
        base_total = per_diem_total + mileage_total + efficiency_adjustment + receipt_reimbursement
        
        # Step 7: Apply cluster-specific multiplier
        adjusted_total = base_total * cluster_config['multiplier']
        
        # Step 8: Add systematic variation (±1-2% to match observed noise)
        # Use deterministic noise based on inputs for consistency
        noise_seed = int((trip_duration_days * 1000 + miles_traveled * 10 + total_receipts_amount * 100) % 1000)
        random.seed(noise_seed)
        noise = random.uniform(-0.015, 0.015)
        final_total = adjusted_total * (1 + noise)
        
        # Step 9: Apply cents bug for receipts ending in .49 or .99
        if self._has_magic_cents(total_receipts_amount):
            final_total += random.uniform(3, 7)  # Small bonus
        
        return round(final_total, 2)
    
    def _classify_trip(self, days: int, miles: float, receipts: float) -> Tuple[str, dict]:
        """Classify trip into one of the discovered clusters."""
        if days == 0:
            return 'standard', self.cluster_configs['standard']
        
        miles_per_day = miles / days
        receipts_per_day = receipts / days
        
        # High-mileage road warrior (Cluster 0)
        if miles_per_day > 350 and days <= 3:
            return 'road_warrior', self.cluster_configs['road_warrior']
        
        # Optimal business travel (Cluster 1 - Kevin's sweet spot)
        if (days == 5 and 170 <= miles_per_day <= 230 and receipts_per_day < 110) or \
           (4 <= days <= 6 and 180 <= miles_per_day <= 220 and receipts_per_day < 100):
            return 'optimal_business', self.cluster_configs['optimal_business']
        
        # Extended low-activity trips (Cluster 2)
        if days >= 7 and miles_per_day < 120:
            return 'extended_low', self.cluster_configs['extended_low']
        
        # High spending trips (Cluster 5)
        if receipts_per_day > 140 or (receipts > 800 and days <= 3):
            return 'high_spend', self.cluster_configs['high_spend']
        
        # Local trips (Cluster 4)
        if miles < 60 and days <= 2 and receipts_per_day < 50:
            return 'local', self.cluster_configs['local']
        
        # Default: standard business travel (Cluster 3)
        return 'standard', self.cluster_configs['standard']
    
    def _calculate_per_diem(self, days: int, cluster_config: dict) -> float:
        """Calculate per diem with 5-day bonus and cluster adjustment."""
        base = self.base_per_diem * days * cluster_config['per_diem_adj']
        
        # Apply 5-day bonus (discovered pattern)
        if days == 5:
            base *= (1 + self.five_day_bonus_rate)
        
        return base
    
    def _calculate_mileage(self, miles: float, cluster_config: dict) -> float:
        """Calculate tiered mileage reimbursement."""
        total = 0.0
        remaining_miles = miles
        prev_tier = 0
        
        for tier_limit, rate in self.mileage_tiers:
            tier_miles = min(remaining_miles, tier_limit - prev_tier)
            if tier_miles <= 0:
                break
            
            # Apply cluster-specific mileage adjustment
            adjusted_rate = rate * cluster_config['mileage_adj']
            total += tier_miles * adjusted_rate
            remaining_miles -= tier_miles
            prev_tier = tier_limit
        
        return total
    
    def _calculate_efficiency_adjustment(self, days: int, miles: float, base_amount: float) -> float:
        """Calculate efficiency bonus or penalty."""
        if days == 0:
            return 0.0
        
        miles_per_day = miles / days
        
        # Sweet spot bonus (180-220 miles/day)
        if self.efficiency_sweet_spot[0] <= miles_per_day <= self.efficiency_sweet_spot[1]:
            return base_amount * self.efficiency_bonus_rate
        
        # High efficiency penalty (>300 miles/day - system thinks you're not doing business)
        if miles_per_day > 300:
            penalty = (miles_per_day - 300) * 0.0001 * base_amount
            return -min(penalty, base_amount * 0.05)  # Cap at 5% penalty
        
        return 0.0
    
    def _calculate_receipt_reimbursement(self, receipts: float, days: int, cluster_config: dict) -> float:
        """Calculate receipt reimbursement with penalties and coverage rules."""
        if receipts == 0:
            return 0.0
        
        # Apply cluster-specific receipt adjustment
        adj_factor = cluster_config['receipt_adj']
        
        # Small receipt penalty
        if receipts < self.small_receipt_threshold:
            # Extra penalty for very small amounts
            if receipts < 20:
                return receipts * 0.65 * adj_factor
            return receipts * self.small_receipt_penalty_rate * adj_factor
        
        # Medium receipt range (optimal)
        if self.medium_receipt_range[0] <= receipts <= self.medium_receipt_range[1]:
            return receipts * self.medium_receipt_coverage * adj_factor
        
        # High receipt diminishing returns
        if receipts > self.high_receipt_threshold:
            # First $600 at base rate
            base_amount = self.high_receipt_threshold * self.high_receipt_base_coverage
            # Remaining at diminishing rate
            excess = receipts - self.high_receipt_threshold
            # Coverage decreases with excess amount
            excess_coverage = 0.7 * (1 - self.high_receipt_excess_decay * excess)
            excess_coverage = max(0.3, excess_coverage)  # Floor at 30%
            return (base_amount + (excess * excess_coverage)) * adj_factor
        
        # Default coverage
        return receipts * self.medium_receipt_coverage * adj_factor
    
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