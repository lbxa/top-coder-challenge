#!/usr/bin/env python3
"""
Analyze error patterns to improve the calculator
"""

import json
from reimbursement_calculator_optimized import calculate_reimbursement


def analyze_magic_cents():
    """Analyze the magic cents pattern in detail."""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Group by cents ending
    cents_groups = {}
    
    for case in cases:
        inp = case['input']
        expected = case['expected_output']
        receipts = inp['total_receipts_amount']
        
        # Get cents value
        cents = int(round(receipts * 100)) % 100
        
        if cents not in cents_groups:
            cents_groups[cents] = []
        
        # Calculate our prediction
        predicted = calculate_reimbursement(
            inp['trip_duration_days'],
            inp['miles_traveled'],
            receipts
        )
        
        error = predicted - expected
        
        cents_groups[cents].append({
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'days': inp['trip_duration_days'],
            'miles': inp['miles_traveled']
        })
    
    # Analyze .49 and .99 patterns
    print("MAGIC CENTS ANALYSIS")
    print("=" * 60)
    
    for cents_value in [49, 99]:
        if cents_value in cents_groups:
            group = cents_groups[cents_value]
            errors = [c['error'] for c in group]
            
            print(f"\nReceipts ending in .{cents_value:02d}:")
            print(f"  Count: {len(group)}")
            print(f"  Average error: ${sum(errors)/len(errors):.2f}")
            
            # Show examples
            print("  Examples:")
            for i, case in enumerate(sorted(group, key=lambda x: abs(x['error']), reverse=True)[:5]):
                print(f"    {case['days']}d, {case['miles']:.0f}mi, ${case['receipts']:.2f}")
                print(f"      Expected: ${case['expected']:.2f}, Got: ${case['predicted']:.2f}, Error: ${case['error']:.2f}")
    
    # Compare with other cents values
    print("\nComparison with other cents endings:")
    avg_errors = {}
    for cents, group in cents_groups.items():
        if len(group) >= 5:  # Only consider groups with enough samples
            errors = [abs(c['error']) for c in group]
            avg_errors[cents] = sum(errors) / len(errors)
    
    # Sort by average error
    sorted_cents = sorted(avg_errors.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 10 cents values by average absolute error:")
    for cents, avg_err in sorted_cents[:10]:
        count = len(cents_groups[cents])
        print(f"  .{cents:02d}: ${avg_err:.2f} (n={count})")
    
    # Analyze relationship between receipt amount and error for .49/.99
    print("\n\nRECEIPT AMOUNT ANALYSIS FOR .49/.99 ENDINGS")
    print("=" * 60)
    
    for cents_value in [49, 99]:
        if cents_value in cents_groups:
            group = cents_groups[cents_value]
            
            # Group by receipt ranges
            ranges = [(0, 100), (100, 500), (500, 1000), (1000, 2000), (2000, 5000)]
            
            print(f"\nReceipts ending in .{cents_value:02d} by amount range:")
            for low, high in ranges:
                in_range = [c for c in group if low <= c['receipts'] < high]
                if in_range:
                    avg_error = sum(c['error'] for c in in_range) / len(in_range)
                    print(f"  ${low}-${high}: avg error ${avg_error:.2f} (n={len(in_range)})")


if __name__ == "__main__":
    analyze_magic_cents()