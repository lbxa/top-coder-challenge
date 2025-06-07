#!/usr/bin/env python3
"""
Re-analyze interviews to extract REAL patterns vs red herrings
"""

print("=== INTERVIEW PATTERN ANALYSIS ===\n")

print("MARCUS (Sales):")
print("✓ 5-6 day trips have sweet spot - CONFIRMED by data")
print("✓ High mileage trips (300+) don't scale linearly - CONFIRMED")
print("✓ Receipt caps/penalties exist - CONFIRMED") 
print("✗ Monthly quotas - NO EVIDENCE (red herring)")
print("✗ Submission day matters - NO EVIDENCE (red herring)")
print("? Quarterly patterns (Q4 generous) - CANNOT VERIFY")

print("\nLISA (Accounting):")
print("✓ $100/day baseline - ROUGHLY CONFIRMED")
print("✓ 5-day trips get bonus - CONFIRMED by data")
print("✓ Mileage is tiered, first 100mi ~58¢ - CONFIRMED pattern exists")
print("✓ Medium-high receipts ($600-800) get good treatment - CONFIRMED")
print("✓ Low receipts get penalized - CONFIRMED")
print("✓ Rounding bug for .49/.99 - CONFIRMED as PENALTY not bonus")
print("✗ Seasonal variations - NO CLEAR PATTERN")

print("\nDAVE (Marketing):")
print("✓ Small receipts hurt reimbursement - CONFIRMED")
print("✗ City-specific rates - NO EVIDENCE")
print("✗ Lunar cycles - DEFINITELY RED HERRING")

print("\nJENNIFER (HR):")
print("✓ 4-6 day sweet spot - PARTIALLY CONFIRMED (5 days yes)")
print("✓ Small receipts should be avoided - CONFIRMED")
print("? New vs experienced employees - CANNOT VERIFY")

print("\nKEVIN (Procurement):")
print("✓ 6 calculation paths/clusters - CONFIRMED!")
print("✓ Efficiency matters (but claimed 180-220 bonus) - ACTUALLY A PENALTY!")
print("✓ Optimal spending ranges by trip length - CONFIRMED pattern exists")
print("✗ Tuesday submissions - RED HERRING")
print("✗ Lunar cycles - RED HERRING")
print("✗ User history/profiling - CANNOT VERIFY")

print("\n=== KEY INSIGHTS TO IMPLEMENT ===")
print("1. Mileage tiers: Need to refine rates (Lisa mentioned 58¢ for first 100)")
print("2. Receipt sweet spots: $600-800 should get better treatment")
print("3. 5-day bonus: Should be more explicit")
print("4. Low receipt penalty: Already implemented")
print("5. Efficiency 180-220: Is a PENALTY not bonus (Kevin was wrong)")

print("\n=== PATTERNS TO IGNORE (RED HERRINGS) ===")
print("- Lunar cycles / day of week")
print("- Seasonal / quarterly variations")
print("- City or department specific rules")
print("- User history tracking")
print("- Submission timing")