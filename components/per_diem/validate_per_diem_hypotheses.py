#!/usr/bin/env python3
"""
Per Diem Hypothesis Validation

Acting as a validator to critically test multiple hypotheses:
1. Is it really $100/day flat?
2. Could there be hidden step functions?
3. Are there weekend/weekday differences?
4. Does per diem vary by trip length ranges?
5. Are there seasonal/monthly variations?
6. Does per diem interact with other variables?
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from components.per_diem.per_diem import PerDiemCalculator
from components.mileage.mileage import MileageCalculator
from components.receipts.receipts import ReceiptProcessor
from components.bonuses.bonuses import BonusCalculator


def load_and_prepare_data():
    """Load public cases and calculate component contributions."""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Initialize calculators
    mileage_calc = MileageCalculator()
    
    data = []
    for i, case in enumerate(cases):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Calculate known components
        mileage_pay = mileage_calc.calculate(miles)
        
        # Estimate per diem contribution by subtracting mileage
        # This gives us per_diem + receipts + bonuses + bugs
        residual_after_mileage = reimbursement - mileage_pay
        
        data.append({
            'case_id': i,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'reimbursement': reimbursement,
            'mileage_pay': mileage_pay,
            'residual_after_mileage': residual_after_mileage,
            'implied_per_day_rate': residual_after_mileage / days if days > 0 else 0,
            'miles_per_day': miles / days if days > 0 else 0,
            'receipts_per_day': receipts / days if days > 0 else 0
        })
    
    return pd.DataFrame(data)


def test_flat_rate_hypothesis(df):
    """Test if per diem is truly a flat rate."""
    print("=== HYPOTHESIS 1: FLAT $100/DAY RATE ===")
    
    # Group by days and analyze the residuals
    day_groups = df.groupby('days').agg({
        'residual_after_mileage': ['mean', 'std', 'min', 'max', 'count'],
        'implied_per_day_rate': ['mean', 'std']
    }).round(2)
    
    print("\nResidual after mileage by trip length:")
    print("(If per diem is flat $100/day, residual should increase linearly with days)")
    print(day_groups)
    
    # Test linearity
    days_array = df['days'].unique()
    mean_residuals = [df[df['days'] == d]['residual_after_mileage'].mean() for d in sorted(days_array)]
    
    # Fit a line and check R²
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(sorted(days_array), mean_residuals)
    
    print(f"\nLinear regression on mean residuals:")
    print(f"  Slope: ${slope:.2f} per day")
    print(f"  Intercept: ${intercept:.2f}")
    print(f"  R²: {r_value**2:.4f}")
    print(f"  Expected slope if flat $100/day: ~$100 (plus receipts/bonuses)")
    
    if abs(slope - 100) > 20:
        print("  ⚠️  Slope significantly different from $100/day!")
    
    return slope, r_value**2


def test_step_function_hypothesis(df):
    """Test for step functions or brackets in per diem."""
    print("\n=== HYPOTHESIS 2: STEP FUNCTIONS BY TRIP LENGTH ===")
    
    # Calculate average per-day rate from residuals
    df['adjusted_per_day'] = (df['residual_after_mileage'] - df['receipts'] * 0.85) / df['days']
    
    # Look for discontinuities
    trip_lengths = sorted(df['days'].unique())
    avg_rates = []
    
    for days in trip_lengths:
        subset = df[df['days'] == days]
        if len(subset) >= 5:  # Need enough samples
            avg_rate = subset['adjusted_per_day'].mean()
            std_rate = subset['adjusted_per_day'].std()
            avg_rates.append({
                'days': days,
                'avg_rate': avg_rate,
                'std': std_rate,
                'count': len(subset)
            })
    
    print("\nAverage per-day rates (adjusted for receipts):")
    print(f"{'Days':>4} | {'Avg Rate':>10} | {'Std Dev':>8} | {'Count':>6}")
    print("-" * 35)
    
    for rate_info in avg_rates:
        print(f"{rate_info['days']:4d} | ${rate_info['avg_rate']:9.2f} | ${rate_info['std']:7.2f} | {rate_info['count']:6d}")
    
    # Check for jumps between consecutive trip lengths
    print("\nChecking for step changes:")
    for i in range(1, len(avg_rates)):
        prev = avg_rates[i-1]
        curr = avg_rates[i]
        diff = curr['avg_rate'] - prev['avg_rate']
        if abs(diff) > 10:
            print(f"  Jump from {prev['days']} to {curr['days']} days: ${diff:+.2f}")


def test_variable_rate_hypothesis(df):
    """Test if per diem varies based on other factors."""
    print("\n=== HYPOTHESIS 3: VARIABLE RATES BASED ON OTHER FACTORS ===")
    
    # Test 1: Does per diem vary with total miles?
    print("\nTest 1: Per diem variation by total miles")
    
    # Bin trips by mileage
    df['mileage_bin'] = pd.cut(df['miles'], bins=[0, 100, 300, 600, 1000, 2000], 
                                labels=['0-100', '100-300', '300-600', '600-1000', '1000+'])
    
    mileage_analysis = df.groupby('mileage_bin').agg({
        'implied_per_day_rate': ['mean', 'std', 'count']
    }).round(2)
    
    print(mileage_analysis)
    
    # Test 2: Does per diem vary with efficiency (miles/day)?
    print("\nTest 2: Per diem variation by efficiency")
    
    df['efficiency_bin'] = pd.cut(df['miles_per_day'], 
                                   bins=[0, 50, 100, 180, 220, 500, 2000],
                                   labels=['0-50', '50-100', '100-180', '180-220', '220-500', '500+'])
    
    efficiency_analysis = df.groupby('efficiency_bin').agg({
        'implied_per_day_rate': ['mean', 'std', 'count']
    }).round(2)
    
    print(efficiency_analysis)
    
    # Test 3: Correlation analysis
    print("\nTest 3: Correlation with other variables")
    correlations = df[['implied_per_day_rate', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day']].corr()
    print(correlations['implied_per_day_rate'].round(3))


def test_specific_day_bonuses(df):
    """Test for bonuses on specific trip lengths beyond 5 days."""
    print("\n=== HYPOTHESIS 4: SPECIFIC DAY BONUSES ===")
    
    # For each trip length, calculate the "excess" over expected
    expected_base = 100  # $100/day
    
    day_analysis = []
    for days in sorted(df['days'].unique()):
        subset = df[df['days'] == days]
        if len(subset) >= 5:
            # Remove receipt effect (rough estimate)
            adjusted_residual = subset['residual_after_mileage'] - subset['receipts'] * 0.85
            avg_adjusted = adjusted_residual.mean()
            expected = days * expected_base
            excess = avg_adjusted - expected
            excess_per_day = excess / days
            
            day_analysis.append({
                'days': days,
                'count': len(subset),
                'expected': expected,
                'actual': avg_adjusted,
                'excess': excess,
                'excess_per_day': excess_per_day
            })
    
    print(f"{'Days':>4} | {'Count':>6} | {'Expected':>9} | {'Actual':>9} | {'Excess':>8} | {'Per Day':>8}")
    print("-" * 60)
    
    for analysis in day_analysis:
        marker = "***" if abs(analysis['excess_per_day']) > 10 else ""
        print(f"{analysis['days']:4d} | {analysis['count']:6d} | ${analysis['expected']:8.0f} | "
              f"${analysis['actual']:8.0f} | ${analysis['excess']:7.0f} | ${analysis['excess_per_day']:7.1f} {marker}")
    
    print("\n*** = Potential bonus/penalty (>$10/day difference)")


def test_receipt_interaction_hypothesis(df):
    """Test if per diem interacts with receipt amounts."""
    print("\n=== HYPOTHESIS 5: PER DIEM VARIES WITH RECEIPT LEVELS ===")
    
    # Group by receipt levels
    df['receipt_level'] = pd.cut(df['receipts'], 
                                  bins=[0, 50, 200, 500, 1000, 3000],
                                  labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    
    # For trips of the same length, does per diem vary by receipt level?
    print("\nPer-day rates by receipt level (controlling for trip length):")
    
    for days in [3, 5, 7, 10]:  # Common trip lengths
        subset = df[df['days'] == days]
        if len(subset) >= 10:
            print(f"\n{days}-day trips:")
            receipt_analysis = subset.groupby('receipt_level').agg({
                'implied_per_day_rate': ['mean', 'count']
            }).round(2)
            print(receipt_analysis)


def test_alternative_base_rates(df):
    """Test which base rate minimizes prediction error."""
    print("\n=== HYPOTHESIS 6: OPTIMAL BASE RATE ===")
    
    # Test different base rates
    test_rates = range(90, 115, 2)
    errors = []
    
    for rate in test_rates:
        total_error = 0
        
        for _, row in df.iterrows():
            # Simple prediction: rate * days + mileage + receipts * 0.85
            predicted = (rate * row['days'] + 
                        row['mileage_pay'] + 
                        row['receipts'] * 0.85)
            
            error = abs(predicted - row['reimbursement'])
            total_error += error
        
        avg_error = total_error / len(df)
        errors.append({'rate': rate, 'error': avg_error})
    
    errors_df = pd.DataFrame(errors)
    best_rate = errors_df.loc[errors_df['error'].idxmin()]
    
    print(f"Base rate with minimum error: ${best_rate['rate']}/day")
    print(f"Average error: ${best_rate['error']:.2f}")
    
    print("\nError by base rate:")
    for i in range(0, len(errors), 5):
        subset = errors[i:i+5]
        rates = [f"${e['rate']}" for e in subset]
        errs = [f"${e['error']:.0f}" for e in subset]
        print(f"Rates: {' '.join(rates):30} | Errors: {' '.join(errs)}")


def main():
    """Run all hypothesis tests."""
    print("=== PER DIEM HYPOTHESIS VALIDATION ===")
    print("Loading and preparing data...")
    
    df = load_and_prepare_data()
    print(f"Loaded {len(df)} cases")
    
    # Run all tests
    slope, r2 = test_flat_rate_hypothesis(df)
    test_step_function_hypothesis(df)
    test_variable_rate_hypothesis(df)
    test_specific_day_bonuses(df)
    test_receipt_interaction_hypothesis(df)
    test_alternative_base_rates(df)
    
    # Summary
    print("\n=== VALIDATION SUMMARY ===")
    print(f"1. Flat rate hypothesis: {'SUPPORTED' if r2 > 0.9 else 'QUESTIONABLE'} (R²={r2:.3f})")
    print(f"2. Estimated daily rate from regression: ${slope:.2f}")
    print("3. Evidence suggests per diem might:")
    print("   - Have small variations by trip length")
    print("   - Interact with receipt levels")
    print("   - Include bonuses beyond just 5-day trips")
    print("\nRecommendation: Test these findings with full component integration")


if __name__ == "__main__":
    main()