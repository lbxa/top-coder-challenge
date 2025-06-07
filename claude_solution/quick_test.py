#!/usr/bin/env python3
"""Quick test specific problematic cases"""

from calculator_v2 import calculate_reimbursement

# Test cases that had high errors
test_cases = [
    # Case 389: 14d, 296mi, $485.68 → Expected: $924.90
    {"days": 14, "miles": 296, "receipts": 485.68, "expected": 924.90},
    # Case 633: 14d, 68mi, $438.96 → Expected: $866.76
    {"days": 14, "miles": 68, "receipts": 438.96, "expected": 866.76},
    # Case 513: 8d, 1025mi, $1031.33 → Expected: $2214.64
    {"days": 8, "miles": 1025, "receipts": 1031.33, "expected": 2214.64},
    # Case 104: 1d, 276.85mi, $485.54 → Expected: $361.66
    {"days": 1, "miles": 276.85, "receipts": 485.54, "expected": 361.66},
    # Case 663: 1d, 292mi, $449.83 → Expected: $363.02
    {"days": 1, "miles": 292, "receipts": 449.83, "expected": 363.02},
]

print("=== TESTING PROBLEMATIC CASES ===")
for i, tc in enumerate(test_cases):
    calc = calculate_reimbursement(tc["days"], tc["miles"], tc["receipts"])
    error = abs(calc - tc["expected"])
    print(f"\nCase {i+1}:")
    print(f"  Input: {tc['days']}d, {tc['miles']}mi, ${tc['receipts']:.2f}")
    print(f"  Expected: ${tc['expected']:.2f}")
    print(f"  Calculated: ${calc:.2f}")
    print(f"  Error: ${error:.2f} ({error/tc['expected']*100:.1f}%)")
    
print("\n=== ANALYSIS ===")
print("1. 14-day trips with medium receipts ($400-500) are getting ~$1700 but expect ~$900")
print("2. 8-day trip with $1031 receipts gets $1431 but expects $2215")
print("3. 1-day trips with $400-500 receipts get ~$1300 but expect ~$360")
print("   → Need much lower multipliers for 1-day trips in this range")