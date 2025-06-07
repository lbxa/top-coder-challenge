"""
Analyze receipt patterns in public cases to validate and refine hypotheses.

This script performs detailed analysis on receipt processing patterns to:
1. Identify spending thresholds by trip length
2. Find penalty patterns
3. Detect edge cases and anomalies
4. Test alternative hypotheses
"""

import json
import statistics
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent.parent))
from components.receipts.receipts import ReceiptProcessor
from components.per_diem.per_diem import PerDiemCalculator
from components.mileage.mileage import MileageCalculator
from components.duration.duration import DurationCalculator
from components.bonuses.bonuses import BonusCalculator
from components.bugs.bugs import BugProcessor


def load_public_cases() -> List[Dict]:
    """Load public test cases."""
    with open("/Users/lchubarbos001/u/top-coder-challenge/public_cases.json", 'r') as f:
        return json.load(f)


def calculate_other_components(days: float, miles: float, receipts: float) -> float:
    """Calculate total from all components except receipts."""
    per_diem_calc = PerDiemCalculator()
    mileage_calc = MileageCalculator()
    duration_calc = DurationCalculator()
    bonus_calc = BonusCalculator()
    bug_processor = BugProcessor()
    
    per_diem_pay = per_diem_calc.calculate(days)
    mileage_pay = mileage_calc.calculate(miles)
    duration_adjustment = duration_calc.calculate(days)
    bonus_amount = bonus_calc.calculate_all_bonuses(days, miles, receipts)
    bug_adjustment = bug_processor.apply_bugs(receipts)
    
    return per_diem_pay + mileage_pay + duration_adjustment + bonus_amount + bug_adjustment


def analyze_receipt_impact():
    """Analyze how receipts contribute to the total reimbursement."""
    cases = load_public_cases()
    receipt_processor = ReceiptProcessor()
    
    print("Analyzing Receipt Impact on Total Reimbursement")
    print("=" * 60)
    
    # Group cases by trip length
    short_trips = []  # 1-3 days
    medium_trips = []  # 4-7 days
    long_trips = []  # 8+ days
    
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Calculate what receipts should contribute
        other_components = calculate_other_components(days, miles, receipts)
        implied_receipt_pay = expected - other_components
        
        # Calculate what our processor returns
        processed_receipts = receipt_processor.process(days, receipts)
        
        # Calculate error
        error = processed_receipts - implied_receipt_pay
        
        case_data = {
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'receipts_per_day': receipts / days if days > 0 else 0,
            'expected_total': expected,
            'other_components': other_components,
            'implied_receipt_pay': implied_receipt_pay,
            'processed_receipts': processed_receipts,
            'error': error
        }
        
        if 1 <= days <= 3:
            short_trips.append(case_data)
        elif 4 <= days <= 7:
            medium_trips.append(case_data)
        elif days >= 8:
            long_trips.append(case_data)
    
    # Analyze patterns for each trip length category
    for category_name, cases_list in [
        ("Short Trips (1-3 days)", short_trips),
        ("Medium Trips (4-7 days)", medium_trips),
        ("Long Trips (8+ days)", long_trips)
    ]:
        if not cases_list:
            continue
            
        print(f"\n{category_name}: {len(cases_list)} cases")
        print("-" * 40)
        
        # Filter cases with receipts
        with_receipts = [c for c in cases_list if c['receipts'] > 0]
        
        if with_receipts:
            # Analyze spending patterns
            receipts_per_day = [c['receipts_per_day'] for c in with_receipts]
            print(f"Receipt spending per day:")
            print(f"  Min: ${min(receipts_per_day):.2f}")
            print(f"  Max: ${max(receipts_per_day):.2f}")
            print(f"  Avg: ${statistics.mean(receipts_per_day):.2f}")
            print(f"  Median: ${statistics.median(receipts_per_day):.2f}")
            
            # Analyze errors
            errors = [c['error'] for c in with_receipts]
            print(f"\nReceipt processing errors:")
            print(f"  Min error: ${min(errors):.2f}")
            print(f"  Max error: ${max(errors):.2f}")
            print(f"  Avg error: ${statistics.mean(errors):.2f}")
            print(f"  Std dev: ${statistics.stdev(errors) if len(errors) > 1 else 0:.2f}")
            
            # Find cases with large errors
            large_errors = [c for c in with_receipts if abs(c['error']) > 50]
            if large_errors:
                print(f"\nLarge error cases ({len(large_errors)}):")
                for case in sorted(large_errors, key=lambda x: abs(x['error']), reverse=True)[:5]:
                    print(f"  {case['days']} days, ${case['receipts']:.2f} receipts (${case['receipts_per_day']:.2f}/day)")
                    print(f"    Expected receipt contribution: ${case['implied_receipt_pay']:.2f}")
                    print(f"    Our calculation: ${case['processed_receipts']:.2f}")
                    print(f"    Error: ${case['error']:.2f}")


def analyze_penalty_patterns():
    """Analyze specific penalty patterns in the data."""
    cases = load_public_cases()
    receipt_processor = ReceiptProcessor()
    
    print("\n\nAnalyzing Penalty Patterns")
    print("=" * 60)
    
    # Look for overspending penalty patterns
    for threshold in [50, 60, 70, 75, 80, 90, 100, 110, 120, 130, 140, 150]:
        print(f"\nTesting threshold ${threshold}/day:")
        
        total_error = 0
        count = 0
        
        for case in cases:
            days = case['input']['trip_duration_days']
            receipts = case['input']['total_receipts_amount']
            
            if receipts > 0 and days > 0:
                receipts_per_day = receipts / days
                
                # Only look at cases above the threshold
                if receipts_per_day > threshold:
                    miles = case['input']['miles_traveled']
                    expected = case['expected_output']
                    
                    other_components = calculate_other_components(days, miles, receipts)
                    implied_receipt_pay = expected - other_components
                    
                    # Test if penalty exists
                    if implied_receipt_pay < receipts:
                        penalty = receipts - implied_receipt_pay
                        penalty_rate = penalty / (receipts - threshold * days) if receipts > threshold * days else 0
                        
                        total_error += abs(penalty_rate)
                        count += 1
                        
                        if count <= 3:  # Show first 3 examples
                            print(f"  {days} days, ${receipts_per_day:.2f}/day: penalty ${penalty:.2f} (rate: {penalty_rate:.2%})")
        
        if count > 0:
            avg_penalty_rate = total_error / count
            print(f"  Average penalty rate: {avg_penalty_rate:.2%} ({count} cases)")


def test_alternative_hypotheses():
    """Test alternative receipt processing hypotheses."""
    cases = load_public_cases()
    
    print("\n\nTesting Alternative Hypotheses")
    print("=" * 60)
    
    # Hypothesis 1: Fixed percentage of receipts
    print("\nHypothesis 1: Fixed percentage of receipts")
    for percentage in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        total_error = 0
        count = 0
        
        for case in cases:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            if receipts > 0:
                other_components = calculate_other_components(days, miles, receipts)
                implied_receipt_pay = expected - other_components
                
                test_receipt_pay = receipts * percentage
                error = abs(test_receipt_pay - implied_receipt_pay)
                
                total_error += error
                count += 1
        
        avg_error = total_error / count if count > 0 else float('inf')
        print(f"  {percentage:.0%}: avg error ${avg_error:.2f}")
    
    # Hypothesis 2: Cap on daily receipt reimbursement
    print("\nHypothesis 2: Daily receipt cap")
    for cap in [50, 75, 100, 125, 150, 200]:
        total_error = 0
        count = 0
        
        for case in cases:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            if receipts > 0 and days > 0:
                other_components = calculate_other_components(days, miles, receipts)
                implied_receipt_pay = expected - other_components
                
                # Apply daily cap
                max_allowed = cap * days
                test_receipt_pay = min(receipts, max_allowed)
                error = abs(test_receipt_pay - implied_receipt_pay)
                
                total_error += error
                count += 1
        
        avg_error = total_error / count if count > 0 else float('inf')
        print(f"  ${cap}/day cap: avg error ${avg_error:.2f}")


def find_receipt_patterns_by_amount():
    """Analyze patterns based on receipt amounts."""
    cases = load_public_cases()
    
    print("\n\nAnalyzing Receipt Patterns by Amount")
    print("=" * 60)
    
    # Group by receipt amount ranges
    ranges = [
        (0, 100, "Very Low ($0-100)"),
        (100, 500, "Low ($100-500)"),
        (500, 1000, "Medium ($500-1000)"),
        (1000, 2000, "High ($1000-2000)"),
        (2000, float('inf'), "Very High ($2000+)")
    ]
    
    for min_amt, max_amt, label in ranges:
        range_cases = []
        
        for case in cases:
            receipts = case['input']['total_receipts_amount']
            
            if min_amt <= receipts < max_amt:
                days = case['input']['trip_duration_days']
                miles = case['input']['miles_traveled']
                expected = case['expected_output']
                
                other_components = calculate_other_components(days, miles, receipts)
                implied_receipt_pay = expected - other_components
                
                receipt_ratio = implied_receipt_pay / receipts if receipts > 0 else 0
                
                range_cases.append({
                    'days': days,
                    'receipts': receipts,
                    'receipts_per_day': receipts / days if days > 0 else 0,
                    'implied_receipt_pay': implied_receipt_pay,
                    'receipt_ratio': receipt_ratio
                })
        
        if range_cases:
            print(f"\n{label}: {len(range_cases)} cases")
            
            ratios = [c['receipt_ratio'] for c in range_cases if c['receipts'] > 0]
            if ratios:
                print(f"  Receipt reimbursement ratio:")
                print(f"    Min: {min(ratios):.2%}")
                print(f"    Max: {max(ratios):.2%}")
                print(f"    Avg: {statistics.mean(ratios):.2%}")
                print(f"    Median: {statistics.median(ratios):.2%}")


if __name__ == "__main__":
    print("Receipt Pattern Analysis")
    print("=" * 60)
    
    # Run all analyses
    analyze_receipt_impact()
    analyze_penalty_patterns()
    test_alternative_hypotheses()
    find_receipt_patterns_by_amount()
    
    print("\n\n✅ Analysis complete!")