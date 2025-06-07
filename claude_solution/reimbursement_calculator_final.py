#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement Calculator - Final Version
Based on comprehensive analysis of all patterns
"""

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement matching the legacy system behavior.
    
    Key patterns discovered:
    1. Receipt amount drives most of the calculation with complex ratios
    2. Cents bug (.49/.99) applies different penalties based on receipt range
    3. Per-day rates vary significantly by trip duration
    4. Mileage has modest impact
    """
    
    # Check for cents bug
    cents = round((total_receipts_amount * 100) % 100)
    has_cents_bug = cents in [49, 99]
    
    # Start with receipt-based calculation
    # Using piecewise function based on ratio analysis
    if total_receipts_amount < 5:
        base = 200 + total_receipts_amount * 30
    elif total_receipts_amount < 10:
        base = 150 + total_receipts_amount * 25
    elif total_receipts_amount < 20:
        base = 100 + total_receipts_amount * 20
    elif total_receipts_amount < 50:
        base = 300 + total_receipts_amount * 10
    elif total_receipts_amount < 100:
        base = 500 + total_receipts_amount * 3
    elif total_receipts_amount < 200:
        base = 650 + total_receipts_amount * 1.8
    elif total_receipts_amount < 500:
        base = 800 + total_receipts_amount * 1.1
    elif total_receipts_amount < 1000:
        base = 500 + total_receipts_amount * 1.0
    elif total_receipts_amount < 1500:
        base = 300 + total_receipts_amount * 0.95
    elif total_receipts_amount < 2000:
        base = 200 + total_receipts_amount * 0.85
    else:
        base = 100 + total_receipts_amount * 0.72
    
    # Add per diem component based on trip duration
    if trip_duration_days == 1:
        # 1-day trips average $873
        per_diem = 200
    elif trip_duration_days == 2:
        # 2-day trips average $1046 total
        per_diem = trip_duration_days * 150
    elif trip_duration_days == 3:
        # 3-day trips average $1010 total
        per_diem = trip_duration_days * 110
    elif trip_duration_days == 4:
        per_diem = trip_duration_days * 105
    elif trip_duration_days == 5:
        # 5-day bonus
        per_diem = trip_duration_days * 100
    elif trip_duration_days <= 7:
        per_diem = trip_duration_days * 95
    elif trip_duration_days <= 10:
        per_diem = trip_duration_days * 85
    elif trip_duration_days <= 12:
        per_diem = trip_duration_days * 80
    else:
        per_diem = trip_duration_days * 75
    
    # Mileage component (relatively small impact)
    if miles_traveled < 100:
        mileage = miles_traveled * 0.20
    elif miles_traveled < 300:
        mileage = 20 + (miles_traveled - 100) * 0.15
    elif miles_traveled < 600:
        mileage = 50 + (miles_traveled - 300) * 0.12
    elif miles_traveled < 1000:
        mileage = 86 + (miles_traveled - 600) * 0.10
    else:
        mileage = 126 + (miles_traveled - 1000) * 0.08
    
    # Combine components
    reimbursement = base + per_diem + mileage
    
    # Apply cents bug penalty - varies by receipt amount!
    if has_cents_bug:
        if total_receipts_amount < 100:
            # Low receipts: moderate penalty
            reimbursement *= 0.75
        elif total_receipts_amount < 500:
            # Medium receipts: stronger penalty
            reimbursement *= 0.55
        elif total_receipts_amount < 1000:
            # High receipts: severe penalty
            reimbursement *= 0.40
        else:
            # Very high receipts: extreme penalty
            reimbursement *= 0.30
    
    # Special adjustments for edge cases
    # Very low receipts with short trips
    if total_receipts_amount < 10 and trip_duration_days <= 2:
        reimbursement = max(reimbursement, 120)
    
    # 1-day trips have high variance - adjust based on other factors
    if trip_duration_days == 1:
        if total_receipts_amount > 1000:
            reimbursement *= 0.85
        elif total_receipts_amount < 100:
            reimbursement *= 1.2
    
    # Long trips with very high receipts are capped
    if trip_duration_days >= 12 and total_receipts_amount > 2000:
        max_allowed = total_receipts_amount * 0.78 + 200
        reimbursement = min(reimbursement, max_allowed)
    
    return round(reimbursement, 2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: ./reimbursement_calculator_final.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    try:
        trip_duration = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        result = calculate_reimbursement(trip_duration, miles, receipts)
        print(f"{result:.2f}")
        
    except (ValueError, TypeError) as e:
        print(f"Error: Invalid input - {e}")
        sys.exit(1)