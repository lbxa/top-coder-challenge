#!/usr/bin/env python3
"""
Analyze calculation errors to identify patterns
"""

import json
from calculator_v2 import calculate_reimbursement

# Load cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Calculate errors
errors = []
for i, case in enumerate(cases):
    inp = case['input']
    expected = case['expected_output']
    calculated = calculate_reimbursement(
        inp['trip_duration_days'],
        inp['miles_traveled'],
        inp['total_receipts_amount']
    )
    error = abs(calculated - expected)
    
    errors.append({
        'case_id': i,
        'input': inp,
        'expected': expected,
        'calculated': calculated,
        'error': error,
        'error_pct': error / expected * 100 if expected > 0 else 0
    })

# Sort by error
errors.sort(key=lambda x: x['error'], reverse=True)

print("=== TOP 20 ERRORS ===")
for i, e in enumerate(errors[:20]):
    inp = e['input']
    print(f"\n{i+1}. Case {e['case_id']}: Error ${e['error']:.2f} ({e['error_pct']:.1f}%)")
    print(f"   Input: {inp['trip_duration_days']}d, {inp['miles_traveled']:.1f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"   Expected: ${e['expected']:.2f}, Calculated: ${e['calculated']:.2f}")
    
    # Check patterns
    cents = round((inp['total_receipts_amount'] * 100) % 100)
    if cents in [49, 99]:
        print(f"   → Has cents bug (.{cents:02d})")
    
    # Analyze what went wrong
    if e['calculated'] > e['expected']:
        print("   → OVERESTIMATED")
    else:
        print("   → UNDERESTIMATED")

# Analyze by trip duration
print("\n\n=== ERROR ANALYSIS BY TRIP DURATION ===")
for days in range(1, 15):
    day_errors = [e for e in errors if e['input']['trip_duration_days'] == days]
    if day_errors:
        avg_error = sum(e['error'] for e in day_errors) / len(day_errors)
        avg_pct = sum(e['error_pct'] for e in day_errors) / len(day_errors)
        overest = sum(1 for e in day_errors if e['calculated'] > e['expected'])
        
        print(f"\n{days} days: {len(day_errors)} cases")
        print(f"  Avg error: ${avg_error:.2f} ({avg_pct:.1f}%)")
        print(f"  Overestimated: {overest}/{len(day_errors)} cases")
        
        # Show worst case
        worst = max(day_errors, key=lambda x: x['error'])
        print(f"  Worst: Case {worst['case_id']}, error ${worst['error']:.2f}")

# Analyze by receipt range
print("\n\n=== ERROR ANALYSIS BY RECEIPT RANGE ===")
ranges = [(0, 50), (50, 100), (100, 200), (200, 500), (500, 1000), (1000, 2000), (2000, 5000)]
for low, high in ranges:
    range_errors = [e for e in errors if low <= e['input']['total_receipts_amount'] < high]
    if range_errors:
        avg_error = sum(e['error'] for e in range_errors) / len(range_errors)
        avg_pct = sum(e['error_pct'] for e in range_errors) / len(range_errors)
        
        print(f"\n${low}-${high}: {len(range_errors)} cases")
        print(f"  Avg error: ${avg_error:.2f} ({avg_pct:.1f}%)")

# Specific pattern: 1-day trips with medium receipts
print("\n\n=== 1-DAY TRIP ANALYSIS ===")
one_day_trips = [c for c in cases if c['input']['trip_duration_days'] == 1]
print(f"Total 1-day trips: {len(one_day_trips)}")

# Group by receipt range
for low, high in [(0, 100), (100, 500), (500, 1000), (1000, 2000), (2000, 5000)]:
    range_trips = [t for t in one_day_trips if low <= t['input']['total_receipts_amount'] < high]
    if range_trips:
        avg_expected = sum(t['expected_output'] for t in range_trips) / len(range_trips)
        
        # Calculate what we're producing
        avg_calculated = 0
        for t in range_trips:
            calc = calculate_reimbursement(1, t['input']['miles_traveled'], t['input']['total_receipts_amount'])
            avg_calculated += calc
        avg_calculated /= len(range_trips)
        
        print(f"\n  Receipts ${low}-${high}: {len(range_trips)} cases")
        print(f"    Avg expected: ${avg_expected:.2f}")
        print(f"    Avg calculated: ${avg_calculated:.2f}")
        print(f"    Difference: ${avg_calculated - avg_expected:.2f}")

print("\n\n=== KEY INSIGHTS ===")
print("1. Major overestimation on 1-day trips with $100-500 receipts")
print("2. Need to reduce base per diem for 1-day trips")
print("3. Receipt multipliers may be too high for certain ranges")