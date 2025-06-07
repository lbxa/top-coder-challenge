#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement Calculator - Production Version
Reverse-engineered from 1000 test cases
"""

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement based on comprehensive pattern analysis.
    """
    
    # Check for cents bug first
    cents = round((total_receipts_amount * 100) % 100)
    has_cents_bug = cents in [49, 99]
    
    # Base calculation depends heavily on receipt amount range
    if total_receipts_amount < 20:
        # Very low receipts: use mostly per diem + mileage
        base = trip_duration_days * 100 + miles_traveled * 0.3 + total_receipts_amount * 2
    
    elif total_receipts_amount < 100:
        # Low receipts: declining multiplier
        base = trip_duration_days * 80 + miles_traveled * 0.25 + total_receipts_amount * 5
    
    elif total_receipts_amount < 500:
        # Medium receipts: balanced approach
        base = trip_duration_days * 70 + miles_traveled * 0.2 + total_receipts_amount * 1.5
    
    elif total_receipts_amount < 1000:
        # Medium-high receipts: receipt-focused
        base = trip_duration_days * 60 + miles_traveled * 0.15 + total_receipts_amount * 1.1
    
    elif total_receipts_amount < 2000:
        # High receipts: mostly receipt-based
        base = trip_duration_days * 50 + miles_traveled * 0.1 + total_receipts_amount * 0.9
    
    else:
        # Very high receipts: ratio depends on trip duration
        if trip_duration_days <= 2:
            receipt_ratio = 0.61
        elif trip_duration_days <= 4:
            receipt_ratio = 0.655
        elif trip_duration_days <= 6:
            receipt_ratio = 0.74
        elif trip_duration_days <= 8:
            receipt_ratio = 0.71
        elif trip_duration_days <= 10:
            receipt_ratio = 0.76
        elif trip_duration_days <= 12:
            receipt_ratio = 0.78
        else:
            receipt_ratio = 0.84
        
        base = total_receipts_amount * receipt_ratio + trip_duration_days * 30 + miles_traveled * 0.08
    
    # Special adjustments for 1-day trips
    if trip_duration_days == 1:
        if total_receipts_amount < 100:
            base *= 1.5  # Boost for low receipt 1-day trips
        elif total_receipts_amount > 1500:
            base *= 0.95  # Slight penalty for high receipt 1-day trips
    
    # Apply cents bug penalty
    if has_cents_bug:
        # Analysis showed avg of $566 vs $1373
        if total_receipts_amount < 100:
            base *= 0.7
        elif total_receipts_amount < 500:
            base *= 0.45
        elif total_receipts_amount < 1000:
            base *= 0.35
        elif total_receipts_amount < 2000:
            base *= 0.25
        else:
            # Case 151: 4d, 69mi, $2321.49 → $322 (ratio 0.139)
            base *= 0.18
    
    # Efficiency bonus for optimal miles/day
    miles_per_day = miles_traveled / trip_duration_days
    if 180 <= miles_per_day <= 220:
        base *= 1.02
    
    # Edge case adjustments
    # Very short trip with very low miles and high receipts
    if trip_duration_days <= 2 and miles_traveled < 50 and total_receipts_amount > 2000:
        base = min(base, total_receipts_amount * 0.5)
    
    return round(base, 2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>")
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