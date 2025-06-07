#!/usr/bin/env python3
"""
Simple robust calculator based on observed patterns
Uses direct formulas discovered from data analysis
"""

import random


def calculate_reimbursement(trip_duration_days: int, miles_traveled: float, 
                           total_receipts_amount: float) -> float:
    """
    Calculate reimbursement using simplified robust model.
    Based on patterns discovered in clustering analysis.
    """
    
    # Handle edge cases
    if trip_duration_days == 0:
        return round(50.0 + miles_traveled * 0.4 + total_receipts_amount * 0.5, 2)
    
    # Extract features
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Base calculation components
    
    # 1. Per diem calculation with discovered patterns
    if trip_duration_days == 5:
        # Special 5-day bonus confirmed
        base_per_diem = 115.0 * trip_duration_days
    elif trip_duration_days == 1:
        # Single day trips get slightly less
        base_per_diem = 95.0 * trip_duration_days
    elif trip_duration_days >= 7:
        # Long trips get reduced per diem
        base_per_diem = 98.0 * trip_duration_days
    else:
        # Standard rate
        base_per_diem = 100.0 * trip_duration_days
    
    # 2. Mileage calculation with simplified tiers
    if miles_traveled <= 100:
        mileage_reimb = miles_traveled * 0.58
    elif miles_traveled <= 300:
        mileage_reimb = 100 * 0.58 + (miles_traveled - 100) * 0.52
    elif miles_traveled <= 600:
        mileage_reimb = 100 * 0.58 + 200 * 0.52 + (miles_traveled - 300) * 0.47
    elif miles_traveled <= 1000:
        mileage_reimb = 100 * 0.58 + 200 * 0.52 + 300 * 0.47 + (miles_traveled - 600) * 0.42
    else:
        mileage_reimb = 100 * 0.58 + 200 * 0.52 + 300 * 0.47 + 400 * 0.42 + (miles_traveled - 1000) * 0.38
    
    # 3. Efficiency adjustment
    efficiency_mult = 1.0
    if 180 <= miles_per_day <= 220:
        # Kevin's sweet spot confirmed
        efficiency_mult = 1.08
    elif miles_per_day > 300:
        # High efficiency penalty (not actually doing business)
        efficiency_mult = 0.95
    elif miles_per_day < 50 and trip_duration_days >= 3:
        # Low activity penalty
        efficiency_mult = 0.92
    
    # 4. Receipt reimbursement with observed patterns
    if total_receipts_amount == 0:
        receipt_reimb = 0
    elif total_receipts_amount < 20:
        # Very small receipts get poor coverage
        receipt_reimb = total_receipts_amount * 0.65
    elif total_receipts_amount < 50:
        # Small receipt penalty
        receipt_reimb = total_receipts_amount * 0.80
    elif total_receipts_amount <= 600:
        # Optimal receipt range
        receipt_reimb = total_receipts_amount * 0.92
    elif total_receipts_amount <= 1200:
        # Diminishing returns start
        receipt_reimb = 600 * 0.92 + (total_receipts_amount - 600) * 0.75
    else:
        # Heavy penalty for high spending
        receipt_reimb = 600 * 0.92 + 600 * 0.75 + (total_receipts_amount - 1200) * 0.50
    
    # 5. Calculate base total
    base_total = base_per_diem + mileage_reimb * efficiency_mult + receipt_reimb
    
    # 6. Apply trip-type adjustments based on clustering patterns
    trip_mult = 1.0
    
    # Road warrior pattern (high mileage, short trip)
    if miles_per_day > 350 and trip_duration_days <= 3:
        trip_mult = 1.05
    
    # 5-day optimal business travel (Kevin's pattern)
    elif trip_duration_days == 5 and 150 <= miles_per_day <= 250 and receipts_per_day < 120:
        trip_mult = 1.12
    
    # Extended low-activity trips
    elif trip_duration_days >= 7 and miles_per_day < 120:
        trip_mult = 0.90
    
    # High spending trips
    elif receipts_per_day > 150 or (total_receipts_amount > 800 and trip_duration_days <= 3):
        trip_mult = 0.85
    
    # Local trips
    elif miles_traveled < 80 and trip_duration_days <= 2 and receipts_per_day < 60:
        trip_mult = 0.94
    
    # Apply trip multiplier
    total = base_total * trip_mult
    
    # 7. Add controlled randomness (system noise)
    # Use deterministic seed for consistency
    noise_seed = int((trip_duration_days * 1000 + miles_traveled * 10 + total_receipts_amount * 100) % 10000)
    random.seed(noise_seed)
    noise_factor = random.uniform(0.99, 1.01)  # ±1% noise
    total *= noise_factor
    
    # 8. Magic cents bug (confirmed pattern)
    cents = int(round(total_receipts_amount * 100)) % 100
    if cents == 49 or cents == 99:
        total += random.uniform(3, 6)
    
    return round(total, 2)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        (3, 93, 1.42),      # From public cases
        (5, 900, 450),      # 5-day high mileage
        (1, 55, 3.60),      # Short local
        (8, 400, 1200),     # Extended high-spend
        (5, 200, 100),      # 5-day optimal (Kevin's sweet spot)
        (2, 500, 200),      # Road warrior
        (10, 300, 2000),    # Long trip high spend
    ]
    
    print("Simple Robust Calculator Test:")
    print("-" * 60)
    
    for days, miles, receipts in test_cases:
        result = calculate_reimbursement(days, miles, receipts)
        mpd = miles / days if days > 0 else 0
        rpd = receipts / days if days > 0 else 0
        
        print(f"Days: {days}, Miles: {miles:.0f}, Receipts: ${receipts:.2f}")
        print(f"  Miles/day: {mpd:.1f}, Receipts/day: ${rpd:.2f}")
        print(f"  → Reimbursement: ${result:.2f}")
        print()