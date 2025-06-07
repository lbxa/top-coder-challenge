#!/usr/bin/env python3
"""Test the V3 calculator against public cases"""

import json
from reimbursement_calculator_v3 import calculate_reimbursement

def test_accuracy():
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    exact_matches = 0
    close_matches = 0
    within_10 = 0
    within_50 = 0
    total_error = 0
    max_error = 0
    errors = []
    
    for i, case in enumerate(public_cases):
        inputs = case['input']
        expected = case['expected_output']
        
        calculated = calculate_reimbursement(
            inputs['trip_duration_days'],
            inputs['miles_traveled'],
            inputs['total_receipts_amount']
        )
        
        error = abs(calculated - expected)
        total_error += error
        
        if error <= 0.01:
            exact_matches += 1
        elif error <= 1.00:
            close_matches += 1
        
        if error <= 10.00:
            within_10 += 1
        if error <= 50.00:
            within_50 += 1
        
        if error > max_error:
            max_error = error
        
        errors.append({
            'case': i,
            'inputs': inputs,
            'expected': expected,
            'calculated': calculated,
            'error': error
        })
    
    # Sort errors by magnitude
    errors.sort(key=lambda x: x['error'], reverse=True)
    
    print(f"=== V3 CALCULATOR TEST RESULTS ===")
    print(f"Total cases: {len(public_cases)}")
    print(f"Exact matches (±$0.01): {exact_matches} ({exact_matches/len(public_cases)*100:.1f}%)")
    print(f"Close matches (±$1.00): {close_matches} ({close_matches/len(public_cases)*100:.1f}%)")
    print(f"Within $10: {within_10} ({within_10/len(public_cases)*100:.1f}%)")
    print(f"Within $50: {within_50} ({within_50/len(public_cases)*100:.1f}%)")
    print(f"Average error: ${total_error/len(public_cases):.2f}")
    print(f"Maximum error: ${max_error:.2f}")
    print(f"Total score: {total_error:.0f}")
    
    print(f"\n=== TOP 10 ERRORS ===")
    for i, err in enumerate(errors[:10]):
        print(f"\n{i+1}. Case {err['case']}: Error ${err['error']:.2f}")
        print(f"   Inputs: {err['inputs']['trip_duration_days']}d, {err['inputs']['miles_traveled']}mi, ${err['inputs']['total_receipts_amount']:.2f}")
        print(f"   Expected: ${err['expected']:.2f}, Calculated: ${err['calculated']:.2f}")
        
        # Check for patterns
        cents = round((err['inputs']['total_receipts_amount'] * 100) % 100)
        if cents in [49, 99]:
            print(f"   → Has .{cents:02d} ending (cents bug)")
    
    # Find successful matches
    successful = [e for e in errors if e['error'] <= 10.00]
    if successful:
        print(f"\n=== SAMPLE SUCCESSFUL MATCHES (Error ≤ $10) ===")
        print(f"Found {len(successful)} successful matches")
        # Show a diverse sample
        sample_indices = [0, len(successful)//4, len(successful)//2, 3*len(successful)//4, -1]
        for idx in sample_indices:
            if 0 <= idx < len(successful) or idx == -1:
                succ = successful[idx]
                print(f"\nCase {succ['case']}: Error ${succ['error']:.2f}")
                print(f"   Inputs: {succ['inputs']['trip_duration_days']}d, {succ['inputs']['miles_traveled']}mi, ${succ['inputs']['total_receipts_amount']:.2f}")
                print(f"   Expected: ${succ['expected']:.2f}, Calculated: ${succ['calculated']:.2f}")

if __name__ == "__main__":
    test_accuracy()