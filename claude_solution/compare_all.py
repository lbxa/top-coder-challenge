#!/usr/bin/env python3
"""
Compare all calculator implementations and select the best
"""

import json
import statistics
import sys


def test_calculator(module_name: str, cases: list) -> dict:
    """Test a calculator module and return statistics."""
    # Import the module
    if module_name == 'reimbursement_calculator':
        from reimbursement_calculator import calculate_reimbursement
    elif module_name == 'reimbursement_calculator_optimized':
        from reimbursement_calculator_optimized import calculate_reimbursement
    elif module_name == 'advanced_calculator':
        from advanced_calculator import calculate_reimbursement
    elif module_name == 'reimbursement_calculator_final':
        from reimbursement_calculator_final import calculate_reimbursement
    elif module_name == 'simple_robust_calculator':
        from simple_robust_calculator import calculate_reimbursement
    else:
        raise ValueError(f"Unknown module: {module_name}")
    
    errors = []
    absolute_errors = []
    percent_errors = []
    
    for case in cases:
        input_data = case['input']
        expected = case['expected_output']
        
        try:
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
        except Exception as e:
            print(f"Error in {module_name}: {e}")
            absolute_errors.append(1000)  # Large penalty for errors
            percent_errors.append(100)
    
    # Calculate statistics
    return {
        'module': module_name,
        'mean_abs_error': statistics.mean(absolute_errors),
        'median_abs_error': statistics.median(absolute_errors),
        'max_abs_error': max(absolute_errors),
        'mean_pct_error': statistics.mean(percent_errors),
        'median_pct_error': statistics.median(percent_errors),
        'within_10': sum(1 for e in absolute_errors if e <= 10),
        'within_50': sum(1 for e in absolute_errors if e <= 50),
        'within_10_pct': sum(1 for e in percent_errors if e <= 10)
    }


def main():
    """Compare all implementations."""
    # Load public cases
    with open('../public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("Comparing All Calculator Implementations")
    print("=" * 80)
    print(f"Testing on {len(cases)} public cases\n")
    
    # Test all implementations
    modules = [
        'reimbursement_calculator',
        'reimbursement_calculator_optimized',
        'advanced_calculator',
        'reimbursement_calculator_final',
        'simple_robust_calculator'
    ]
    
    results = []
    for module in modules:
        print(f"Testing {module}...", end='', flush=True)
        try:
            stats = test_calculator(module, cases)
            results.append(stats)
            print(" Done")
        except Exception as e:
            print(f" Failed: {e}")
    
    # Sort by mean absolute error
    results.sort(key=lambda x: x['mean_abs_error'])
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS (sorted by mean absolute error)")
    print("=" * 80)
    
    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['module']}")
        print(f"   Mean absolute error: ${result['mean_abs_error']:.2f}")
        print(f"   Median absolute error: ${result['median_abs_error']:.2f}")
        print(f"   Max absolute error: ${result['max_abs_error']:.2f}")
        print(f"   Mean percentage error: {result['mean_pct_error']:.1f}%")
        print(f"   Median percentage error: {result['median_pct_error']:.1f}%")
        print(f"   Within $10: {result['within_10']}/{len(cases)} ({result['within_10']/len(cases)*100:.1f}%)")
        print(f"   Within $50: {result['within_50']}/{len(cases)} ({result['within_50']/len(cases)*100:.1f}%)")
        print(f"   Within 10%: {result['within_10_pct']}/{len(cases)} ({result['within_10_pct']/len(cases)*100:.1f}%)")
    
    # Recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    best = results[0]
    print(f"\nBest implementation: {best['module']}")
    print(f"Mean error: ${best['mean_abs_error']:.2f} ({best['mean_pct_error']:.1f}%)")
    
    if best['mean_abs_error'] < 50:
        print("\n✅ EXCELLENT: This implementation should work well for the private cases!")
    elif best['mean_abs_error'] < 100:
        print("\n⚠️  GOOD: This implementation is reasonably accurate.")
    else:
        print("\n❌ The best implementation still has high error.")
        print("   Consider further optimization or different approaches.")
    
    # Save best module name
    with open('best_calculator.txt', 'w') as f:
        f.write(best['module'])
    
    print(f"\nBest calculator module saved to: best_calculator.txt")


if __name__ == "__main__":
    main()