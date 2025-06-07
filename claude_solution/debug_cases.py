#!/usr/bin/env python3
"""Debug specific test cases to understand patterns"""

import json
from reimbursement_calculator_comprehensive import calculate_reimbursement

# Load public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Test specific cases
test_indices = [241, 637, 317, 585, 792]  # High error cases from eval

print("=== DEBUGGING HIGH ERROR CASES ===")
for idx in test_indices:
    if idx < len(cases):
        case = cases[idx]
        inp = case['input']
        expected = case['expected_output']
        
        calculated = calculate_reimbursement(
            inp['trip_duration_days'],
            inp['miles_traveled'],
            inp['total_receipts_amount']
        )
        
        print(f"\nCase {idx}:")
        print(f"  Inputs: {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']}")
        print(f"  Expected: ${expected:.2f}")
        print(f"  Calculated: ${calculated:.2f}")
        print(f"  Error: ${abs(calculated - expected):.2f}")
        
        # Calculate ratios
        receipt_ratio = expected / inp['total_receipts_amount']
        per_day = expected / inp['trip_duration_days']
        per_mile = expected / inp['miles_traveled']
        
        print(f"  Expected ratios:")
        print(f"    Reimb/Receipt: {receipt_ratio:.3f}")
        print(f"    Reimb/Day: ${per_day:.2f}")
        print(f"    Reimb/Mile: ${per_mile:.3f}")

# Look for cases with very high receipts
print("\n=== ANALYZING HIGH RECEIPT CASES ===")
high_receipt_cases = [(i, c) for i, c in enumerate(cases) if c['input']['total_receipts_amount'] > 2000]
print(f"Found {len(high_receipt_cases)} cases with receipts > $2000")

# Group by reimbursement ratio
ratios = []
for i, case in high_receipt_cases:
    ratio = case['expected_output'] / case['input']['total_receipts_amount']
    ratios.append((ratio, i, case))

ratios.sort()

print("\nLowest ratios (reimb/receipt):")
for ratio, idx, case in ratios[:5]:
    inp = case['input']
    print(f"  Case {idx}: {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"    Reimb: ${case['expected_output']:.2f}, Ratio: {ratio:.3f}")

print("\nHighest ratios (reimb/receipt):")
for ratio, idx, case in ratios[-5:]:
    inp = case['input']
    print(f"  Case {idx}: {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"    Reimb: ${case['expected_output']:.2f}, Ratio: {ratio:.3f}")

# Analyze patterns
print("\n=== PATTERN ANALYSIS ===")
print("Average ratio by trip duration for high receipt cases:")
for days in range(1, 15):
    day_cases = [c for r, i, c in ratios if c['input']['trip_duration_days'] == days]
    if day_cases:
        avg_ratio = sum(c['expected_output'] / c['input']['total_receipts_amount'] for c in day_cases) / len(day_cases)
        print(f"  {days} days: {len(day_cases)} cases, avg ratio: {avg_ratio:.3f}")