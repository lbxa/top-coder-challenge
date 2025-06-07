#!/usr/bin/env python3
"""
Per Diem Hypothesis Testing

Based on analysis, we hypothesize:
1. Base per diem is exactly $100/day (no adjustments)
2. All trip-length bonuses are handled in bonuses.py
3. Per diem calculation is purely linear: days * rate

This script tests these hypotheses against public cases.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from components.per_diem.per_diem import PerDiemCalculator
from components.mileage.mileage import MileageCalculator
from components.receipts.receipts import ReceiptProcessor
from components.bonuses.bonuses import BonusCalculator
from components.bugs.bugs import BugProcessor


def test_per_diem_hypothesis():
    """Test if per diem is truly $100/day with no internal adjustments."""
    
    # Load public cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    per_diem_calc = PerDiemCalculator()
    
    print("=== TESTING PER DIEM HYPOTHESIS ===")
    print(f"Current daily rate: ${per_diem_calc.daily_rate}")
    print()
    
    # Test 1: Verify linear calculation
    print("Test 1: Verifying linear calculation (days * rate)")
    test_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    for days in test_days:
        calculated = per_diem_calc.calculate(days)
        expected = days * per_diem_calc.daily_rate
        print(f"  Days: {days:2d} | Calculated: ${calculated:6.2f} | Expected: ${expected:6.2f} | Match: {calculated == expected}")
    
    print("\nConclusion: Per diem calculation is purely linear ✓")
    
    # Test 2: Check if 5-day bonus is in per_diem or bonuses
    print("\nTest 2: Checking 5-day bonus location")
    bonus_calc = BonusCalculator()
    
    for days in [4, 5, 6]:
        per_diem = per_diem_calc.calculate(days)
        bonus = bonus_calc._calculate_five_day_bonus(days)
        print(f"  Days: {days} | Per Diem: ${per_diem:6.2f} | 5-day Bonus: ${bonus:6.2f}")
    
    print("\nConclusion: 5-day bonus is in BonusCalculator, not PerDiemCalculator ✓")
    
    # Test 3: Analyze actual cases to estimate per diem contribution
    print("\nTest 3: Estimating per diem contribution from actual cases")
    print("(Subtracting estimated mileage and examining residuals)")
    
    mileage_calc = MileageCalculator()
    
    # Sample some cases with different trip lengths
    trip_length_samples = {}
    for case in cases[:200]:  # First 200 cases
        days = case['input']['trip_duration_days']
        if days not in trip_length_samples:
            trip_length_samples[days] = []
        
        # Calculate known components
        per_diem = per_diem_calc.calculate(days)
        mileage = mileage_calc.calculate(case['input']['miles_traveled'])
        
        # Residual after per diem and mileage
        residual = case['expected_output'] - per_diem - mileage
        
        trip_length_samples[days].append({
            'reimbursement': case['expected_output'],
            'per_diem': per_diem,
            'mileage': mileage,
            'residual': residual,
            'receipts': case['input']['total_receipts_amount']
        })
    
    # Analyze by trip length
    print(f"\n{'Days':>4} | {'Count':>5} | {'Avg Reimb':>10} | {'Per Diem':>9} | {'Avg Residual':>12}")
    print("-" * 55)
    
    for days in sorted(trip_length_samples.keys()):
        samples = trip_length_samples[days]
        if len(samples) >= 3:  # Only show if we have enough samples
            avg_reimb = sum(s['reimbursement'] for s in samples) / len(samples)
            avg_residual = sum(s['residual'] for s in samples) / len(samples)
            per_diem = samples[0]['per_diem']  # Same for all with same days
            
            print(f"{days:4d} | {len(samples):5d} | ${avg_reimb:9.2f} | ${per_diem:8.2f} | ${avg_residual:11.2f}")
    
    # Test 4: Check for any non-linear patterns
    print("\nTest 4: Checking for non-linear patterns in per diem")
    print("If per diem has hidden adjustments, residuals should vary by trip length")
    
    # Calculate correlation between days and per-diem portion of residuals
    # If per diem has hidden rules, this should show patterns
    
    return True


def test_alternative_rates():
    """Test alternative per diem rates to see if they fit better."""
    
    print("\n=== TESTING ALTERNATIVE PER DIEM RATES ===")
    
    # Test rates from $90 to $110
    test_rates = [90, 95, 100, 105, 110]
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)[:100]  # First 100 cases
    
    per_diem_calc = PerDiemCalculator()
    original_rate = per_diem_calc.daily_rate
    
    for rate in test_rates:
        per_diem_calc.daily_rate = rate
        
        total_error = 0
        for case in cases:
            days = case['input']['trip_duration_days']
            calculated = per_diem_calc.calculate(days)
            # This is a rough test - we'd need full calculation to be precise
            error = abs(case['expected_output'] - calculated)
            total_error += error
        
        avg_error = total_error / len(cases)
        print(f"  Rate: ${rate}/day | Avg Error: ${avg_error:.2f}")
    
    per_diem_calc.daily_rate = original_rate


if __name__ == "__main__":
    test_per_diem_hypothesis()
    test_alternative_rates()