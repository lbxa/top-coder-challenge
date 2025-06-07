#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement Calculator V2
Based on deep analysis of patterns in the data
"""

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement based on discovered patterns.
    
    Key findings:
    1. Receipt amount is the dominant factor (55.9% importance)
    2. Trip duration * miles interaction is significant (25.8% importance)
    3. 5-day trips get bonuses, 1-day trips have high per-day rates
    4. Receipts ending in .49/.99 get PENALTIES (not bonuses)
    5. Complex mileage tiers exist
    """
    
    # Start with receipt-based calculation (most important factor)
    # Base coverage appears to be around 80-95% of receipts
    if total_receipts_amount < 50:
        # Very low receipts get penalized
        receipt_component = total_receipts_amount * 0.65
    elif total_receipts_amount < 200:
        receipt_component = total_receipts_amount * 0.75
    elif total_receipts_amount < 500:
        receipt_component = total_receipts_amount * 0.82
    elif total_receipts_amount < 1000:
        receipt_component = total_receipts_amount * 0.88
    elif total_receipts_amount < 1500:
        receipt_component = total_receipts_amount * 0.92
    elif total_receipts_amount < 2000:
        receipt_component = total_receipts_amount * 0.85
    else:
        # Very high receipts face diminishing returns
        receipt_component = 1700 + (total_receipts_amount - 2000) * 0.15
    
    # Per diem component
    # Analysis shows varying per-day rates by trip length
    if trip_duration_days == 1:
        # 1-day trips average $874 total
        per_diem_component = 280
    elif trip_duration_days == 2:
        per_diem_component = trip_duration_days * 85
    elif trip_duration_days == 3:
        per_diem_component = trip_duration_days * 90
    elif trip_duration_days == 4:
        per_diem_component = trip_duration_days * 95
    elif trip_duration_days == 5:
        # 5-day trips get bonus
        per_diem_component = trip_duration_days * 105
    elif trip_duration_days <= 7:
        per_diem_component = trip_duration_days * 100
    elif trip_duration_days <= 10:
        per_diem_component = trip_duration_days * 98
    else:
        per_diem_component = trip_duration_days * 95
    
    # Mileage component with tiers
    if miles_traveled <= 100:
        mileage_component = miles_traveled * 0.58
    elif miles_traveled <= 200:
        mileage_component = 58 + (miles_traveled - 100) * 0.52
    elif miles_traveled <= 400:
        mileage_component = 110 + (miles_traveled - 200) * 0.48
    elif miles_traveled <= 600:
        mileage_component = 206 + (miles_traveled - 400) * 0.45
    elif miles_traveled <= 800:
        mileage_component = 296 + (miles_traveled - 800) * 0.42
    elif miles_traveled <= 1000:
        mileage_component = 380 + (miles_traveled - 800) * 0.40
    else:
        mileage_component = 460 + (miles_traveled - 1000) * 0.35
    
    # Trip duration * miles interaction effect
    interaction_bonus = 0
    miles_per_day = miles_traveled / trip_duration_days
    
    # Efficiency bonus for 180-220 miles/day
    if 180 <= miles_per_day <= 220:
        interaction_bonus = 25
    elif 150 <= miles_per_day <= 250:
        interaction_bonus = 15
    
    # Additional interaction effect
    if trip_duration_days >= 5 and miles_traveled >= 500:
        interaction_bonus += (trip_duration_days * miles_traveled) * 0.00008
    
    # Calculate base reimbursement
    base_reimbursement = receipt_component + per_diem_component + mileage_component + interaction_bonus
    
    # Apply the cents bug (PENALTY for .49/.99 endings)
    cents = round((total_receipts_amount * 100) % 100)
    if cents == 49 or cents == 99:
        # Analysis showed these cases average $574 vs $1372 for others
        # That's about a 58% penalty
        base_reimbursement *= 0.42
    
    # Final adjustments based on trip clusters
    # Short trips with high efficiency
    if trip_duration_days <= 2 and miles_per_day > 400:
        base_reimbursement *= 0.95
    # Long trips with high receipts
    elif trip_duration_days >= 10 and total_receipts_amount > 1500:
        base_reimbursement *= 1.02
    # Medium balanced trips (sweet spot)
    elif 4 <= trip_duration_days <= 6 and 400 <= miles_traveled <= 800:
        base_reimbursement *= 1.05
    
    return round(base_reimbursement, 2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: ./reimbursement_calculator_v2.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
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