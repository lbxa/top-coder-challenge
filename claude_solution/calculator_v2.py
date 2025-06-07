#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement Calculator V2
Based on comprehensive pattern analysis
"""

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement using discovered patterns.
    
    Key insights:
    1. Receipt ratios vary dramatically by range (45x for <$20 to 0.73x for >$2000)
    2. Cents bug is a PENALTY that varies by receipt amount
    3. Per-day rates decline with trip length
    4. Efficiency "bonus" is actually a penalty
    5. Interaction effects exist but are secondary
    """
    
    # Check for cents bug
    cents = round((total_receipts_amount * 100) % 100)
    has_cents_bug = cents in [49, 99]
    
    # Base calculation using receipt ratios from analysis
    if total_receipts_amount < 20:
        # Very low: 45.7x ratio but highly variable
        # Use combination of high multiplier and base per diem
        receipt_component = total_receipts_amount * 30
        base_per_diem = 100
    elif total_receipts_amount < 50:
        # Low: 26.5x ratio
        receipt_component = total_receipts_amount * 20
        base_per_diem = 80
    elif total_receipts_amount < 100:
        # Medium-low: 9.7x ratio
        receipt_component = total_receipts_amount * 8
        base_per_diem = 60
    elif total_receipts_amount < 200:
        # Medium: 5.8x ratio
        receipt_component = total_receipts_amount * 4.5
        base_per_diem = 50
    elif total_receipts_amount < 500:
        # Medium-high: 2.4x ratio
        receipt_component = total_receipts_amount * 2.1
        base_per_diem = 40
    elif total_receipts_amount < 1000:
        # High: 1.6x ratio
        receipt_component = total_receipts_amount * 1.5
        base_per_diem = 30
    elif total_receipts_amount < 1500:
        # Very high: 1.32x ratio
        receipt_component = total_receipts_amount * 1.28
        base_per_diem = 25
    elif total_receipts_amount < 2000:
        # Extreme high: 0.96x ratio
        receipt_component = total_receipts_amount * 0.94
        base_per_diem = 20
    else:
        # Ultra high: 0.73x ratio, but varies by trip duration
        # From analysis: 1-2d ~0.61, 3-4d ~0.655, 5-6d ~0.74, etc.
        if trip_duration_days <= 2:
            ratio = 0.60
        elif trip_duration_days <= 4:
            ratio = 0.65
        elif trip_duration_days <= 6:
            ratio = 0.73
        elif trip_duration_days <= 8:
            ratio = 0.70
        elif trip_duration_days <= 10:
            ratio = 0.75
        elif trip_duration_days <= 12:
            ratio = 0.77
        else:
            ratio = 0.82
        receipt_component = total_receipts_amount * ratio
        base_per_diem = 15
    
    # Calculate per diem component
    # From analysis: 1 day averages $873, declining with length
    if trip_duration_days == 1:
        # Special handling for 1-day trips
        if total_receipts_amount < 500:
            per_diem_total = 300  # Higher base for low receipts
        else:
            per_diem_total = 150  # Lower base for high receipts
    else:
        # Declining per-day rate
        if trip_duration_days <= 3:
            per_day = base_per_diem + 50
        elif trip_duration_days <= 5:
            per_day = base_per_diem + 30
        elif trip_duration_days <= 7:
            per_day = base_per_diem + 20
        elif trip_duration_days <= 10:
            per_day = base_per_diem + 10
        else:
            per_day = base_per_diem + 5
        per_diem_total = trip_duration_days * per_day
    
    # Mileage component (small effect)
    # Simple tiered structure
    if miles_traveled < 100:
        mileage_component = miles_traveled * 0.25
    elif miles_traveled < 500:
        mileage_component = 25 + (miles_traveled - 100) * 0.15
    elif miles_traveled < 1000:
        mileage_component = 85 + (miles_traveled - 500) * 0.10
    else:
        mileage_component = 135 + (miles_traveled - 1000) * 0.05
    
    # Calculate base reimbursement
    base_reimbursement = receipt_component + per_diem_total + mileage_component
    
    # Apply cents bug penalty
    if has_cents_bug:
        if total_receipts_amount < 100:
            penalty = 0.50  # Average of 0.44-0.95
        elif total_receipts_amount < 500:
            penalty = 0.58
        elif total_receipts_amount < 1000:
            penalty = 0.58
        elif total_receipts_amount < 1500:
            penalty = 0.38
        elif total_receipts_amount < 2000:
            penalty = 0.35
        else:
            penalty = 0.20
        base_reimbursement *= penalty
    
    # Apply efficiency penalty (not bonus!)
    miles_per_day = miles_traveled / trip_duration_days
    if 180 <= miles_per_day <= 220:
        base_reimbursement *= 0.90  # 0.903 from analysis
    
    # Interaction effect (trip_duration * miles)
    interaction = trip_duration_days * miles_traveled
    if interaction < 1000:
        # Small positive effect
        base_reimbursement += interaction * 0.01
    elif interaction > 10000:
        # Small negative effect for very high interactions
        base_reimbursement -= (interaction - 10000) * 0.002
    
    # Edge case adjustments
    # Very low miles with decent receipts
    if miles_traveled < 20 and total_receipts_amount > 500:
        base_reimbursement *= 0.85
    
    # Short trips with very high receipts need special handling
    if trip_duration_days <= 2 and total_receipts_amount > 2000:
        # These have specific ratios around 0.5-0.7
        expected = total_receipts_amount * 0.60 + miles_traveled * 0.1 + 100
        base_reimbursement = min(base_reimbursement, expected)
    
    return round(base_reimbursement, 2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: ./calculator_v2.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
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