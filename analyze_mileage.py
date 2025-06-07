#!/usr/bin/env python3
"""
Analyze mileage patterns in public cases to optimize MileageCalculator parameters
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict

def analyze_mileage_patterns():
    # Load public cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Convert to DataFrame for easier analysis
    data = []
    for case in cases:
        inp = case['input']
        data.append({
            'days': inp['trip_duration_days'],
            'miles': inp['miles_traveled'],
            'receipts': inp['total_receipts_amount'],
            'expected': case['expected_output']
        })
    
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} test cases")
    print("\n" + "="*70)
    
    # Look for cases with minimal other factors to isolate mileage effect
    print("ANALYZING MILEAGE ISOLATION")
    print("="*70)
    
    # Find cases with same days and receipts but different miles
    grouped = df.groupby(['days', 'receipts'])
    
    mileage_effects = []
    for (days, receipts), group in grouped:
        if len(group) > 1:
            # Sort by miles
            group = group.sort_values('miles')
            
            # Calculate incremental rates
            for i in range(1, len(group)):
                prev = group.iloc[i-1]
                curr = group.iloc[i]
                
                miles_delta = curr['miles'] - prev['miles']
                reimb_delta = curr['expected'] - prev['expected']
                
                if miles_delta > 0:
                    rate = reimb_delta / miles_delta
                    avg_miles = (curr['miles'] + prev['miles']) / 2
                    
                    mileage_effects.append({
                        'days': days,
                        'receipts': receipts,
                        'miles_from': prev['miles'],
                        'miles_to': curr['miles'],
                        'avg_miles': avg_miles,
                        'miles_delta': miles_delta,
                        'reimb_delta': reimb_delta,
                        'rate': rate
                    })
    
    mileage_df = pd.DataFrame(mileage_effects)
    
    if len(mileage_df) > 0:
        print(f"\nFound {len(mileage_df)} mileage comparison pairs")
        
        # Analyze rates by mileage ranges
        print("\nMILEAGE RATE ANALYSIS")
        print("-"*50)
        
        # Define mileage bins
        bins = [0, 50, 100, 150, 200, 300, 500, 1000, 2000]
        mileage_df['miles_bin'] = pd.cut(mileage_df['avg_miles'], bins=bins)
        
        # Calculate average rate per bin
        rate_by_bin = mileage_df.groupby('miles_bin')['rate'].agg(['mean', 'std', 'count'])
        print("\nAverage incremental rate by mileage range:")
        print(rate_by_bin)
        
        # Look for specific breakpoints
        print("\nBREAKPOINT ANALYSIS")
        print("-"*50)
        
        # Check around common breakpoints
        breakpoints = [50, 100, 150, 200, 250, 300, 500]
        for bp in breakpoints:
            before = mileage_df[mileage_df['avg_miles'] < bp]['rate']
            after = mileage_df[mileage_df['avg_miles'] >= bp]['rate']
            
            if len(before) > 0 and len(after) > 0:
                before_mean = before.mean()
                after_mean = after.mean()
                if abs(before_mean - after_mean) > 0.05:
                    print(f"\nPotential breakpoint at {bp} miles:")
                    print(f"  Rate before: ${before_mean:.3f}/mile")
                    print(f"  Rate after: ${after_mean:.3f}/mile")
                    print(f"  Difference: ${before_mean - after_mean:.3f}")
    
    # Analyze cases with zero receipts to see pure mileage effect
    print("\n" + "="*70)
    print("ZERO RECEIPT CASES")
    print("="*70)
    
    zero_receipt = df[df['receipts'] == 0].copy()
    if len(zero_receipt) > 0:
        print(f"\nFound {len(zero_receipt)} cases with zero receipts")
        
        # Group by days to see if mileage calculation varies by trip length
        for days in sorted(zero_receipt['days'].unique())[:5]:
            day_cases = zero_receipt[zero_receipt['days'] == days].sort_values('miles')
            if len(day_cases) > 1:
                print(f"\n{days}-day trips with 0 receipts:")
                for idx, row in day_cases.head(5).iterrows():
                    base_per_diem = days * 100  # Assumed from code
                    mileage_component = row['expected'] - base_per_diem
                    print(f"  {row['miles']:4.0f} miles -> ${row['expected']:7.2f} (mileage: ${mileage_component:6.2f})")
    
    # Look for maximum mileage effects
    print("\n" + "="*70)
    print("HIGH MILEAGE ANALYSIS")
    print("="*70)
    
    high_mileage = df[df['miles'] > 800].copy()
    high_mileage['reimb_per_mile'] = high_mileage['expected'] / high_mileage['miles']
    
    print(f"\nCases with >800 miles:")
    print(f"Average reimbursement per mile: ${high_mileage['reimb_per_mile'].mean():.3f}")
    print(f"Min reimbursement per mile: ${high_mileage['reimb_per_mile'].min():.3f}")
    print(f"Max reimbursement per mile: ${high_mileage['reimb_per_mile'].max():.3f}")
    
    # Generate recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS FOR MILEAGE CALCULATOR")
    print("="*70)
    
    if len(mileage_df) > 0:
        # Find the most likely tier structure
        tier1_rates = mileage_df[mileage_df['avg_miles'] < 100]['rate']
        tier2_rates = mileage_df[(mileage_df['avg_miles'] >= 100) & (mileage_df['avg_miles'] < 300)]['rate']
        tier3_rates = mileage_df[mileage_df['avg_miles'] >= 300]['rate']
        
        print("\nSuggested tier structure:")
        if len(tier1_rates) > 0:
            print(f"Tier 1 (0-100 miles): ${tier1_rates.mean():.3f}/mile")
        if len(tier2_rates) > 0:
            print(f"Tier 2 (100-300 miles): ${tier2_rates.mean():.3f}/mile")
        if len(tier3_rates) > 0:
            print(f"Tier 3 (300+ miles): ${tier3_rates.mean():.3f}/mile")
    
    return df

if __name__ == "__main__":
    df = analyze_mileage_patterns()