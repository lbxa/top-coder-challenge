#!/usr/bin/env python3
"""
Test the reimbursement calculator against public cases
"""

import json
import statistics
from reimbursement_calculator import calculate_reimbursement


def test_public_cases():
    """Test against all public cases and report accuracy."""
    # Load public cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print(f"Testing against {len(cases)} public cases...")
    print("=" * 70)
    
    errors = []
    absolute_errors = []
    percent_errors = []
    
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
        
        # Print details for large errors
        if abs_error > 50 or pct_error > 10:
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
    
    print("\nMean absolute error by trip duration:")
    for days in sorted(error_by_duration.keys()):
        if days <= 10:
            mean_error = statistics.mean(error_by_duration[days])
            print(f"  {days} days: ${mean_error:.2f}")
    
    print("\nMean absolute error by efficiency:")
    for eff in ['low', 'medium', 'high']:
        if eff in error_by_efficiency:
            mean_error = statistics.mean(error_by_efficiency[eff])
            print(f"  {eff}: ${mean_error:.2f}")
    
    print("\nMean absolute error by spending level:")
    for spend in ['low', 'medium', 'high']:
        if spend in error_by_spending:
            mean_error = statistics.mean(error_by_spending[spend])
            print(f"  {spend}: ${mean_error:.2f}")
    
    return mean_abs_error, mean_pct_error


if __name__ == "__main__":
    # Set random seed for reproducibility during testing
    import random
    random.seed(42)
    
    mean_abs_error, mean_pct_error = test_public_cases()
    
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