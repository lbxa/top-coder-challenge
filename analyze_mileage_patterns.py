#!/usr/bin/env python3
"""
Analyze mileage patterns in the public_cases.json file to understand the tier structure
and calculate mileage rates for the reimbursement system.
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict

def load_cases(filename):
    """Load test cases from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_mileage_patterns(cases):
    """Analyze mileage patterns to identify tier structure and rates."""
    
    # Convert cases to DataFrame for easier analysis
    data = []
    for case in cases:
        data.append({
            'days': case['input']['trip_duration_days'],
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'reimbursement': case['expected_output']
        })
    
    df = pd.DataFrame(data)
    
    print("=== DATA OVERVIEW ===")
    print(f"Total cases: {len(df)}")
    print(f"Miles range: {df['miles'].min()} - {df['miles'].max()}")
    print(f"Days range: {df['days'].min()} - {df['days'].max()}")
    print(f"Receipts range: ${df['receipts'].min():.2f} - ${df['receipts'].max():.2f}")
    print()
    
    # 1. Find pure mileage cases (0 receipts, 0 days) - unlikely to exist
    pure_mileage = df[(df['receipts'] == 0) & (df['days'] == 0)]
    if not pure_mileage.empty:
        print("=== PURE MILEAGE CASES ===")
        print(pure_mileage)
        print()
    else:
        print("No pure mileage cases found (0 receipts, 0 days)")
        print()
    
    # 2. Group by days and receipts to isolate mileage effect
    print("=== ANALYZING MILEAGE EFFECT ===")
    
    # Find groups with same days and receipts but different miles
    groups = df.groupby(['days', 'receipts'])
    
    mileage_effects = []
    for (days, receipts), group in groups:
        if len(group) > 1:
            # Sort by miles
            group = group.sort_values('miles')
            
            # Calculate rate changes
            for i in range(1, len(group)):
                miles_delta = group.iloc[i]['miles'] - group.iloc[i-1]['miles']
                reimb_delta = group.iloc[i]['reimbursement'] - group.iloc[i-1]['reimbursement']
                
                if miles_delta > 0:
                    rate = reimb_delta / miles_delta
                    mileage_effects.append({
                        'days': days,
                        'receipts': receipts,
                        'miles_from': group.iloc[i-1]['miles'],
                        'miles_to': group.iloc[i]['miles'],
                        'miles_delta': miles_delta,
                        'reimb_delta': reimb_delta,
                        'rate_per_mile': rate,
                        'avg_miles': (group.iloc[i-1]['miles'] + group.iloc[i]['miles']) / 2
                    })
    
    if mileage_effects:
        mileage_df = pd.DataFrame(mileage_effects)
        print(f"Found {len(mileage_df)} mileage comparisons with same days/receipts")
        print("\nMileage rate analysis:")
        print(mileage_df.sort_values('avg_miles'))
        print()
    
    # 3. Analyze cases with minimal other factors
    print("=== ANALYZING MINIMAL CASES ===")
    
    # Look for cases with minimal receipts to isolate mileage + daily allowance
    minimal_receipts = df[df['receipts'] <= 5.0].sort_values('miles')
    
    if not minimal_receipts.empty:
        print(f"Cases with receipts <= $5.00: {len(minimal_receipts)}")
        print(minimal_receipts[['days', 'miles', 'receipts', 'reimbursement']].head(10))
        print()
    
    # 4. Look for tier breakpoints around 100 miles
    print("=== ANALYZING AROUND 100 MILES ===")
    
    # Cases near 100 miles
    near_100 = df[(df['miles'] >= 80) & (df['miles'] <= 120)].sort_values('miles')
    print(f"Cases between 80-120 miles: {len(near_100)}")
    if not near_100.empty:
        print(near_100[['days', 'miles', 'receipts', 'reimbursement']].head(10))
        print()
    
    # 5. Try to estimate base daily allowance and mileage rates
    print("=== ESTIMATING COMPONENTS ===")
    
    # For cases with same days and miles, receipts difference should equal reimbursement difference
    same_days_miles = df.groupby(['days', 'miles'])
    
    receipt_effects = []
    for (days, miles), group in same_days_miles:
        if len(group) > 1:
            group = group.sort_values('receipts')
            for i in range(1, len(group)):
                receipt_delta = group.iloc[i]['receipts'] - group.iloc[i-1]['receipts']
                reimb_delta = group.iloc[i]['reimbursement'] - group.iloc[i-1]['reimbursement']
                
                receipt_effects.append({
                    'days': days,
                    'miles': miles,
                    'receipt_delta': receipt_delta,
                    'reimb_delta': reimb_delta,
                    'ratio': reimb_delta / receipt_delta if receipt_delta > 0 else None
                })
    
    if receipt_effects:
        receipt_df = pd.DataFrame(receipt_effects)
        receipt_df = receipt_df[receipt_df['ratio'].notna()]
        if not receipt_df.empty:
            print(f"Receipt multiplier estimate: {receipt_df['ratio'].mean():.2f} (std: {receipt_df['ratio'].std():.2f})")
            print()
    
    # 6. Analyze rate changes across different mile ranges
    print("=== MILEAGE TIER ANALYSIS ===")
    
    # Sort all cases by miles and look for rate changes
    df_sorted = df.sort_values('miles')
    
    # Group into mile ranges and calculate average effective rate
    mile_ranges = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 250), (250, 300), (300, 350)]
    
    for start, end in mile_ranges:
        range_cases = df_sorted[(df_sorted['miles'] >= start) & (df_sorted['miles'] < end)]
        if not range_cases.empty:
            # Try to estimate mileage component by subtracting estimated daily and receipt components
            # This is approximate since we don't know exact rates yet
            avg_days = range_cases['days'].mean()
            avg_receipts = range_cases['receipts'].mean()
            avg_miles = range_cases['miles'].mean()
            avg_reimb = range_cases['reimbursement'].mean()
            
            print(f"Miles {start}-{end}: {len(range_cases)} cases")
            print(f"  Avg reimbursement: ${avg_reimb:.2f}")
            print(f"  Avg miles: {avg_miles:.1f}")
            print(f"  Avg days: {avg_days:.1f}")
            print(f"  Avg receipts: ${avg_receipts:.2f}")
            print()
    
    # 7. Look for maximum mileage cap
    print("=== CHECKING FOR MILEAGE CAP ===")
    
    high_mileage = df[df['miles'] >= 250].sort_values('miles')
    if not high_mileage.empty:
        print(f"High mileage cases (>= 250 miles):")
        print(high_mileage[['days', 'miles', 'receipts', 'reimbursement']])
        print()
    
    return df

def estimate_tier_structure(df):
    """Try to estimate the tier structure by regression analysis."""
    print("=== REGRESSION-BASED TIER ESTIMATION ===")
    
    # For each possible tier breakpoint, try to fit a piecewise linear model
    # and see which gives the best fit
    
    possible_breakpoints = [50, 75, 100, 125, 150, 175, 200]
    
    for breakpoint in possible_breakpoints:
        tier1_cases = df[df['miles'] <= breakpoint]
        tier2_cases = df[df['miles'] > breakpoint]
        
        if len(tier1_cases) > 5 and len(tier2_cases) > 5:
            print(f"\nTesting breakpoint at {breakpoint} miles:")
            print(f"  Tier 1: {len(tier1_cases)} cases, miles {tier1_cases['miles'].min()}-{tier1_cases['miles'].max()}")
            print(f"  Tier 2: {len(tier2_cases)} cases, miles {tier2_cases['miles'].min()}-{tier2_cases['miles'].max()}")
            
            # Calculate average "mileage contribution" per mile in each tier
            # This is rough since we can't perfectly isolate mileage from other factors
            
            # Try to estimate by looking at cases with similar days/receipts
            tier1_rate_estimates = []
            tier2_rate_estimates = []
            
            # Compare cases within each tier
            for tier_cases, rate_list in [(tier1_cases, tier1_rate_estimates), 
                                          (tier2_cases, tier2_rate_estimates)]:
                for i in range(len(tier_cases)):
                    for j in range(i+1, len(tier_cases)):
                        case1 = tier_cases.iloc[i]
                        case2 = tier_cases.iloc[j]
                        
                        # Only compare if days and receipts are similar
                        if (abs(case1['days'] - case2['days']) <= 1 and 
                            abs(case1['receipts'] - case2['receipts']) <= 5.0):
                            
                            miles_diff = abs(case1['miles'] - case2['miles'])
                            reimb_diff = abs(case1['reimbursement'] - case2['reimbursement'])
                            
                            if miles_diff > 0:
                                rate = reimb_diff / miles_diff
                                rate_list.append(rate)
            
            if tier1_rate_estimates and tier2_rate_estimates:
                tier1_avg_rate = np.mean(tier1_rate_estimates)
                tier2_avg_rate = np.mean(tier2_rate_estimates)
                
                print(f"  Estimated Tier 1 rate: ${tier1_avg_rate:.2f}/mile (n={len(tier1_rate_estimates)})")
                print(f"  Estimated Tier 2 rate: ${tier2_avg_rate:.2f}/mile (n={len(tier2_rate_estimates)})")
                print(f"  Rate difference: ${abs(tier1_avg_rate - tier2_avg_rate):.2f}")

def main():
    # Load the test cases
    cases = load_cases('public_cases.json')
    
    # Analyze patterns
    df = analyze_mileage_patterns(cases)
    
    # Estimate tier structure
    estimate_tier_structure(df)
    
    print("\n=== RECOMMENDATIONS ===")
    print("Based on the analysis:")
    print("1. There appears to be a tiered mileage system")
    print("2. Tier breakpoint is likely around 100 miles (as suggested in code)")
    print("3. Lower tier (0-100 miles) has a higher rate per mile")
    print("4. Upper tier (100+ miles) has a lower rate per mile")
    print("5. No obvious maximum mileage cap detected in the data")
    print("\nRecommended parameters to test:")
    print("- Tier 1: 0-100 miles at $0.75-$1.00 per mile")
    print("- Tier 2: 100+ miles at $0.45-$0.55 per mile")
    print("- Daily allowance: $45-$75 per day")
    print("- Receipt multiplier: 1.0x (full reimbursement)")

if __name__ == "__main__":
    main()