#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement Calculator V3
Based on detailed ratio analysis
"""

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement with proper ratio-based approach.
    
    Key insights:
    1. Low receipts get massive multipliers (up to 256x)
    2. High receipts get less than 1x (capped around 0.7x)
    3. .49/.99 endings get severe penalty ($566 avg vs $1373)
    4. 1-day trips average $873, not proportional to other trips
    """
    
    # First, check for the cents bug - this is a MAJOR factor
    cents = round((total_receipts_amount * 100) % 100)
    has_cents_bug = cents in [49, 99]
    
    # Base calculation depends heavily on receipt amount
    if total_receipts_amount < 10:
        # Very low receipts: massive multipliers
        base = total_receipts_amount * 40 + 100
    elif total_receipts_amount < 50:
        # Low receipts: still high multipliers
        base = total_receipts_amount * 15 + 200
    elif total_receipts_amount < 100:
        # Medium-low: declining multipliers
        base = total_receipts_amount * 8 + 300
    elif total_receipts_amount < 200:
        # Transition zone
        base = total_receipts_amount * 3.5 + 400
    elif total_receipts_amount < 500:
        # Medium receipts: ~3x multiplier
        base = total_receipts_amount * 2.8 + 100
    elif total_receipts_amount < 1000:
        # Medium-high: ~1.6x multiplier
        base = total_receipts_amount * 1.55 + 50
    elif total_receipts_amount < 1500:
        # High: ~1.3x multiplier
        base = total_receipts_amount * 1.28
    elif total_receipts_amount < 2000:
        # Very high: <1x multiplier
        base = total_receipts_amount * 0.93 + 50
    else:
        # Extremely high: ~0.73x multiplier
        base = total_receipts_amount * 0.71 + 100
    
    # Trip duration adjustments based on per-day rates
    if trip_duration_days == 1:
        # 1-day trips are special: average $873
        duration_factor = 0.9 if base < 900 else 0.85
    elif trip_duration_days == 2:
        # 2-day trips: average $1046 total
        duration_factor = 0.95
    elif trip_duration_days <= 5:
        duration_factor = 1.0
    elif trip_duration_days <= 8:
        duration_factor = 1.02
    elif trip_duration_days <= 12:
        duration_factor = 1.05
    else:
        duration_factor = 1.08
    
    # Mileage component (smaller than expected)
    if miles_traveled < 100:
        mileage_bonus = miles_traveled * 0.15
    elif miles_traveled < 500:
        mileage_bonus = 15 + (miles_traveled - 100) * 0.10
    elif miles_traveled < 1000:
        mileage_bonus = 55 + (miles_traveled - 500) * 0.08
    else:
        mileage_bonus = 95 + (miles_traveled - 1000) * 0.05
    
    # Calculate base reimbursement
    reimbursement = base * duration_factor + mileage_bonus
    
    # Apply the cents bug penalty if applicable
    if has_cents_bug:
        # Average is $566 vs $1373, so about 41% of normal
        reimbursement *= 0.41
    
    # Final adjustments for edge cases
    # Very short trips with very low receipts
    if trip_duration_days <= 2 and total_receipts_amount < 20:
        reimbursement = max(reimbursement, 120)
    
    # Long trips with high receipts tend to be capped
    if trip_duration_days >= 10 and total_receipts_amount > 1500:
        reimbursement = min(reimbursement, total_receipts_amount * 0.95 + 200)
    
    return round(reimbursement, 2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: ./reimbursement_calculator_v3.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
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