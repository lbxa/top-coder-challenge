#!/usr/bin/env python3
"""
Pattern analysis without external dependencies
"""

import json
import math

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Analyze patterns
print("=== COMPREHENSIVE PATTERN ANALYSIS ===\n")

# 1. Analyze receipt ranges and their behavior
receipt_ranges = [
    (0, 20, "very_low"),
    (20, 50, "low"),
    (50, 100, "medium_low"),
    (100, 200, "medium"),
    (200, 500, "medium_high"),
    (500, 1000, "high"),
    (1000, 1500, "very_high"),
    (1500, 2000, "extreme_high"),
    (2000, 3000, "ultra_high")
]

print("=== RECEIPT RANGE ANALYSIS ===")
for low, high, name in receipt_ranges:
    range_cases = []
    for case in cases:
        receipt = case['input']['total_receipts_amount']
        if low <= receipt < high:
            range_cases.append(case)
    
    if range_cases:
        # Calculate statistics
        ratios = []
        per_day_rates = []
        for case in range_cases:
            inp = case['input']
            out = case['expected_output']
            if inp['total_receipts_amount'] > 0:
                ratios.append(out / inp['total_receipts_amount'])
            per_day_rates.append(out / inp['trip_duration_days'])
        
        avg_ratio = sum(ratios) / len(ratios) if ratios else 0
        avg_per_day = sum(per_day_rates) / len(per_day_rates)
        
        print(f"\n{name.upper()} (${low}-${high}): {len(range_cases)} cases")
        print(f"  Avg reimbursement/receipt ratio: {avg_ratio:.3f}")
        print(f"  Avg reimbursement per day: ${avg_per_day:.2f}")
        
        # Analyze by trip duration
        by_duration = {}
        for case in range_cases:
            dur = case['input']['trip_duration_days']
            if dur not in by_duration:
                by_duration[dur] = []
            by_duration[dur].append(case['expected_output'])
        
        print("  By trip duration:")
        for dur in sorted(by_duration.keys()):
            avg = sum(by_duration[dur]) / len(by_duration[dur])
            print(f"    {dur} days: {len(by_duration[dur])} cases, avg ${avg:.2f}")

# 2. Analyze cents bug impact
print("\n\n=== CENTS BUG ANALYSIS ===")
normal_cases = []
cents_bug_cases = []

for case in cases:
    cents = round((case['input']['total_receipts_amount'] * 100) % 100)
    if cents in [49, 99]:
        cents_bug_cases.append(case)
    else:
        normal_cases.append(case)

print(f"Normal cases: {len(normal_cases)}")
print(f"Cents bug cases: {len(cents_bug_cases)}")

# Analyze cents bug by receipt range
for low, high, name in receipt_ranges:
    bug_in_range = []
    normal_in_range = []
    
    for case in cents_bug_cases:
        if low <= case['input']['total_receipts_amount'] < high:
            bug_in_range.append(case)
    
    for case in normal_cases:
        if low <= case['input']['total_receipts_amount'] < high:
            normal_in_range.append(case)
    
    if bug_in_range and normal_in_range:
        avg_bug = sum(c['expected_output'] for c in bug_in_range) / len(bug_in_range)
        avg_normal = sum(c['expected_output'] for c in normal_in_range) / len(normal_in_range)
        penalty_factor = avg_bug / avg_normal if avg_normal > 0 else 0
        
        print(f"\n{name}: ")
        print(f"  Bug cases: {len(bug_in_range)}, avg ${avg_bug:.2f}")
        print(f"  Normal cases: {len(normal_in_range)}, avg ${avg_normal:.2f}")
        print(f"  Penalty factor: {penalty_factor:.3f}")

# 3. Analyze trip duration patterns
print("\n\n=== TRIP DURATION PATTERNS ===")
for days in range(1, 15):
    day_cases = [c for c in cases if c['input']['trip_duration_days'] == days]
    if day_cases:
        avg_reimb = sum(c['expected_output'] for c in day_cases) / len(day_cases)
        avg_miles = sum(c['input']['miles_traveled'] for c in day_cases) / len(day_cases)
        avg_receipts = sum(c['input']['total_receipts_amount'] for c in day_cases) / len(day_cases)
        
        print(f"\n{days} days: {len(day_cases)} cases")
        print(f"  Avg reimbursement: ${avg_reimb:.2f} (${avg_reimb/days:.2f}/day)")
        print(f"  Avg miles: {avg_miles:.0f} ({avg_miles/days:.0f}/day)")
        print(f"  Avg receipts: ${avg_receipts:.2f} (${avg_receipts/days:.2f}/day)")

# 4. Find interaction patterns
print("\n\n=== INTERACTION PATTERNS ===")

# High efficiency trips (180-220 miles/day)
efficient_trips = []
for case in cases:
    mpd = case['input']['miles_traveled'] / case['input']['trip_duration_days']
    if 180 <= mpd <= 220:
        efficient_trips.append(case)

print(f"\nEfficient trips (180-220 miles/day): {len(efficient_trips)} cases")
if efficient_trips:
    avg_reimb = sum(c['expected_output'] for c in efficient_trips) / len(efficient_trips)
    print(f"  Avg reimbursement: ${avg_reimb:.2f}")
    
    # Compare to similar non-efficient trips
    comparison_trips = []
    for case in cases:
        mpd = case['input']['miles_traveled'] / case['input']['trip_duration_days']
        if 150 <= mpd < 180 or 220 < mpd <= 250:
            comparison_trips.append(case)
    
    if comparison_trips:
        avg_comp = sum(c['expected_output'] for c in comparison_trips) / len(comparison_trips)
        print(f"  Comparison group avg: ${avg_comp:.2f}")
        print(f"  Efficiency bonus factor: {avg_reimb/avg_comp:.3f}")

# 5. Edge cases
print("\n\n=== EDGE CASES ===")

# Very low miles
low_mile_cases = [c for c in cases if c['input']['miles_traveled'] < 20]
print(f"\nVery low miles (<20): {len(low_mile_cases)} cases")
for case in low_mile_cases[:5]:
    inp = case['input']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f} → ${case['expected_output']:.2f}")

# Very high receipts with short trips
edge_cases = []
for case in cases:
    if case['input']['trip_duration_days'] <= 2 and case['input']['total_receipts_amount'] > 2000:
        edge_cases.append(case)

print(f"\nShort trips (<=2d) with high receipts (>$2000): {len(edge_cases)} cases")
for case in edge_cases:
    inp = case['input']
    ratio = case['expected_output'] / inp['total_receipts_amount']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f} → ${case['expected_output']:.2f} (ratio: {ratio:.3f})")

# 6. Look for multiplicative patterns
print("\n\n=== MULTIPLICATIVE PATTERNS ===")

# Calculate correlation between trip_duration * miles and reimbursement
correlations = []
for case in cases:
    inp = case['input']
    interaction = inp['trip_duration_days'] * inp['miles_traveled']
    correlations.append((interaction, case['expected_output']))

# Sort by interaction value
correlations.sort()

# Analyze in buckets
buckets = [(0, 1000), (1000, 5000), (5000, 10000), (10000, 20000), (20000, 50000)]
for low, high in buckets:
    bucket_cases = [(i, r) for i, r in correlations if low <= i < high]
    if bucket_cases:
        avg_interaction = sum(i for i, r in bucket_cases) / len(bucket_cases)
        avg_reimb = sum(r for i, r in bucket_cases) / len(bucket_cases)
        print(f"\nInteraction {low}-{high}: {len(bucket_cases)} cases")
        print(f"  Avg interaction: {avg_interaction:.0f}")
        print(f"  Avg reimbursement: ${avg_reimb:.2f}")
        print(f"  Ratio: {avg_reimb/avg_interaction:.3f}")

print("\n\n=== KEY INSIGHTS FOR CALCULATOR ===")
print("1. Receipt amount dominates with non-linear ratios")
print("2. Cents bug (.49/.99) has varying penalties by receipt range")
print("3. Trip duration affects high receipt ratios significantly")
print("4. Efficiency bonus exists but is modest")
print("5. Edge cases need special handling")
print("6. Interaction effects are real but secondary")