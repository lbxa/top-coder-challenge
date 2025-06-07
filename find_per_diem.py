#!/usr/bin/env python3
"""
Find the actual per diem rate by analyzing simple cases
"""

import json

def find_per_diem():
    # Load public cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("FINDING PER DIEM RATE")
    print("="*70)
    
    # Look for the simplest cases - 1 day trips with minimal miles and receipts
    simple_cases = []
    
    for i, case in enumerate(cases):
        inp = case['input']
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        
        # Focus on 1-day trips with low complexity
        if days == 1 and miles < 20 and receipts < 10:
            simple_cases.append({
                'case': i,
                'days': days,
                'miles': miles,
                'receipts': receipts,
                'expected': expected
            })
    
    print(f"\nFound {len(simple_cases)} simple 1-day cases:")
    for case in sorted(simple_cases, key=lambda x: x['miles'])[:10]:
        print(f"\nCase {case['case']}: {case['days']} day, {case['miles']} miles, ${case['receipts']:.2f} receipts")
        print(f"  Expected: ${case['expected']:.2f}")
        
        # Try to decompose
        # Assume mileage at 0.58/mile for first tier
        mileage_component = case['miles'] * 0.58
        
        # Assume receipts might not be fully covered
        for receipt_coverage in [0, 0.5, 0.75, 1.0]:
            receipt_component = case['receipts'] * receipt_coverage
            
            # Calculate implied per diem
            per_diem_component = case['expected'] - mileage_component - receipt_component
            implied_per_diem = per_diem_component / case['days']
            
            if 40 <= implied_per_diem <= 120:  # Reasonable range
                print(f"  If receipt coverage = {receipt_coverage*100:.0f}%: implied per diem = ${implied_per_diem:.2f}")
    
    # Look at 2-day trips too
    print("\n" + "="*70)
    print("2-DAY SIMPLE CASES")
    print("="*70)
    
    two_day_cases = []
    for i, case in enumerate(cases):
        inp = case['input']
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        
        if days == 2 and miles < 50 and receipts < 20:
            two_day_cases.append({
                'case': i,
                'days': days,
                'miles': miles,
                'receipts': receipts,
                'expected': expected
            })
    
    for case in sorted(two_day_cases, key=lambda x: x['miles'])[:5]:
        print(f"\nCase {case['case']}: {case['days']} days, {case['miles']} miles, ${case['receipts']:.2f} receipts")
        print(f"  Expected: ${case['expected']:.2f}")
        
        # Similar analysis
        mileage_component = case['miles'] * 0.58
        
        for receipt_coverage in [0, 0.5, 0.75, 1.0]:
            receipt_component = case['receipts'] * receipt_coverage
            per_diem_component = case['expected'] - mileage_component - receipt_component
            implied_per_diem = per_diem_component / case['days']
            
            if 40 <= implied_per_diem <= 120:
                print(f"  If receipt coverage = {receipt_coverage*100:.0f}%: implied per diem = ${implied_per_diem:.2f}")

if __name__ == "__main__":
    find_per_diem()