#!/usr/bin/env python3
"""
Deep analysis of the bugs component to find optimal parameters.

This script performs exhaustive testing of different bug configurations.
"""

import json
import sys
from pathlib import Path
from itertools import combinations
import numpy as np

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from components.bugs.bugs import BugProcessor


def analyze_cents_patterns():
    """Analyze patterns in receipt cents values and their relationship to errors."""
    print("Analyzing Cents Patterns in Test Data")
    print("=" * 60)
    
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Group cases by cents value
    cents_groups = {}
    for case in public_cases:
        receipts = case['input']['total_receipts_amount']
        cents = int((receipts * 100) % 100)
        
        if cents not in cents_groups:
            cents_groups[cents] = []
        cents_groups[cents].append(case)
    
    # Analyze error patterns by cents value
    cents_analysis = []
    
    for cents, cases in cents_groups.items():
        if len(cases) >= 5:  # Only analyze cents values with enough samples
            # Calculate average error for this cents value
            errors = []
            for case in cases:
                # Simple approximation of error without full calculation
                # Using basic per diem + mileage estimate
                estimated = (case['input']['trip_duration_days'] * 100 + 
                           case['input']['miles_traveled'] * 0.58 + 
                           case['input']['total_receipts_amount'] * 0.85)
                error = case['expected_output'] - estimated
                errors.append(error)
            
            avg_error = np.mean(errors)
            std_error = np.std(errors)
            
            cents_analysis.append({
                'cents': cents,
                'count': len(cases),
                'avg_error': avg_error,
                'std_error': std_error
            })
    
    # Sort by average error to find potential bug candidates
    cents_analysis.sort(key=lambda x: x['avg_error'], reverse=True)
    
    print("\nTop 15 Cents Values by Positive Error (potential bug candidates):")
    print(f"{'Cents':>5} | {'Count':>5} | {'Avg Error':>10} | {'Std Dev':>10}")
    print("-" * 40)
    
    for item in cents_analysis[:15]:
        print(f"{item['cents']:>5} | {item['count']:>5} | "
              f"${item['avg_error']:>9.2f} | ${item['std_error']:>9.2f}")
    
    return cents_analysis


def test_all_cents_combinations():
    """Test all reasonable combinations of cents values as bug triggers."""
    print("\n\nTesting All Reasonable Cents Combinations")
    print("=" * 60)
    
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Get cents values that appear frequently enough
    cents_counts = {}
    for case in public_cases:
        cents = int((case['input']['total_receipts_amount'] * 100) % 100)
        cents_counts[cents] = cents_counts.get(cents, 0) + 1
    
    # Consider cents values that appear at least 10 times
    candidate_cents = [c for c, count in cents_counts.items() if count >= 10]
    print(f"Candidate cents values (appearing 10+ times): {sorted(candidate_cents)}")
    
    # Test different combinations
    best_configs = []
    
    # Test single values
    for cents in candidate_cents:
        config = test_cents_configuration([cents], public_cases)
        if config['improvement'] > 0:
            best_configs.append(config)
    
    # Test pairs
    for pair in combinations(candidate_cents, 2):
        config = test_cents_configuration(list(pair), public_cases)
        if config['improvement'] > 0:
            best_configs.append(config)
    
    # Test triples
    for triple in combinations(candidate_cents, 3):
        config = test_cents_configuration(list(triple), public_cases)
        if config['improvement'] > 0:
            best_configs.append(config)
    
    # Sort by improvement
    best_configs.sort(key=lambda x: x['improvement'], reverse=True)
    
    print("\n\nTop 10 Best Configurations:")
    print(f"{'Trigger Values':>20} | {'Bonus':>6} | {'Hits':>5} | {'Improvement':>12}")
    print("-" * 50)
    
    for config in best_configs[:10]:
        trigger_str = str(config['triggers'])
        print(f"{trigger_str:>20} | ${config['bonus']:>5.2f} | "
              f"{config['hits']:>5} | ${config['improvement']:>11.2f}")
    
    return best_configs


def test_cents_configuration(trigger_values, test_cases, bonus_range=(5.0, 10.0)):
    """Test a specific configuration of cents trigger values."""
    best_bonus = None
    best_improvement = -float('inf')
    
    # Test different bonus amounts
    for bonus in np.arange(bonus_range[0], bonus_range[1], 0.5):
        total_adjustment = 0
        hits = 0
        
        for case in test_cases:
            cents = int((case['input']['total_receipts_amount'] * 100) % 100)
            if cents in trigger_values:
                hits += 1
                total_adjustment += bonus
        
        # Simple metric: total adjustment (more sophisticated would consider errors)
        improvement = total_adjustment if hits > 0 else 0
        
        if improvement > best_improvement:
            best_improvement = improvement
            best_bonus = bonus
    
    return {
        'triggers': trigger_values,
        'bonus': best_bonus,
        'hits': hits,
        'improvement': best_improvement
    }


def analyze_other_bug_patterns():
    """Look for other potential bug patterns beyond cents."""
    print("\n\nAnalyzing Other Potential Bug Patterns")
    print("=" * 60)
    
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Pattern 1: Round dollar amounts
    print("\n1. Round Dollar Amounts:")
    round_cases = []
    non_round_cases = []
    
    for case in public_cases:
        receipts = case['input']['total_receipts_amount']
        if receipts == int(receipts):  # Exactly round dollar
            round_cases.append(case)
        else:
            non_round_cases.append(case)
    
    print(f"   Round dollar cases: {len(round_cases)}")
    print(f"   Non-round cases: {len(non_round_cases)}")
    
    # Pattern 2: Palindrome amounts (e.g., 121.21, 434.34)
    print("\n2. Palindrome Amounts:")
    palindrome_cases = []
    
    for case in public_cases:
        amount_str = f"{case['input']['total_receipts_amount']:.2f}".replace('.', '')
        if amount_str == amount_str[::-1] and len(amount_str) >= 3:
            palindrome_cases.append(case)
    
    print(f"   Palindrome cases: {len(palindrome_cases)}")
    if palindrome_cases:
        print("   Examples:", [f"${c['input']['total_receipts_amount']:.2f}" 
                               for c in palindrome_cases[:5]])
    
    # Pattern 3: Powers of 2 or other special numbers
    print("\n3. Special Number Patterns:")
    special_patterns = {
        'power_of_2': [],
        'fibonacci': [],
        'prime_cents': []
    }
    
    # Common Fibonacci numbers
    fibs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    # Common primes
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    for case in public_cases:
        amount = case['input']['total_receipts_amount']
        cents = int((amount * 100) % 100)
        
        # Check if amount is close to power of 2
        for i in range(1, 11):
            if abs(amount - 2**i) < 0.01:
                special_patterns['power_of_2'].append(case)
                break
        
        # Check if cents is Fibonacci
        if cents in fibs:
            special_patterns['fibonacci'].append(case)
        
        # Check if cents is prime
        if cents in primes:
            special_patterns['prime_cents'].append(case)
    
    for pattern, cases in special_patterns.items():
        if cases:
            print(f"   {pattern}: {len(cases)} cases")
    
    # Pattern 4: Repeated digits (e.g., 111.11, 222.22)
    print("\n4. Repeated Digit Amounts:")
    repeated_digit_cases = []
    
    for case in public_cases:
        amount_str = f"{case['input']['total_receipts_amount']:.2f}"
        digits = [d for d in amount_str if d.isdigit()]
        if len(set(digits)) == 1 and len(digits) >= 3:
            repeated_digit_cases.append(case)
    
    print(f"   Repeated digit cases: {len(repeated_digit_cases)}")
    if repeated_digit_cases:
        print("   Examples:", [f"${c['input']['total_receipts_amount']:.2f}" 
                               for c in repeated_digit_cases[:5]])
    
    # Pattern 5: Sequential patterns (e.g., 123.45, 234.56)
    print("\n5. Sequential Patterns:")
    sequential_cases = []
    
    for case in public_cases:
        amount_str = f"{case['input']['total_receipts_amount']:06.2f}".replace('.', '')
        digits = [int(d) for d in amount_str if d.isdigit()]
        
        # Check for ascending sequence
        is_sequential = True
        for i in range(len(digits) - 1):
            if digits[i+1] != (digits[i] + 1) % 10:
                is_sequential = False
                break
        
        if is_sequential and len(digits) >= 3:
            sequential_cases.append(case)
    
    print(f"   Sequential cases: {len(sequential_cases)}")


def find_optimal_bug_parameters():
    """Find the truly optimal bug parameters through comprehensive testing."""
    print("\n\nFinding Optimal Bug Parameters")
    print("=" * 60)
    
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Test a comprehensive range of cents values and bonuses
    all_cents = list(range(100))
    bonus_range = np.arange(0.5, 15.0, 0.5)
    
    best_config = None
    best_total_error = float('inf')
    
    print("Testing comprehensive parameter space...")
    print("(This may take a moment)")
    
    # Test each cents value individually with different bonuses
    results = []
    
    for cents in all_cents:
        for bonus in bonus_range:
            # Calculate what the error would be with this configuration
            # This is a simplified calculation - in reality we'd need the full calculator
            total_error = 0
            hits = 0
            
            for case in public_cases:
                case_cents = int((case['input']['total_receipts_amount'] * 100) % 100)
                
                # Simplified reimbursement calculation
                base_estimate = (case['input']['trip_duration_days'] * 100 + 
                               case['input']['miles_traveled'] * 0.58 + 
                               case['input']['total_receipts_amount'] * 0.85)
                
                if case_cents == cents:
                    base_estimate += bonus
                    hits += 1
                
                error = abs(case['expected_output'] - base_estimate)
                total_error += error
            
            if hits > 10:  # Only consider if it affects enough cases
                results.append({
                    'cents': [cents],
                    'bonus': bonus,
                    'total_error': total_error,
                    'hits': hits,
                    'avg_error': total_error / len(public_cases)
                })
    
    # Sort by total error
    results.sort(key=lambda x: x['total_error'])
    
    print("\n\nTop 20 Single-Cents Configurations:")
    print(f"{'Cents':>6} | {'Bonus':>6} | {'Hits':>5} | {'Avg Error':>10}")
    print("-" * 35)
    
    for result in results[:20]:
        print(f"{result['cents'][0]:>6} | ${result['bonus']:>5.2f} | "
              f"{result['hits']:>5} | ${result['avg_error']:>9.2f}")
    
    # Now test the current configuration [49, 99] with different bonuses
    print("\n\nOptimizing Current Configuration [49, 99]:")
    print(f"{'Bonus':>6} | {'Hits':>5} | {'Avg Error':>10}")
    print("-" * 25)
    
    current_results = []
    for bonus in bonus_range:
        total_error = 0
        hits = 0
        
        for case in public_cases:
            case_cents = int((case['input']['total_receipts_amount'] * 100) % 100)
            
            base_estimate = (case['input']['trip_duration_days'] * 100 + 
                           case['input']['miles_traveled'] * 0.58 + 
                           case['input']['total_receipts_amount'] * 0.85)
            
            if case_cents in [49, 99]:
                base_estimate += bonus
                hits += 1
            
            error = abs(case['expected_output'] - base_estimate)
            total_error += error
        
        avg_error = total_error / len(public_cases)
        current_results.append({
            'bonus': bonus,
            'hits': hits,
            'avg_error': avg_error
        })
        
        print(f"${bonus:>5.2f} | {hits:>5} | ${avg_error:>9.2f}")
    
    # Find best bonus for current configuration
    best_current = min(current_results, key=lambda x: x['avg_error'])
    print(f"\nBest bonus for [49, 99]: ${best_current['bonus']:.2f}")


if __name__ == "__main__":
    cents_analysis = analyze_cents_patterns()
    best_configs = test_all_cents_combinations()
    analyze_other_bug_patterns()
    find_optimal_bug_parameters()