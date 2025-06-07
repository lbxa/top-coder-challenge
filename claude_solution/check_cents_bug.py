#!/usr/bin/env python3
"""Check the cents bug pattern."""

import json
from reimbursement_calculator_optimized import calculate_reimbursement

def check_cents_bug():
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Group by cents ending
    cents_49_99 = []
    normal_cents = []
    
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        cents = int(round(receipts * 100)) % 100
        
        predicted = calculate_reimbursement(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'],
            receipts
        )
        actual = case['expected_output']
        error = abs(predicted - actual)
        
        if cents in [49, 99]:
            cents_49_99.append((actual, predicted, error, receipts))
        else:
            normal_cents.append((actual, predicted, error, receipts))
    
    # Compare averages
    if cents_49_99:
        avg_actual_bug = sum(x[0] for x in cents_49_99) / len(cents_49_99)
        avg_error_bug = sum(x[2] for x in cents_49_99) / len(cents_49_99)
        print(f"Cases with .49/.99 cents:")
        print(f"  Count: {len(cents_49_99)}")
        print(f"  Avg actual reimbursement: ${avg_actual_bug:.2f}")
        print(f"  Avg error: ${avg_error_bug:.2f}")
        
        # Show some examples
        print("\n  Examples:")
        for actual, pred, err, receipts in sorted(cents_49_99, key=lambda x: x[2], reverse=True)[:5]:
            print(f"    Receipts ${receipts:.2f}: Expected ${actual:.2f}, Got ${pred:.2f}, Error ${err:.2f}")
    
    if normal_cents:
        avg_actual_normal = sum(x[0] for x in normal_cents) / len(normal_cents)
        avg_error_normal = sum(x[2] for x in normal_cents) / len(normal_cents)
        print(f"\nNormal cases:")
        print(f"  Count: {len(normal_cents)}")
        print(f"  Avg actual reimbursement: ${avg_actual_normal:.2f}")
        print(f"  Avg error: ${avg_error_normal:.2f}")
    
    # Check if cents bug cases actually get LESS reimbursement
    print(f"\nCents bug effect: ${avg_actual_bug - avg_actual_normal:.2f} difference")
    print("(Negative means .49/.99 cases get LESS reimbursement)")

if __name__ == "__main__":
    check_cents_bug()