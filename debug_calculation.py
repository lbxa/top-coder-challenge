#!/usr/bin/env python3
"""
Debug a specific calculation to understand where the error comes from
"""

import json
from main import calculate_reimbursement
from components.per_diem.per_diem import PerDiemCalculator
from components.mileage.mileage import MileageCalculator
from components.receipts import ReceiptProcessor
from components.bonuses.bonuses import BonusCalculator
from components.bugs.bugs import BugProcessor

def debug_case(case_num=None, days=None, miles=None, receipts=None):
    """Debug a specific case or custom values"""
    
    if case_num is not None:
        # Load from public cases
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        
        case = cases[case_num]
        inp = case['input']
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        print(f"Case {case_num}: {days} days, {miles} miles, ${receipts:.2f} receipts")
        print(f"Expected: ${expected:.2f}")
    else:
        print(f"Custom case: {days} days, {miles} miles, ${receipts:.2f} receipts")
        expected = None
    
    print("\n" + "="*50)
    print("COMPONENT BREAKDOWN")
    print("="*50)
    
    # Initialize calculators
    per_diem_calc = PerDiemCalculator()
    mileage_calc = MileageCalculator()
    receipt_processor = ReceiptProcessor()
    bonus_calc = BonusCalculator()
    bug_processor = BugProcessor()
    
    # Calculate each component
    per_diem_pay = per_diem_calc.calculate(days)
    print(f"\n1. Per Diem: ${per_diem_pay:.2f}")
    print(f"   - {days} days × $100/day = ${per_diem_pay:.2f}")
    
    mileage_pay = mileage_calc.calculate(miles)
    print(f"\n2. Mileage: ${mileage_pay:.2f}")
    if miles <= 100:
        print(f"   - {miles} miles × $0.58/mile = ${mileage_pay:.2f}")
    else:
        tier1 = 100 * 0.58
        tier2_miles = miles - 100
        tier2 = tier2_miles * 0.45
        print(f"   - First 100 miles × $0.58 = ${tier1:.2f}")
        print(f"   - Next {tier2_miles} miles × $0.45 = ${tier2:.2f}")
        print(f"   - Total: ${tier1 + tier2:.2f}")
    
    receipt_pay = receipt_processor.process(days, receipts)
    print(f"\n3. Receipts: ${receipt_pay:.2f}")
    receipts_per_day = receipts / days if days > 0 else 0
    print(f"   - Original amount: ${receipts:.2f} (${receipts_per_day:.2f}/day)")
    
    # Check penalties
    if 1 <= days <= 3 and receipts_per_day > 75:
        penalty = (receipts_per_day - 75) * days * 0.5
        print(f"   - Short trip penalty: -${penalty:.2f}")
    elif 4 <= days <= 7 and receipts_per_day > 120:
        penalty = (receipts_per_day - 120) * days * 0.75
        print(f"   - Medium trip penalty: -${penalty:.2f}")
    elif days >= 8 and receipts_per_day > 90:
        penalty = (receipts_per_day - 90) * days * 1.0
        print(f"   - Long trip penalty: -${penalty:.2f}")
    
    if 0 < receipts and receipts_per_day < 20:
        print(f"   - Small receipt penalty: -$50.00")
    
    print(f"   - Final receipt amount: ${receipt_pay:.2f}")
    
    bonus_amount = bonus_calc.calculate_all_bonuses(days, miles, receipts)
    print(f"\n4. Bonuses: ${bonus_amount:.2f}")
    
    # Check each bonus
    if days == 5:
        print(f"   - 5-day bonus: $75.00")
    
    miles_per_day = miles / days if days > 0 else 0
    if 180 <= miles_per_day <= 220:
        print(f"   - Efficiency bonus: $65.00")
    
    bug_adjustment = bug_processor.apply_bugs(receipts)
    print(f"\n5. Bug adjustments: ${bug_adjustment:.2f}")
    
    cents = int((receipts * 100) % 100)
    if cents == 49 or cents == 99:
        print(f"   - Cents bug (ends in .{cents}): $7.50")
    
    # Total
    total = per_diem_pay + mileage_pay + receipt_pay + bonus_amount + bug_adjustment
    print(f"\n" + "="*50)
    print(f"TOTAL: ${total:.2f}")
    
    if expected is not None:
        error = total - expected
        print(f"Expected: ${expected:.2f}")
        print(f"Error: ${error:+.2f}")
        
        # Try to understand the error
        print(f"\n" + "="*50)
        print("ERROR ANALYSIS")
        print("="*50)
        
        # What would make sense?
        base_components = per_diem_pay + mileage_pay
        remaining = expected - base_components
        print(f"\nIf we assume per diem and mileage are correct:")
        print(f"  Base (per diem + mileage): ${base_components:.2f}")
        print(f"  Remaining for receipts/bonuses/bugs: ${remaining:.2f}")
        
        # Check if receipts might have a different coverage
        if receipts > 0:
            receipt_coverage = remaining / receipts
            print(f"  Implied receipt coverage: {receipt_coverage:.1%}")

# Debug some high-error cases
if __name__ == "__main__":
    print("Debugging high-error cases...")
    print("\n" + "#"*70 + "\n")
    
    # Case 520: 14 days, 481 miles, $939.99 receipts
    debug_case(519)  # 0-indexed
    
    print("\n" + "#"*70 + "\n")
    
    # Case 367: 11 days, 740 miles, $1171.99 receipts
    debug_case(366)  # 0-indexed