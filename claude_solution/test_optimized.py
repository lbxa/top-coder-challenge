#!/usr/bin/env python3
"""
Test the optimized calculator against all public cases
"""

import json
import statistics
from reimbursement_calculator_optimized import calculate_reimbursement


def test_optimized():
    """Test optimized calculator."""
    # Load public cases
    with open('../public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print(f"Testing optimized calculator against {len(cases)} public cases...")
    print("=" * 70)
    
    errors = []
    absolute_errors = []
    percent_errors = []
    
    # Test each case
    for i, case in enumerate(cases):
        input_data = case['input']
        expected = case['expected_output']
        
        calculated = calculate_reimbursement(
            input_data['trip_duration_days'],
            input_data['miles_traveled'],
            input_data['total_receipts_amount']
        )
        
        error = calculated - expected
        abs_error = abs(error)
        pct_error = (abs_error / expected * 100) if expected > 0 else 0
        
        errors.append(error)
        absolute_errors.append(abs_error)
        percent_errors.append(pct_error)
    
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
    within_50_dollars = sum(1 for e in absolute_errors if e <= 50)
    within_5_percent = sum(1 for e in percent_errors if e <= 5)
    within_10_percent = sum(1 for e in percent_errors if e <= 10)
    
    print("OPTIMIZED CALCULATOR ACCURACY REPORT")
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
    print(f"  Within $50: {within_50_dollars}/{len(cases)} ({within_50_dollars/len(cases)*100:.1f}%)")
    print(f"  Within 5%: {within_5_percent}/{len(cases)} ({within_5_percent/len(cases)*100:.1f}%)")
    print(f"  Within 10%: {within_10_percent}/{len(cases)} ({within_10_percent/len(cases)*100:.1f}%)")
    
    # Success evaluation
    print("\n" + "=" * 70)
    print("EVALUATION:")
    if mean_abs_error < 50 and mean_pct_error < 10:
        print("✅ EXCELLENT: The optimized calculator achieves good accuracy!")
        print("   This implementation should perform well on private cases.")
    elif mean_abs_error < 100 and mean_pct_error < 15:
        print("⚠️  GOOD: The calculator is reasonably accurate.")
        print("   Further optimization may improve results.")
    else:
        print("❌ NEEDS IMPROVEMENT: Accuracy is still below target.")
        print("   Consider more sophisticated modeling approaches.")
    
    return mean_abs_error, mean_pct_error


if __name__ == "__main__":
    test_optimized()