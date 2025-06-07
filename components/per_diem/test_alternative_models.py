#!/usr/bin/env python3
"""
Test Alternative Per Diem Models

Based on validation concerns, test these alternative models:
1. Variable rate by trip length (not flat)
2. Base rate lower than $100 with receipt-dependent adjustments
3. Per diem that decreases with trip length
4. Per diem that's actually part of a combined calculation
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from components.mileage.mileage import MileageCalculator
from components.bonuses.bonuses import BonusCalculator
from components.bugs.bugs import BugProcessor


def test_decreasing_per_diem_model():
    """Test if per diem decreases with trip length."""
    print("=== MODEL 1: DECREASING PER DIEM BY TRIP LENGTH ===")
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    mileage_calc = MileageCalculator()
    bonus_calc = BonusCalculator()
    bug_proc = BugProcessor()
    
    # Group cases by trip length
    by_days = {}
    for case in cases:
        days = case['input']['trip_duration_days']
        if days not in by_days:
            by_days[days] = []
        
        # Calculate known components
        mileage = mileage_calc.calculate(case['input']['miles_traveled'])
        bonuses = bonus_calc.calculate_all_bonuses(
            days, 
            case['input']['miles_traveled'], 
            case['input']['total_receipts_amount']
        )
        bugs = bug_proc.apply_bugs(case['input']['total_receipts_amount'])
        
        # Assume receipts are 85% covered
        receipt_estimate = case['input']['total_receipts_amount'] * 0.85
        
        # What's left should be per diem
        per_diem_estimate = case['expected_output'] - mileage - bonuses - bugs - receipt_estimate
        per_day_rate = per_diem_estimate / days if days > 0 else 0
        
        by_days[days].append({
            'per_diem_total': per_diem_estimate,
            'per_day_rate': per_day_rate,
            'reimbursement': case['expected_output']
        })
    
    # Analyze pattern
    print(f"{'Days':>4} | {'Count':>6} | {'Avg Per Diem':>12} | {'Per Day Rate':>12} | {'Std Dev':>10}")
    print("-" * 60)
    
    rates_by_length = []
    for days in sorted(by_days.keys()):
        if len(by_days[days]) >= 5:
            avg_total = sum(c['per_diem_total'] for c in by_days[days]) / len(by_days[days])
            avg_rate = sum(c['per_day_rate'] for c in by_days[days]) / len(by_days[days])
            std_dev = (sum((c['per_day_rate'] - avg_rate)**2 for c in by_days[days]) / len(by_days[days])) ** 0.5
            
            print(f"{days:4d} | {len(by_days[days]):6d} | ${avg_total:11.2f} | ${avg_rate:11.2f} | ${std_dev:9.2f}")
            rates_by_length.append((days, avg_rate))
    
    # Check if rates decrease
    print("\nTrend analysis:")
    for i in range(1, len(rates_by_length)):
        prev_days, prev_rate = rates_by_length[i-1]
        curr_days, curr_rate = rates_by_length[i]
        change = curr_rate - prev_rate
        print(f"  {prev_days} → {curr_days} days: ${change:+.2f}/day")


def test_tiered_per_diem_model():
    """Test if per diem has tiers like mileage."""
    print("\n=== MODEL 2: TIERED PER DIEM ===")
    
    # Hypothetical tiers
    tiers = [
        (3, 120),   # 1-3 days: $120/day
        (7, 100),   # 4-7 days: $100/day  
        (14, 80),   # 8-14 days: $80/day
    ]
    
    def calculate_tiered_per_diem(days):
        total = 0
        remaining_days = days
        prev_tier = 0
        
        for tier_limit, rate in tiers:
            tier_days = min(remaining_days, tier_limit - prev_tier)
            if tier_days <= 0:
                break
            total += tier_days * rate
            remaining_days -= tier_days
            prev_tier = tier_limit
        
        return total
    
    # Test this model
    print("\nTiered calculation examples:")
    for test_days in [1, 3, 5, 7, 10, 14]:
        tiered = calculate_tiered_per_diem(test_days)
        flat = test_days * 100
        diff = tiered - flat
        print(f"  {test_days:2d} days: Tiered=${tiered:4.0f}, Flat=${flat:4.0f}, Diff=${diff:+4.0f}")
    
    # Test against actual data
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)[:100]
    
    total_error_tiered = 0
    total_error_flat = 0
    
    for case in cases:
        days = case['input']['trip_duration_days']
        actual = case['expected_output']
        
        # Very rough estimate (just for comparison)
        tiered_estimate = calculate_tiered_per_diem(days) + case['input']['miles_traveled'] * 0.5
        flat_estimate = days * 100 + case['input']['miles_traveled'] * 0.5
        
        total_error_tiered += abs(actual - tiered_estimate)
        total_error_flat += abs(actual - flat_estimate)
    
    print(f"\nError comparison (first 100 cases):")
    print(f"  Tiered model avg error: ${total_error_tiered/len(cases):.2f}")
    print(f"  Flat model avg error: ${total_error_flat/len(cases):.2f}")


def test_base_plus_factors_model():
    """Test if per diem = base + adjustments based on other factors."""
    print("\n=== MODEL 3: BASE + ADJUSTMENT FACTORS ===")
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Calculate implied per diem for different scenarios
    scenarios = {
        'low_miles_low_receipts': [],
        'low_miles_high_receipts': [],
        'high_miles_low_receipts': [],
        'high_miles_high_receipts': []
    }
    
    mileage_calc = MileageCalculator()
    
    for case in cases[:500]:  # First 500 cases
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        
        miles_per_day = miles / days if days > 0 else 0
        receipts_per_day = receipts / days if days > 0 else 0
        
        # Categorize
        miles_category = 'high_miles' if miles_per_day > 100 else 'low_miles'
        receipts_category = 'high_receipts' if receipts_per_day > 100 else 'low_receipts'
        scenario = f"{miles_category}_{receipts_category}"
        
        # Estimate per diem
        mileage_pay = mileage_calc.calculate(miles)
        receipt_pay = receipts * 0.85  # Rough estimate
        
        implied_per_diem = case['expected_output'] - mileage_pay - receipt_pay
        implied_per_day = implied_per_diem / days if days > 0 else 0
        
        scenarios[scenario].append({
            'days': days,
            'per_day': implied_per_day,
            'total': implied_per_diem
        })
    
    # Analyze each scenario
    print("\nImplied per-day rates by scenario:")
    print(f"{'Scenario':30} | {'Count':>6} | {'Avg Rate':>10} | {'Std Dev':>10}")
    print("-" * 65)
    
    for scenario, data in scenarios.items():
        if data:
            rates = [d['per_day'] for d in data]
            avg_rate = sum(rates) / len(rates)
            std_dev = (sum((r - avg_rate)**2 for r in rates) / len(rates)) ** 0.5
            
            print(f"{scenario:30} | {len(data):6d} | ${avg_rate:9.2f} | ${std_dev:9.2f}")
    
    print("\nConclusion: Per diem appears to vary significantly based on other factors!")


def test_no_per_diem_model():
    """Test if there's actually no separate per diem component."""
    print("\n=== MODEL 4: NO SEPARATE PER DIEM ===")
    print("What if 'per diem' is just emergent from other calculations?")
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Test a model with no per diem, just:
    # - Mileage (tiered)
    # - Receipt coverage (with penalties)
    # - Trip length multiplier on total
    
    errors = []
    
    for case in cases[:200]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        actual = case['expected_output']
        
        # Calculate without per diem
        mileage_calc = MileageCalculator()
        mileage_pay = mileage_calc.calculate(miles)
        
        # Receipt coverage with trip-length adjustment
        receipt_base = receipts * 0.85
        receipt_adjusted = receipt_base * (1 + days * 0.02)  # 2% more per day
        
        # Trip length multiplier on total
        base_total = mileage_pay + receipt_adjusted
        
        # Different multipliers by trip length
        if days <= 2:
            multiplier = 1.5
        elif days <= 5:
            multiplier = 1.3
        elif days <= 7:
            multiplier = 1.2
        else:
            multiplier = 1.1
        
        predicted = base_total * multiplier
        error = abs(predicted - actual)
        errors.append(error)
        
        if case == cases[0]:  # Show first example
            print(f"\nExample calculation (first case):")
            print(f"  Days: {days}, Miles: {miles}, Receipts: ${receipts:.2f}")
            print(f"  Mileage pay: ${mileage_pay:.2f}")
            print(f"  Receipt adjusted: ${receipt_adjusted:.2f}")
            print(f"  Base total: ${base_total:.2f}")
            print(f"  Multiplier: {multiplier}")
            print(f"  Predicted: ${predicted:.2f}")
            print(f"  Actual: ${actual:.2f}")
            print(f"  Error: ${error:.2f}")
    
    avg_error = sum(errors) / len(errors)
    print(f"\nAverage error for no-per-diem model: ${avg_error:.2f}")


def main():
    """Run all alternative model tests."""
    print("=== TESTING ALTERNATIVE PER DIEM MODELS ===\n")
    
    test_decreasing_per_diem_model()
    test_tiered_per_diem_model()
    test_base_plus_factors_model()
    test_no_per_diem_model()
    
    print("\n=== SUMMARY ===")
    print("Evidence suggests per diem is NOT a simple $100/day flat rate.")
    print("Most likely scenarios:")
    print("1. Per diem varies based on trip length (decreasing rate)")
    print("2. Per diem interacts strongly with other factors")
    print("3. What we call 'per diem' might be emergent from complex rules")
    print("\nRecommendation: Test these models with full system integration")


if __name__ == "__main__":
    main()