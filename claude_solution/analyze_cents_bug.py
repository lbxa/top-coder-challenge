#!/usr/bin/env python3
"""Analyze the cents bug pattern in detail"""

import json

with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Find all cases with .49 or .99 endings
special_cases = []
for i, case in enumerate(cases):
    receipts = case['input']['total_receipts_amount']
    cents = round((receipts * 100) % 100)
    if cents in [49, 99]:
        special_cases.append({
            'index': i,
            'inputs': case['input'],
            'expected': case['expected_output'],
            'cents': cents
        })

print(f"=== CENTS BUG ANALYSIS ===")
print(f"Found {len(special_cases)} cases with .49 or .99 endings")

# Sort by receipt amount
special_cases.sort(key=lambda x: x['inputs']['total_receipts_amount'])

print("\nAll special cases:")
for sc in special_cases:
    inp = sc['inputs']
    print(f"\nCase {sc['index']}:")
    print(f"  Inputs: {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"  Expected: ${sc['expected']:.2f}")
    print(f"  Cents: .{sc['cents']:02d}")
    
    # Compare to what it might be without the bug
    # Look for similar cases without .49/.99
    similar_normal = []
    for case in cases:
        other_inp = case['input']
        other_cents = round((other_inp['total_receipts_amount'] * 100) % 100)
        if other_cents not in [49, 99]:
            # Similar if within 10% on all inputs
            if (abs(other_inp['trip_duration_days'] - inp['trip_duration_days']) <= 1 and
                abs(other_inp['miles_traveled'] - inp['miles_traveled']) / (inp['miles_traveled'] + 1) < 0.2 and
                abs(other_inp['total_receipts_amount'] - inp['total_receipts_amount']) / inp['total_receipts_amount'] < 0.2):
                similar_normal.append(case['expected_output'])
    
    if similar_normal:
        avg_normal = sum(similar_normal) / len(similar_normal)
        print(f"  Similar normal cases average: ${avg_normal:.2f} ({len(similar_normal)} cases)")
        print(f"  Ratio: {sc['expected'] / avg_normal:.3f}")

# Group by trip duration
print("\n=== BY TRIP DURATION ===")
for days in range(1, 15):
    day_cases = [sc for sc in special_cases if sc['inputs']['trip_duration_days'] == days]
    if day_cases:
        reimbs = [dc['expected'] for dc in day_cases]
        avg = sum(reimbs) / len(reimbs)
        print(f"{days:2d} days: {len(day_cases)} cases, avg reimbursement: ${avg:.2f}")