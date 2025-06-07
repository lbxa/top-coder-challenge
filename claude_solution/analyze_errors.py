#!/usr/bin/env python3
"""Analyze high-error cases to find patterns."""

import json
from reimbursement_calculator_optimized import calculate_reimbursement

def analyze_high_errors():
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # High error cases from eval.sh output
    high_error_cases = [
        (936, 10, 174, 1991.96, 1542.40),  # Expected $1542.40, Got $2310.16
        (895, 12, 18, 2461.37, 1556.78),   # Expected $1556.78, Got $2281.31
        (876, 13, 8, 78.44, 713.71),       # Expected $713.71, Got $1434.20
        (346, 12, 81, 2485.34, 1589.65),   # Expected $1589.65, Got $2305.05
        (318, 13, 1034, 2477.98, 1842.24), # Expected $1842.24, Got $2554.22
    ]
    
    print("=== HIGH ERROR CASE ANALYSIS ===\n")
    
    for case_id, days, miles, receipts, expected in high_error_cases:
        predicted = calculate_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        
        # Calculate metrics
        mpd = miles / days if days > 0 else 0
        rpd = receipts / days if days > 0 else 0
        receipt_ratio = expected / receipts if receipts > 0 else 0
        
        print(f"Case {case_id}: {days}d, {miles}mi, ${receipts:.2f}")
        print(f"  Expected: ${expected:.2f}, Got: ${predicted:.2f}, Error: ${error:.2f}")
        print(f"  MPD: {mpd:.1f}, RPD: ${rpd:.1f}")
        print(f"  Receipt ratio: {receipt_ratio:.3f}")
        print(f"  Cents: {int(receipts * 100) % 100}")
        print()
    
    # Analyze patterns in all cases with similar characteristics
    print("\n=== PATTERN ANALYSIS ===\n")
    
    # Pattern 1: Long trips (10-14 days) with high receipts
    long_high_receipt = []
    for i, case in enumerate(cases):
        d = case['input']['trip_duration_days']
        r = case['input']['total_receipts_amount']
        if 10 <= d <= 14 and r > 1500:
            predicted = calculate_reimbursement(d, case['input']['miles_traveled'], r)
            actual = case['expected_output']
            error = abs(predicted - actual)
            ratio = actual / r if r > 0 else 0
            long_high_receipt.append((d, r, ratio, error))
    
    if long_high_receipt:
        avg_ratio = sum(x[2] for x in long_high_receipt) / len(long_high_receipt)
        avg_error = sum(x[3] for x in long_high_receipt) / len(long_high_receipt)
        print(f"Long trips (10-14d) with high receipts (>$1500):")
        print(f"  Count: {len(long_high_receipt)}")
        print(f"  Avg receipt ratio: {avg_ratio:.3f}")
        print(f"  Avg error: ${avg_error:.2f}")
    
    # Pattern 2: Long trips with very low mileage
    long_low_miles = []
    for i, case in enumerate(cases):
        d = case['input']['trip_duration_days']
        m = case['input']['miles_traveled']
        if d >= 10 and m < 100:
            predicted = calculate_reimbursement(d, m, case['input']['total_receipts_amount'])
            actual = case['expected_output']
            error = abs(predicted - actual)
            long_low_miles.append((d, m, actual, predicted, error))
    
    if long_low_miles:
        avg_error = sum(x[4] for x in long_low_miles) / len(long_low_miles)
        print(f"\nLong trips (>=10d) with low mileage (<100mi):")
        print(f"  Count: {len(long_low_miles)}")
        print(f"  Avg error: ${avg_error:.2f}")
        for d, m, actual, pred, err in sorted(long_low_miles, key=lambda x: x[4], reverse=True)[:5]:
            print(f"    {d}d, {m}mi: Expected ${actual:.2f}, Got ${pred:.2f}, Error ${err:.2f}")

if __name__ == "__main__":
    analyze_high_errors()