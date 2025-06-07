#!/usr/bin/env python3
"""
ACME Corp Reimbursement Calculator - Final Optimized Version
Generated after comprehensive analysis and optimization
"""

import random


def calculate_reimbursement(trip_duration_days: int, miles_traveled: float, 
                           total_receipts_amount: float) -> float:
    """Calculate reimbursement using final optimized model."""
    
    # Final optimized parameters
    BASE_PER_DIEM = 100.00
    FIVE_DAY_MULT = 1.150
    
    MILEAGE_TIERS = [100, 300, 600, 1000]
    MILEAGE_RATES = [0.58, 0.52, 0.47, 0.42, 0.38]
    
    EFFICIENCY_RANGE = (180, 220)
    EFFICIENCY_BONUS = 0.080
    
    RECEIPT_TIERS = [50, 200, 600, 1200]
    RECEIPT_RATES = [0.7, 0.85, 0.92, 0.88, 0.6]
    
    CLUSTER_MULTS = {
        'road_warrior': 1.050,
        'optimal': 1.150,
        'extended_low': 0.920,
        'standard': 1.000,
        'local': 0.960,
        'high_spend': 0.850
    }
    
    BIAS_CORRECTIONS = {
        'duration': {'short': -inf, 'medium': -inf, 'long': -inf},
        'efficiency': {'low': -inf, 'medium': -inf, 'high': -inf},
        'spending': {'low': -inf, 'medium': -inf, 'high': -inf}
    }
    
    # Classify trip
    if trip_duration_days == 0:
        cluster = 'standard'
    else:
        mpd = miles_traveled / trip_duration_days
        rpd = total_receipts_amount / trip_duration_days
        
        if mpd > 350 and trip_duration_days <= 3:
            cluster = 'road_warrior'
        elif trip_duration_days == 5 and 150 <= mpd <= 250 and rpd < 120:
            cluster = 'optimal'
        elif trip_duration_days >= 7 and mpd < 150:
            cluster = 'extended_low'
        elif rpd > 130:
            cluster = 'high_spend'
        elif miles_traveled < 80 and trip_duration_days <= 2:
            cluster = 'local'
        else:
            cluster = 'standard'
    
    # Calculate components
    per_diem = BASE_PER_DIEM * trip_duration_days
    if trip_duration_days == 5:
        per_diem *= FIVE_DAY_MULT
    
    # Mileage
    mileage = 0.0
    remaining = miles_traveled
    prev_tier = 0
    
    for i, tier in enumerate(MILEAGE_TIERS):
        if remaining <= 0:
            break
        tier_miles = min(remaining, tier - prev_tier)
        mileage += tier_miles * MILEAGE_RATES[i]
        remaining -= tier_miles
        prev_tier = tier
    
    if remaining > 0:
        mileage += remaining * MILEAGE_RATES[-1]
    
    # Efficiency bonus
    efficiency_bonus = 0.0
    if trip_duration_days > 0:
        mpd = miles_traveled / trip_duration_days
        if EFFICIENCY_RANGE[0] <= mpd <= EFFICIENCY_RANGE[1]:
            efficiency_bonus = (per_diem + mileage) * EFFICIENCY_BONUS
    
    # Receipt reimbursement
    if total_receipts_amount == 0:
        receipt_reimb = 0.0
    else:
        for i, tier in enumerate(RECEIPT_TIERS):
            if total_receipts_amount <= tier:
                receipt_reimb = total_receipts_amount * RECEIPT_RATES[i]
                break
        else:
            base = RECEIPT_TIERS[-1] * RECEIPT_RATES[-2]
            excess = total_receipts_amount - RECEIPT_TIERS[-1]
            excess_rate = RECEIPT_RATES[-1] * (1 - excess / 5000)
            excess_rate = max(0.2, excess_rate)
            receipt_reimb = base + excess * excess_rate
    
    # Total with adjustments
    total = per_diem + mileage + efficiency_bonus + receipt_reimb
    total *= CLUSTER_MULTS[cluster]
    
    # Apply bias corrections
    if trip_duration_days <= 2:
        total *= BIAS_CORRECTIONS['duration']['short']
    elif trip_duration_days <= 5:
        total *= BIAS_CORRECTIONS['duration']['medium']
    else:
        total *= BIAS_CORRECTIONS['duration']['long']
    
    if trip_duration_days > 0:
        mpd = miles_traveled / trip_duration_days
        if mpd < 100:
            total *= BIAS_CORRECTIONS['efficiency']['low']
        elif mpd < 200:
            total *= BIAS_CORRECTIONS['efficiency']['medium']
        else:
            total *= BIAS_CORRECTIONS['efficiency']['high']
    
    if total_receipts_amount < 100:
        total *= BIAS_CORRECTIONS['spending']['low']
    elif total_receipts_amount < 500:
        total *= BIAS_CORRECTIONS['spending']['medium']
    else:
        total *= BIAS_CORRECTIONS['spending']['high']
    
    # Add noise
    noise_seed = int((trip_duration_days * 1000 + miles_traveled * 10 + total_receipts_amount * 100) % 1000)
    random.seed(noise_seed)
    noise = random.uniform(-0.01, 0.01)
    total *= (1 + noise)
    
    # Magic cents
    cents = int(round(total_receipts_amount * 100)) % 100
    if cents in [49, 99]:
        total += random.uniform(2, 5)
    
    return round(total, 2)
