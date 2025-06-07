#!/usr/bin/env python3
"""Analyze the relationship between inputs and outputs"""

import json

with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Analyze reimbursement to receipt ratios
ratios = []
for case in cases:
    inp = case['input']
    out = case['expected_output']
    
    if inp['total_receipts_amount'] > 0:
        ratio = out / inp['total_receipts_amount']
        ratios.append({
            'ratio': ratio,
            'receipts': inp['total_receipts_amount'],
            'reimbursement': out,
            'days': inp['trip_duration_days'],
            'miles': inp['miles_traveled']
        })

# Sort by receipts amount
ratios.sort(key=lambda x: x['receipts'])

print("=== REIMBURSEMENT TO RECEIPT RATIOS ===")
print("\nLowest receipt amounts:")
for r in ratios[:10]:
    print(f"Receipts: ${r['receipts']:7.2f} → Reimb: ${r['reimbursement']:7.2f} (Ratio: {r['ratio']:5.2f})")

print("\nHighest receipt amounts:")
for r in ratios[-10:]:
    print(f"Receipts: ${r['receipts']:7.2f} → Reimb: ${r['reimbursement']:7.2f} (Ratio: {r['ratio']:5.2f})")

# Group by receipt ranges
ranges = [(0, 100), (100, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 3000)]
print("\n=== AVERAGE RATIOS BY RECEIPT RANGE ===")
for low, high in ranges:
    range_ratios = [r['ratio'] for r in ratios if low <= r['receipts'] < high]
    if range_ratios:
        avg_ratio = sum(range_ratios) / len(range_ratios)
        count = len(range_ratios)
        print(f"${low:4d}-${high:4d}: Avg ratio = {avg_ratio:.3f} ({count} cases)")

# Check for .49/.99 pattern
print("\n=== CENTS ENDING ANALYSIS ===")
normal_reimb = []
special_reimb = []

for case in cases:
    inp = case['input']
    out = case['expected_output']
    cents = round((inp['total_receipts_amount'] * 100) % 100)
    
    if cents in [49, 99]:
        special_reimb.append(out)
    else:
        normal_reimb.append(out)

print(f"Normal endings: {len(normal_reimb)} cases, avg reimbursement: ${sum(normal_reimb)/len(normal_reimb):.2f}")
print(f"Special endings (.49/.99): {len(special_reimb)} cases, avg reimbursement: ${sum(special_reimb)/len(special_reimb) if special_reimb else 0:.2f}")
if special_reimb:
    print(f"Difference: ${sum(special_reimb)/len(special_reimb) - sum(normal_reimb)/len(normal_reimb):.2f}")

# Analyze per-day rates
print("\n=== PER-DAY REIMBURSEMENT RATES ===")
for days in range(1, 15):
    day_cases = [c for c in cases if c['input']['trip_duration_days'] == days]
    if day_cases:
        reimbs = [c['expected_output'] for c in day_cases]
        avg_reimb = sum(reimbs) / len(reimbs)
        per_day = avg_reimb / days
        print(f"{days:2d} days: {len(day_cases):3d} cases, avg total: ${avg_reimb:7.2f}, per day: ${per_day:6.2f}")