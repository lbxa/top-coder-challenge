#!/usr/bin/env python3
"""
Analyze base rates by looking at simple cases
"""

import json

def analyze_base_rates():
    # Load public cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("ANALYZING BASE RATES")
    print("="*70)
    
    # Look for cases with 0 miles and 0 receipts to find pure per diem
    print("\nCases with 0 miles and 0 receipts (pure per diem):")
    pure_per_diem = []
    for i, case in enumerate(cases):
        inp = case['input']
        if inp['miles_traveled'] == 0 and inp['total_receipts_amount'] == 0:
            days = inp['trip_duration_days']
            expected = case['expected_output']
            rate = expected / days if days > 0 else 0
            pure_per_diem.append((days, expected, rate))
            print(f"  Case {i}: {days} days -> ${expected:.2f} (${rate:.2f}/day)")
    
    if not pure_per_diem:
        print("  No such cases found")
    
    # Look for cases with 0 receipts to analyze per diem + mileage
    print("\nCases with 0 receipts (per diem + mileage only):")
    zero_receipts = []
    for i, case in enumerate(cases[:50]):  # Check first 50
        inp = case['input']
        if inp['total_receipts_amount'] == 0:
            days = inp['trip_duration_days']
            miles = inp['miles_traveled']
            expected = case['expected_output']
            zero_receipts.append((i, days, miles, expected))
    
    if zero_receipts:
        for case_num, days, miles, expected in zero_receipts[:10]:
            print(f"\n  Case {case_num}: {days} days, {miles} miles -> ${expected:.2f}")
            
            # Try different per diem rates
            for per_diem_rate in [50, 75, 100]:
                per_diem = days * per_diem_rate
                remaining = expected - per_diem
                if miles > 0:
                    implied_mileage_rate = remaining / miles
                    print(f"    If per diem = ${per_diem_rate}/day: mileage would be ${implied_mileage_rate:.3f}/mile")
    
    # Look for simple cases to understand the model
    print("\n" + "="*70)
    print("ANALYZING SIMPLE CASES")
    print("="*70)
    
    # Find cases with low values
    simple_cases = []
    for i, case in enumerate(cases):
        inp = case['input']
        if (inp['trip_duration_days'] <= 3 and 
            inp['miles_traveled'] <= 200 and 
            inp['total_receipts_amount'] <= 100):
            simple_cases.append((i, inp, case['expected_output']))
    
    print(f"\nFound {len(simple_cases)} simple cases")
    
    # Analyze a few
    for i, (case_num, inp, expected) in enumerate(simple_cases[:10]):
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        print(f"\nCase {case_num}: {days} days, {miles} miles, ${receipts:.2f} receipts")
        print(f"  Expected: ${expected:.2f}")
        
        # Try to decompose
        # Hypothesis 1: Full coverage of everything
        hypothesis1 = days * 100 + miles * 0.50 + receipts
        print(f"  Hypothesis 1 (full coverage): ${hypothesis1:.2f} (error: ${hypothesis1 - expected:+.2f})")
        
        # Hypothesis 2: Lower per diem
        hypothesis2 = days * 50 + miles * 0.50 + receipts
        print(f"  Hypothesis 2 (50/day per diem): ${hypothesis2:.2f} (error: ${hypothesis2 - expected:+.2f})")
        
        # Hypothesis 3: No receipt coverage
        hypothesis3 = days * 100 + miles * 0.50
        print(f"  Hypothesis 3 (no receipts): ${hypothesis3:.2f} (error: ${hypothesis3 - expected:+.2f})")

if __name__ == "__main__":
    analyze_base_rates()