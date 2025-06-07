#!/usr/bin/env python3
"""
Analyze mileage patterns in public cases to optimize MileageCalculator parameters
"""

import json
from collections import defaultdict
import statistics

def analyze_mileage_patterns():
    # Load public cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print(f"Loaded {len(cases)} test cases")
    print("\n" + "="*70)
    
    # Organize cases for analysis
    cases_by_params = defaultdict(list)
    
    for case in cases:
        inp = case['input']
        key = (inp['trip_duration_days'], inp['total_receipts_amount'])
        cases_by_params[key].append({
            'miles': inp['miles_traveled'],
            'expected': case['expected_output']
        })
    
    # Find cases with same days/receipts but different miles
    print("ANALYZING MILEAGE RATE CHANGES")
    print("="*70)
    
    mileage_rates = []
    
    for (days, receipts), case_list in cases_by_params.items():
        if len(case_list) > 1:
            # Sort by miles
            case_list.sort(key=lambda x: x['miles'])
            
            # Calculate incremental rates
            for i in range(1, len(case_list)):
                prev = case_list[i-1]
                curr = case_list[i]
                
                miles_delta = curr['miles'] - prev['miles']
                reimb_delta = curr['expected'] - prev['expected']
                
                if miles_delta > 0:
                    rate = reimb_delta / miles_delta
                    avg_miles = (curr['miles'] + prev['miles']) / 2
                    
                    mileage_rates.append({
                        'avg_miles': avg_miles,
                        'rate': rate,
                        'miles_from': prev['miles'],
                        'miles_to': curr['miles']
                    })
    
    # Analyze rates by mileage ranges
    ranges = [
        (0, 50, "0-50"),
        (50, 100, "50-100"),
        (100, 150, "100-150"),
        (150, 200, "150-200"),
        (200, 300, "200-300"),
        (300, 500, "300-500"),
        (500, 1000, "500-1000"),
        (1000, 2000, "1000+")
    ]
    
    print(f"\nFound {len(mileage_rates)} mileage comparison pairs")
    print("\nAverage rate by mileage range:")
    print("-" * 50)
    
    for low, high, label in ranges:
        rates_in_range = [r['rate'] for r in mileage_rates 
                         if low <= r['avg_miles'] < high]
        if rates_in_range:
            avg_rate = statistics.mean(rates_in_range)
            print(f"{label:10s} miles: ${avg_rate:.3f}/mile ({len(rates_in_range)} samples)")
    
    # Look for specific breakpoints
    print("\nBREAKPOINT ANALYSIS")
    print("-"*50)
    
    breakpoints = [50, 100, 150, 200, 250, 300, 500]
    for bp in breakpoints:
        before = [r['rate'] for r in mileage_rates if r['avg_miles'] < bp]
        after = [r['rate'] for r in mileage_rates if r['avg_miles'] >= bp]
        
        if before and after:
            before_mean = statistics.mean(before)
            after_mean = statistics.mean(after)
            if abs(before_mean - after_mean) > 0.05:
                print(f"\nPotential breakpoint at {bp} miles:")
                print(f"  Rate before: ${before_mean:.3f}/mile")
                print(f"  Rate after: ${after_mean:.3f}/mile")
                print(f"  Difference: ${before_mean - after_mean:.3f}")
    
    # Analyze zero receipt cases
    print("\n" + "="*70)
    print("ZERO RECEIPT CASES ANALYSIS")
    print("="*70)
    
    zero_receipt_cases = [(case['input']['trip_duration_days'], 
                          case['input']['miles_traveled'], 
                          case['expected_output'])
                         for case in cases if case['input']['total_receipts_amount'] == 0]
    
    if zero_receipt_cases:
        print(f"\nFound {len(zero_receipt_cases)} cases with zero receipts")
        
        # Group by days
        by_days = defaultdict(list)
        for days, miles, expected in zero_receipt_cases:
            by_days[days].append((miles, expected))
        
        for days in sorted(by_days.keys())[:5]:
            cases = sorted(by_days[days])
            print(f"\n{days}-day trips with 0 receipts:")
            for miles, expected in cases[:5]:
                # Assuming $100/day per diem
                base_per_diem = days * 100
                mileage_component = expected - base_per_diem
                if miles > 0:
                    rate = mileage_component / miles
                    print(f"  {miles:4.0f} miles -> ${expected:7.2f} (mileage: ${mileage_component:6.2f}, rate: ${rate:.3f}/mile)")
    
    # Calculate overall recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    # Calculate weighted average rates for different ranges
    tier1_rates = [r['rate'] for r in mileage_rates if r['avg_miles'] < 100]
    tier2_rates = [r['rate'] for r in mileage_rates if 100 <= r['avg_miles'] < 300]
    tier3_rates = [r['rate'] for r in mileage_rates if r['avg_miles'] >= 300]
    
    print("\nSuggested mileage tier structure:")
    if tier1_rates:
        print(f"Tier 1 (0-100 miles): ${statistics.mean(tier1_rates):.3f}/mile")
    if tier2_rates:
        print(f"Tier 2 (100-300 miles): ${statistics.mean(tier2_rates):.3f}/mile")
    if tier3_rates:
        print(f"Tier 3 (300+ miles): ${statistics.mean(tier3_rates):.3f}/mile")
    
    return mileage_rates

if __name__ == "__main__":
    analyze_mileage_patterns()