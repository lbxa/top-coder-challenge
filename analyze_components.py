#!/usr/bin/env python3
"""
Analyze components of reimbursement by running our calculator and comparing
"""

import json
import statistics
from main import calculate_reimbursement
from components.per_diem.per_diem import PerDiemCalculator
from components.mileage.mileage import MileageCalculator
from components.receipts import ReceiptProcessor
from components.bonuses.bonuses import BonusCalculator
from components.bugs.bugs import BugProcessor

def analyze_components():
    # Load public cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print(f"Analyzing {len(cases)} test cases")
    print("="*70)
    
    # Initialize calculators
    per_diem_calc = PerDiemCalculator()
    mileage_calc = MileageCalculator()
    receipt_processor = ReceiptProcessor()
    bonus_calc = BonusCalculator()
    bug_processor = BugProcessor()
    
    # Analyze each component's contribution
    errors_by_component = {
        'total': [],
        'per_diem': [],
        'mileage': [],
        'receipts': [],
        'bonuses': [],
        'bugs': []
    }
    
    mileage_analysis = []
    
    for i, case in enumerate(cases):
        inp = case['input']
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        
        # Calculate each component
        per_diem_pay = per_diem_calc.calculate(days)
        mileage_pay = mileage_calc.calculate(miles)
        receipt_pay = receipt_processor.process(days, receipts)
        bonus_amount = bonus_calc.calculate_all_bonuses(days, miles, receipts)
        bug_adjustment = bug_processor.apply_bugs(receipts)
        
        # Total calculation
        calculated = calculate_reimbursement(days, miles, receipts)
        
        # Error analysis
        total_error = abs(calculated - expected)
        errors_by_component['total'].append(total_error)
        
        # Store mileage-specific data
        if miles > 0:
            mileage_analysis.append({
                'miles': miles,
                'days': days,
                'receipts': receipts,
                'expected': expected,
                'calculated': calculated,
                'mileage_component': mileage_pay,
                'error': total_error,
                'miles_per_day': miles / days if days > 0 else 0
            })
    
    # Analyze mileage patterns
    print("\nMILEAGE COMPONENT ANALYSIS")
    print("-"*50)
    
    # Sort by miles and look for patterns
    mileage_analysis.sort(key=lambda x: x['miles'])
    
    # Check if current tier structure is correct
    print("\nChecking current mileage calculation:")
    print(f"Tier 1: 0-100 miles at $0.58/mile")
    print(f"Tier 2: 100+ miles at $0.45/mile")
    
    # Sample some cases to see if mileage calculation is the issue
    print("\nSample calculations vs expectations:")
    samples = [50, 75, 100, 125, 150, 200, 300, 500, 1000]
    
    for target_miles in samples:
        # Find cases near this mileage
        close_cases = [c for c in mileage_analysis 
                      if abs(c['miles'] - target_miles) < 20]
        
        if close_cases:
            # Pick one with minimal other factors
            case = min(close_cases, key=lambda x: x['receipts'])
            
            # Try to isolate mileage effect
            base_reimb = case['expected']
            # Subtract estimated per diem
            base_reimb -= case['days'] * 100
            # Subtract receipts (assuming full coverage for now)
            base_reimb -= case['receipts']
            
            implied_rate = base_reimb / case['miles'] if case['miles'] > 0 else 0
            
            print(f"\nCase near {target_miles} miles:")
            print(f"  Actual: {case['miles']} miles, {case['days']} days, ${case['receipts']:.2f} receipts")
            print(f"  Expected total: ${case['expected']:.2f}")
            print(f"  Our mileage calc: ${case['mileage_component']:.2f}")
            print(f"  Implied mileage rate: ${implied_rate:.3f}/mile")
    
    # Look for patterns in high-error cases
    print("\n" + "="*70)
    print("HIGH ERROR CASES")
    print("="*70)
    
    high_errors = sorted(mileage_analysis, key=lambda x: x['error'], reverse=True)[:10]
    
    print("\nTop 10 highest error cases:")
    for case in high_errors:
        print(f"\nMiles: {case['miles']}, Days: {case['days']}, Receipts: ${case['receipts']:.2f}")
        print(f"  Expected: ${case['expected']:.2f}, Calculated: ${case['calculated']:.2f}")
        print(f"  Error: ${case['error']:.2f}")
        print(f"  Our mileage component: ${case['mileage_component']:.2f}")
    
    # Check if mileage tiers are wrong
    print("\n" + "="*70)
    print("TESTING DIFFERENT MILEAGE STRUCTURES")
    print("="*70)
    
    # Try different tier structures
    test_structures = [
        {'tier1_threshold': 100, 'tier1_rate': 0.58, 'tier2_rate': 0.45},
        {'tier1_threshold': 100, 'tier1_rate': 0.55, 'tier2_rate': 0.40},
        {'tier1_threshold': 150, 'tier1_rate': 0.55, 'tier2_rate': 0.40},
        {'tier1_threshold': 200, 'tier1_rate': 0.50, 'tier2_rate': 0.35},
    ]
    
    for i, params in enumerate(test_structures):
        total_error = 0
        for case in mileage_analysis[:100]:  # Test on subset
            miles = case['miles']
            if miles <= params['tier1_threshold']:
                test_mileage = miles * params['tier1_rate']
            else:
                test_mileage = (params['tier1_threshold'] * params['tier1_rate'] + 
                              (miles - params['tier1_threshold']) * params['tier2_rate'])
            
            # Very rough error estimate (ignoring other components)
            error_contribution = abs(test_mileage - case['mileage_component'])
            total_error += error_contribution
        
        avg_error = total_error / 100
        print(f"\nStructure {i+1}: Threshold={params['tier1_threshold']}, "
              f"Rate1=${params['tier1_rate']}, Rate2=${params['tier2_rate']}")
        print(f"  Average mileage error contribution: ${avg_error:.2f}")

if __name__ == "__main__":
    analyze_components()