#!/usr/bin/env python3
"""
Test the reimbursement calculator against public cases
"""

import json
import statistics
import random
from reimbursement_calculator import calculate_reimbursement


def test_public_cases(verbose=False):
    """Test against all public cases and report accuracy."""
    # Load public cases
    with open('../public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print(f"Testing against {len(cases)} public cases...")
    print("=" * 70)
    
    errors = []
    absolute_errors = []
    percent_errors = []
    large_error_cases = []
    
    # Test each case
    for i, case in enumerate(cases):
        input_data = case['input']
        expected = case['expected_output']
        
        # Calculate using our implementation
        calculated = calculate_reimbursement(
            input_data['trip_duration_days'],
            input_data['miles_traveled'],
            input_data['total_receipts_amount']
        )
        
        # Calculate error
        error = calculated - expected
        abs_error = abs(error)
        pct_error = (abs_error / expected * 100) if expected > 0 else 0
        
        errors.append(error)
        absolute_errors.append(abs_error)
        percent_errors.append(pct_error)
        
        # Track large errors for analysis
        if abs_error > 50 or pct_error > 10:
            large_error_cases.append({
                'index': i,
                'input': input_data,
                'expected': expected,
                'calculated': calculated,
                'error': error,
                'pct_error': pct_error
            })
            
            if verbose and len(large_error_cases) <= 10:
                print(f"\nCase {i}: LARGE ERROR")
                print(f"  Input: {input_data['trip_duration_days']} days, "
                      f"{input_data['miles_traveled']} miles, "
                      f"${input_data['total_receipts_amount']:.2f} receipts")
                print(f"  Expected: ${expected:.2f}")
                print(f"  Calculated: ${calculated:.2f}")
                print(f"  Error: ${error:.2f} ({pct_error:.1f}%)")
    
    # Calculate statistics
    mean_abs_error = statistics.mean(absolute_errors)
    median_abs_error = statistics.median(absolute_errors)
    max_abs_error = max(absolute_errors)
    
    mean_pct_error = statistics.mean(percent_errors)
    median_pct_error = statistics.median(percent_errors)
    max_pct_error = max(percent_errors)
    
    # Count cases within tolerance
    within_5_dollars = sum(1 for e in absolute_errors if e <= 5)
    within_10_dollars = sum(1 for e in absolute_errors if e <= 10)
    within_20_dollars = sum(1 for e in absolute_errors if e <= 20)
    within_5_percent = sum(1 for e in percent_errors if e <= 5)
    within_10_percent = sum(1 for e in percent_errors if e <= 10)
    
    print("\n" + "=" * 70)
    print("ACCURACY REPORT")
    print("=" * 70)
    print(f"\nAbsolute Error Statistics:")
    print(f"  Mean: ${mean_abs_error:.2f}")
    print(f"  Median: ${median_abs_error:.2f}")
    print(f"  Max: ${max_abs_error:.2f}")
    
    print(f"\nPercentage Error Statistics:")
    print(f"  Mean: {mean_pct_error:.1f}%")
    print(f"  Median: {median_pct_error:.1f}%")
    print(f"  Max: {max_pct_error:.1f}%")
    
    print(f"\nAccuracy Thresholds:")
    print(f"  Within $5: {within_5_dollars}/{len(cases)} ({within_5_dollars/len(cases)*100:.1f}%)")
    print(f"  Within $10: {within_10_dollars}/{len(cases)} ({within_10_dollars/len(cases)*100:.1f}%)")
    print(f"  Within $20: {within_20_dollars}/{len(cases)} ({within_20_dollars/len(cases)*100:.1f}%)")
    print(f"  Within 5%: {within_5_percent}/{len(cases)} ({within_5_percent/len(cases)*100:.1f}%)")
    print(f"  Within 10%: {within_10_percent}/{len(cases)} ({within_10_percent/len(cases)*100:.1f}%)")
    
    # Analyze error patterns
    print("\n" + "=" * 70)
    print("ERROR PATTERN ANALYSIS")
    print("=" * 70)
    
    # Group errors by trip characteristics
    error_by_duration = {}
    error_by_efficiency = {}
    error_by_spending = {}
    error_by_cluster = {'road_warrior': [], 'optimal_business': [], 'extended_low': [], 
                       'standard': [], 'local': [], 'high_spend': []}
    
    for i, case in enumerate(cases):
        input_data = case['input']
        days = input_data['trip_duration_days']
        miles = input_data['miles_traveled']
        receipts = input_data['total_receipts_amount']
        
        miles_per_day = miles / days if days > 0 else 0
        receipts_per_day = receipts / days if days > 0 else 0
        
        # Group by duration
        if days not in error_by_duration:
            error_by_duration[days] = []
        error_by_duration[days].append(absolute_errors[i])
        
        # Group by efficiency
        if miles_per_day < 100:
            eff_group = 'low'
        elif miles_per_day < 200:
            eff_group = 'medium'
        else:
            eff_group = 'high'
        
        if eff_group not in error_by_efficiency:
            error_by_efficiency[eff_group] = []
        error_by_efficiency[eff_group].append(absolute_errors[i])
        
        # Group by spending
        if receipts_per_day < 50:
            spend_group = 'low'
        elif receipts_per_day < 150:
            spend_group = 'medium'
        else:
            spend_group = 'high'
        
        if spend_group not in error_by_spending:
            error_by_spending[spend_group] = []
        error_by_spending[spend_group].append(absolute_errors[i])
        
        # Determine cluster
        if miles_per_day > 350 and days <= 3:
            cluster = 'road_warrior'
        elif (days == 5 and 170 <= miles_per_day <= 230 and receipts_per_day < 110):
            cluster = 'optimal_business'
        elif days >= 7 and miles_per_day < 120:
            cluster = 'extended_low'
        elif receipts_per_day > 140:
            cluster = 'high_spend'
        elif miles < 60 and days <= 2:
            cluster = 'local'
        else:
            cluster = 'standard'
        
        error_by_cluster[cluster].append(absolute_errors[i])
    
    print("\nMean absolute error by trip duration:")
    for days in sorted(error_by_duration.keys()):
        if days <= 10 and len(error_by_duration[days]) > 0:
            mean_error = statistics.mean(error_by_duration[days])
            count = len(error_by_duration[days])
            print(f"  {days} days: ${mean_error:.2f} (n={count})")
    
    print("\nMean absolute error by efficiency:")
    for eff in ['low', 'medium', 'high']:
        if eff in error_by_efficiency and len(error_by_efficiency[eff]) > 0:
            mean_error = statistics.mean(error_by_efficiency[eff])
            count = len(error_by_efficiency[eff])
            print(f"  {eff}: ${mean_error:.2f} (n={count})")
    
    print("\nMean absolute error by spending level:")
    for spend in ['low', 'medium', 'high']:
        if spend in error_by_spending and len(error_by_spending[spend]) > 0:
            mean_error = statistics.mean(error_by_spending[spend])
            count = len(error_by_spending[spend])
            print(f"  {spend}: ${mean_error:.2f} (n={count})")
    
    print("\nMean absolute error by cluster:")
    for cluster, errors in error_by_cluster.items():
        if len(errors) > 0:
            mean_error = statistics.mean(errors)
            count = len(errors)
            print(f"  {cluster}: ${mean_error:.2f} (n={count})")
    
    return mean_abs_error, mean_pct_error, large_error_cases


if __name__ == "__main__":
    mean_abs_error, mean_pct_error, large_errors = test_public_cases(verbose=True)
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION FOR OPTIMIZATION")
    print("=" * 70)
    
    if mean_abs_error > 20 or mean_pct_error > 10:
        print("❌ Accuracy needs significant improvement")
        print("   Consider adjusting:")
        print("   - Base per diem rates")
        print("   - Mileage tier breakpoints and rates")
        print("   - Cluster classification logic")
        print("   - Receipt penalty thresholds")
    elif mean_abs_error > 10 or mean_pct_error > 5:
        print("⚠️  Accuracy is moderate, fine-tuning needed")
        print("   Focus on:")
        print("   - Cluster-specific multipliers")
        print("   - Efficiency bonus rates")
        print("   - Receipt coverage curves")
    else:
        print("✅ Accuracy is good!")
        print("   Minor adjustments may still improve results")
    
    # Save error analysis for optimization
    if len(large_errors) > 0:
        with open('large_errors.json', 'w') as f:
            json.dump(large_errors[:50], f, indent=2)
        print(f"\nSaved {min(50, len(large_errors))} large error cases to large_errors.json")