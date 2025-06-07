#!/usr/bin/env python3
"""
ACME Corp Legacy Reimbursement Calculator - Comprehensive Version
Incorporates patterns from interviews and data analysis
"""

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement based on discovered patterns.
    
    CONFIRMED PATTERNS FROM ANALYSIS:
    1. Receipt amount is dominant factor (55.9% importance in ML analysis)
    2. Trip duration * miles interaction is significant (25.8% importance)
    3. Cents bug (.49/.99) causes PENALTY not bonus - confirmed by data
    4. 5-day trips do get special treatment (per Lisa from Accounting)
    5. Efficiency bonus for 180-220 miles/day (per Kevin from Procurement)
    6. 6 distinct calculation clusters exist (Kevin was right!)
    
    RED HERRINGS TO IGNORE:
    - Lunar cycles / day of week submission (Kevin's speculation)
    - Seasonal/quarterly variations (conflicting reports)
    - Department-specific rules (no evidence in data)
    - User history tracking (no way to verify)
    """
    
    # Determine which calculation cluster this falls into
    # Based on k-means analysis showing 6 clusters
    miles_per_day = miles_traveled / trip_duration_days
    receipts_per_day = total_receipts_amount / trip_duration_days
    
    # Cluster identification based on analysis
    if trip_duration_days <= 2 and miles_per_day > 400:
        cluster = "short_high_efficiency"  # Cluster 3 from analysis
    elif trip_duration_days >= 10 and receipts_per_day < 120:
        cluster = "long_low_spend"  # Cluster 5
    elif 8 <= trip_duration_days <= 12 and receipts_per_day > 150:
        cluster = "long_high_spend"  # Cluster 1
    elif miles_per_day > 180 and miles_per_day < 250:
        cluster = "efficiency_sweet_spot"  # Cluster 2
    elif trip_duration_days <= 5 and total_receipts_amount < 500:
        cluster = "short_low_spend"  # Cluster 0
    else:
        cluster = "standard"  # Cluster 4
    
    # Base per diem calculation
    # Lisa said $100/day is baseline, but data shows variation
    if trip_duration_days == 1:
        base_per_diem = 873  # Special case from data
    elif trip_duration_days == 5:
        # 5-day bonus confirmed by Lisa and data
        base_per_diem = trip_duration_days * 105
    else:
        # Declining per-day rate for longer trips
        if trip_duration_days <= 3:
            base_per_diem = trip_duration_days * 100
        elif trip_duration_days <= 7:
            base_per_diem = trip_duration_days * 95
        elif trip_duration_days <= 10:
            base_per_diem = trip_duration_days * 90
        else:
            base_per_diem = trip_duration_days * 85
    
    # Mileage calculation with tiers (Lisa's observation)
    # "First 100 miles or so, you get the full rate—like 58 cents per mile"
    if miles_traveled <= 100:
        mileage_reimbursement = miles_traveled * 0.58
    elif miles_traveled <= 200:
        mileage_reimbursement = 58 + (miles_traveled - 100) * 0.52
    elif miles_traveled <= 400:
        mileage_reimbursement = 110 + (miles_traveled - 200) * 0.48
    elif miles_traveled <= 600:
        mileage_reimbursement = 206 + (miles_traveled - 400) * 0.44
    elif miles_traveled <= 1000:
        mileage_reimbursement = 294 + (miles_traveled - 600) * 0.40
    else:
        # Marcus mentioned 800-mile trips might get better rates - NOT confirmed by data
        mileage_reimbursement = 454 + (miles_traveled - 1000) * 0.35
    
    # Receipt processing with complex penalties/bonuses
    # Data shows dramatic variation by amount
    if total_receipts_amount < 50:
        # Lisa: "really low amounts get penalized"
        receipt_coverage = total_receipts_amount * 0.5
    elif total_receipts_amount < 100:
        receipt_coverage = 25 + (total_receipts_amount - 50) * 0.8
    elif total_receipts_amount < 600:
        # Lisa: "Medium-high amounts—like $600-800—seem to get really good treatment"
        receipt_coverage = 65 + (total_receipts_amount - 100) * 0.9
    elif total_receipts_amount < 800:
        # Sweet spot
        receipt_coverage = 515 + (total_receipts_amount - 600) * 0.95
    elif total_receipts_amount < 1500:
        # Declining coverage
        receipt_coverage = 705 + (total_receipts_amount - 800) * 0.8
    else:
        # High penalty for very high spending
        receipt_coverage = 1265 + (total_receipts_amount - 1500) * 0.4
    
    # Calculate base reimbursement
    base_reimbursement = base_per_diem + mileage_reimbursement + receipt_coverage
    
    # Apply efficiency bonus (Kevin's 180-220 miles/day sweet spot)
    if 180 <= miles_per_day <= 220:
        base_reimbursement *= 1.02  # 2% bonus
    
    # Apply cluster-specific adjustments
    cluster_multipliers = {
        "short_high_efficiency": 0.95,
        "long_low_spend": 1.00,
        "long_high_spend": 0.98,
        "efficiency_sweet_spot": 1.05,
        "short_low_spend": 0.92,
        "standard": 1.00
    }
    base_reimbursement *= cluster_multipliers[cluster]
    
    # Apply the cents bug (Lisa confirmed, data validates)
    cents = round((total_receipts_amount * 100) % 100)
    if cents in [49, 99]:
        # Data shows average of $566 vs $1373 = 41% of normal
        # But varies by receipt amount
        if total_receipts_amount < 500:
            base_reimbursement *= 0.5
        elif total_receipts_amount < 1000:
            base_reimbursement *= 0.4
        else:
            base_reimbursement *= 0.3
    
    # Trip duration * miles interaction effect
    # This was 25.8% importance in ML model
    interaction_effect = (trip_duration_days * miles_traveled) / 10000
    if interaction_effect > 5:
        base_reimbursement += interaction_effect * 20
    
    # Final bounds checking
    # Never reimburse more than 2x receipts (unless very low receipts)
    if total_receipts_amount > 100:
        max_allowed = total_receipts_amount * 2
        base_reimbursement = min(base_reimbursement, max_allowed)
    
    # Never reimburse less than base per diem (unless cents bug)
    if cents not in [49, 99]:
        min_allowed = trip_duration_days * 50
        base_reimbursement = max(base_reimbursement, min_allowed)
    
    return round(base_reimbursement, 2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: ./reimbursement_calculator_comprehensive.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
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