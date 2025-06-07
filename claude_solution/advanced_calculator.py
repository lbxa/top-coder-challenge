#!/usr/bin/env python3
"""
Advanced reimbursement calculator using ensemble approach
Combines multiple models for better accuracy
"""

import json
import random
import statistics
from typing import Dict, List, Tuple


class AdvancedReimbursementCalculator:
    """
    Advanced calculator using ensemble of specialized models.
    Each model handles specific trip patterns discovered in analysis.
    """
    
    def __init__(self):
        # Load optimized parameters
        try:
            with open('optimized_params.json', 'r') as f:
                self.base_params = json.load(f)
        except:
            # Fallback to default parameters
            self.base_params = self._get_default_params()
        
        # Specialized models for different patterns
        self.models = {
            'standard': self._calculate_standard,
            'five_day': self._calculate_five_day,
            'high_mileage': self._calculate_high_mileage,
            'low_activity': self._calculate_low_activity,
            'high_spend': self._calculate_high_spend,
            'short_local': self._calculate_short_local,
            'edge_case': self._calculate_edge_case
        }
    
    def calculate_reimbursement(self, trip_duration_days: int, miles_traveled: float, 
                               total_receipts_amount: float) -> float:
        """
        Calculate reimbursement using ensemble approach.
        """
        # Extract features
        features = self._extract_features(trip_duration_days, miles_traveled, total_receipts_amount)
        
        # Determine which models to use and their weights
        model_weights = self._get_model_weights(features)
        
        # Calculate weighted average of model predictions
        total_reimbursement = 0.0
        total_weight = 0.0
        
        for model_name, weight in model_weights.items():
            if weight > 0:
                model_func = self.models[model_name]
                prediction = model_func(features)
                total_reimbursement += prediction * weight
                total_weight += weight
        
        if total_weight > 0:
            final_reimbursement = total_reimbursement / total_weight
        else:
            # Fallback to standard model
            final_reimbursement = self._calculate_standard(features)
        
        # Apply final adjustments
        final_reimbursement = self._apply_final_adjustments(final_reimbursement, features)
        
        return round(final_reimbursement, 2)
    
    def _extract_features(self, days: int, miles: float, receipts: float) -> Dict:
        """Extract all relevant features for modeling."""
        features = {
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'miles_per_day': miles / days if days > 0 else 0,
            'receipts_per_day': receipts / days if days > 0 else 0,
            'is_5_day': days == 5,
            'is_weekend_trip': days in [2, 3],
            'is_week_long': days >= 7,
            'is_high_mileage': miles > 500,
            'is_high_spend': receipts > 800,
            'is_low_spend': receipts < 50,
            'efficiency_ratio': miles / (days + 1) if days >= 0 else 0,
            'spend_efficiency': receipts / (miles + 1) if miles >= 0 else 0,
            'total_activity': miles + receipts,
            'has_magic_cents': self._has_magic_cents(receipts),
            'mileage_tier': self._get_mileage_tier(miles),
            'receipt_tier': self._get_receipt_tier(receipts),
            'trip_complexity': days * (1 + miles/1000) * (1 + receipts/1000)
        }
        return features
    
    def _get_model_weights(self, features: Dict) -> Dict[str, float]:
        """Determine which models to use based on features."""
        weights = {
            'standard': 0.3,  # Base weight for standard model
            'five_day': 0.0,
            'high_mileage': 0.0,
            'low_activity': 0.0,
            'high_spend': 0.0,
            'short_local': 0.0,
            'edge_case': 0.0
        }
        
        # Adjust weights based on trip characteristics
        if features['is_5_day']:
            weights['five_day'] = 0.7
            weights['standard'] = 0.2
        
        if features['miles_per_day'] > 300:
            weights['high_mileage'] = 0.5
            weights['standard'] = 0.1
        
        if features['is_week_long'] and features['miles_per_day'] < 100:
            weights['low_activity'] = 0.6
            weights['standard'] = 0.1
        
        if features['receipts_per_day'] > 150:
            weights['high_spend'] = 0.5
            weights['standard'] = 0.1
        
        if features['days'] <= 2 and features['miles'] < 100:
            weights['short_local'] = 0.6
            weights['standard'] = 0.1
        
        # Edge cases
        if features['total_activity'] < 10 or features['trip_complexity'] > 100:
            weights['edge_case'] = 0.3
        
        return weights
    
    def _calculate_standard(self, features: Dict) -> float:
        """Standard calculation model."""
        # Base per diem
        per_diem = self.base_params.get('base_per_diem', 100) * features['days']
        
        # Mileage with tiers
        mileage = self._calculate_tiered_mileage(features['miles'])
        
        # Receipt coverage
        receipt_reimb = self._calculate_receipt_coverage(features['receipts'])
        
        # Basic total
        total = per_diem + mileage + receipt_reimb
        
        # Standard adjustments
        if 180 <= features['miles_per_day'] <= 220:
            total *= 1.08  # Efficiency bonus
        
        return total
    
    def _calculate_five_day(self, features: Dict) -> float:
        """Specialized model for 5-day trips."""
        # Enhanced per diem for 5-day trips
        per_diem = self.base_params.get('base_per_diem', 100) * features['days'] * 1.15
        
        # Mileage calculation
        mileage = self._calculate_tiered_mileage(features['miles'])
        
        # Special efficiency bonus for 5-day trips
        if 150 <= features['miles_per_day'] <= 250:
            efficiency_bonus = (per_diem + mileage) * 0.12
        else:
            efficiency_bonus = 0
        
        # Receipt handling
        receipt_reimb = self._calculate_receipt_coverage(features['receipts'])
        
        # 5-day trip multiplier based on spending
        if features['receipts_per_day'] < 100:
            multiplier = 1.1
        elif features['receipts_per_day'] < 150:
            multiplier = 1.05
        else:
            multiplier = 0.95
        
        total = (per_diem + mileage + efficiency_bonus + receipt_reimb) * multiplier
        
        return total
    
    def _calculate_high_mileage(self, features: Dict) -> float:
        """Model for high-mileage trips."""
        # Standard per diem
        per_diem = self.base_params.get('base_per_diem', 100) * features['days']
        
        # Enhanced mileage calculation for long distances
        if features['miles'] < 500:
            mileage = features['miles'] * 0.55
        elif features['miles'] < 1000:
            mileage = 500 * 0.55 + (features['miles'] - 500) * 0.48
        else:
            mileage = 500 * 0.55 + 500 * 0.48 + (features['miles'] - 1000) * 0.42
        
        # Receipt coverage (often lower for high-mileage trips)
        receipt_reimb = features['receipts'] * 0.85
        
        # High-mileage adjustment
        if features['days'] <= 3:
            total = (per_diem + mileage + receipt_reimb) * 1.05
        else:
            total = per_diem + mileage + receipt_reimb
        
        return total
    
    def _calculate_low_activity(self, features: Dict) -> float:
        """Model for extended low-activity trips."""
        # Reduced per diem for long low-activity trips
        per_diem = self.base_params.get('base_per_diem', 100) * features['days'] * 0.95
        
        # Simple mileage calculation
        mileage = features['miles'] * 0.52
        
        # Receipt coverage
        if features['receipts'] < 500:
            receipt_reimb = features['receipts'] * 0.88
        else:
            receipt_reimb = 500 * 0.88 + (features['receipts'] - 500) * 0.7
        
        # Low activity penalty
        total = (per_diem + mileage + receipt_reimb) * 0.92
        
        return total
    
    def _calculate_high_spend(self, features: Dict) -> float:
        """Model for high-spending trips."""
        # Standard per diem
        per_diem = self.base_params.get('base_per_diem', 100) * features['days']
        
        # Standard mileage
        mileage = self._calculate_tiered_mileage(features['miles'])
        
        # Penalized receipt coverage for high spending
        if features['receipts'] < 600:
            receipt_reimb = features['receipts'] * 0.85
        elif features['receipts'] < 1200:
            receipt_reimb = 600 * 0.85 + (features['receipts'] - 600) * 0.65
        else:
            receipt_reimb = 600 * 0.85 + 600 * 0.65 + (features['receipts'] - 1200) * 0.45
        
        # High spend penalty
        total = (per_diem + mileage + receipt_reimb) * 0.88
        
        return total
    
    def _calculate_short_local(self, features: Dict) -> float:
        """Model for short local trips."""
        # Slightly reduced per diem
        per_diem = self.base_params.get('base_per_diem', 100) * features['days'] * 0.98
        
        # Simple mileage for short distances
        mileage = features['miles'] * 0.54
        
        # Receipt handling for small amounts
        if features['receipts'] < 20:
            receipt_reimb = features['receipts'] * 0.7
        elif features['receipts'] < 50:
            receipt_reimb = features['receipts'] * 0.85
        else:
            receipt_reimb = features['receipts'] * 0.9
        
        # Local trip adjustment
        total = (per_diem + mileage + receipt_reimb) * 0.96
        
        return total
    
    def _calculate_edge_case(self, features: Dict) -> float:
        """Handle edge cases with special logic."""
        # Very simple calculation for edge cases
        base = 50 * features['days'] + 0.4 * features['miles'] + 0.6 * features['receipts']
        
        # Minimal adjustments
        if features['has_magic_cents']:
            base += 3
        
        return base
    
    def _calculate_tiered_mileage(self, miles: float) -> float:
        """Calculate mileage with optimized tiers."""
        tiers = [
            (self.base_params.get('mileage_tier_1', 100), self.base_params.get('mileage_rate_0', 0.58)),
            (self.base_params.get('mileage_tier_2', 300), self.base_params.get('mileage_rate_1', 0.52)),
            (self.base_params.get('mileage_tier_3', 600), self.base_params.get('mileage_rate_2', 0.47)),
            (self.base_params.get('mileage_tier_4', 1000), self.base_params.get('mileage_rate_3', 0.42)),
            (float('inf'), self.base_params.get('mileage_rate_4', 0.38))
        ]
        
        total = 0.0
        remaining = miles
        prev_tier = 0
        
        for tier_limit, rate in tiers:
            if remaining <= 0:
                break
            tier_miles = min(remaining, tier_limit - prev_tier)
            total += tier_miles * rate
            remaining -= tier_miles
            prev_tier = tier_limit
        
        return total
    
    def _calculate_receipt_coverage(self, receipts: float) -> float:
        """Calculate receipt reimbursement with coverage rules."""
        if receipts == 0:
            return 0.0
        
        small_thresh = self.base_params.get('small_receipt_thresh', 50)
        medium_low = self.base_params.get('medium_receipt_low', 50)
        medium_high = self.base_params.get('medium_receipt_high', 600)
        
        if receipts < small_thresh:
            return receipts * self.base_params.get('small_receipt_penalty', 0.85)
        elif medium_low <= receipts <= medium_high:
            return receipts * self.base_params.get('medium_receipt_coverage', 0.92)
        else:
            base = medium_high * self.base_params.get('high_receipt_coverage', 0.88)
            excess = receipts - medium_high
            excess_rate = 0.6 * (1 - excess / 3000)
            excess_rate = max(0.2, excess_rate)
            return base + (excess * excess_rate)
    
    def _apply_final_adjustments(self, amount: float, features: Dict) -> float:
        """Apply final adjustments and noise."""
        # Deterministic noise based on inputs
        noise_seed = int((features['days'] * 1000 + features['miles'] * 10 + 
                         features['receipts'] * 100) % 1000)
        random.seed(noise_seed)
        noise = random.uniform(-0.01, 0.01)
        amount *= (1 + noise)
        
        # Magic cents bonus
        if features['has_magic_cents']:
            amount += random.uniform(2, 5)
        
        return amount
    
    def _has_magic_cents(self, amount: float) -> bool:
        """Check for .49 or .99 cents."""
        cents = int(round(amount * 100)) % 100
        return cents in [49, 99]
    
    def _get_mileage_tier(self, miles: float) -> int:
        """Categorize mileage into tiers."""
        if miles < 100:
            return 0
        elif miles < 300:
            return 1
        elif miles < 600:
            return 2
        elif miles < 1000:
            return 3
        else:
            return 4
    
    def _get_receipt_tier(self, receipts: float) -> int:
        """Categorize receipts into tiers."""
        if receipts < 50:
            return 0
        elif receipts < 200:
            return 1
        elif receipts < 600:
            return 2
        elif receipts < 1200:
            return 3
        else:
            return 4
    
    def _get_default_params(self) -> Dict:
        """Get default parameters if optimized ones not available."""
        return {
            'base_per_diem': 100.0,
            'five_day_bonus_rate': 0.15,
            'mileage_rate_0': 0.58,
            'mileage_rate_1': 0.52,
            'mileage_rate_2': 0.47,
            'mileage_rate_3': 0.42,
            'mileage_rate_4': 0.38,
            'mileage_tier_1': 100,
            'mileage_tier_2': 300,
            'mileage_tier_3': 600,
            'mileage_tier_4': 1000,
            'efficiency_bonus': 0.08,
            'efficiency_low': 180,
            'efficiency_high': 220,
            'small_receipt_thresh': 50,
            'small_receipt_penalty': 0.85,
            'medium_receipt_low': 50,
            'medium_receipt_high': 600,
            'medium_receipt_coverage': 0.92,
            'high_receipt_coverage': 0.88
        }


def calculate_reimbursement(trip_duration_days: int, miles_traveled: float, 
                           total_receipts_amount: float) -> float:
    """
    Main entry point for reimbursement calculation.
    """
    calculator = AdvancedReimbursementCalculator()
    return calculator.calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)


if __name__ == "__main__":
    # Test with examples
    test_cases = [
        (3, 93, 1.42),
        (5, 900, 450),
        (1, 55, 3.60),
        (8, 400, 1200),
        (5, 200, 100),  # 5-day optimal
    ]
    
    print("Advanced Calculator Test Results:")
    print("-" * 50)
    for days, miles, receipts in test_cases:
        result = calculate_reimbursement(days, miles, receipts)
        print(f"Days: {days}, Miles: {miles}, Receipts: ${receipts:.2f}")
        print(f"  → Reimbursement: ${result:.2f}")
        print()