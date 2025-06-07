#!/usr/bin/env python3
"""
Final optimization using gradient-free search and pattern analysis
"""

import json
import random
import statistics
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class PatternAnalyzer:
    """Analyze error patterns to improve model."""
    
    def __init__(self, cases: List[Dict], predictions: List[float]):
        self.cases = cases
        self.predictions = predictions
        self.errors = []
        
        for i, case in enumerate(cases):
            expected = case['expected_output']
            predicted = predictions[i]
            error = predicted - expected
            rel_error = error / expected if expected > 0 else 0
            
            self.errors.append({
                'input': case['input'],
                'expected': expected,
                'predicted': predicted,
                'error': error,
                'abs_error': abs(error),
                'rel_error': rel_error
            })
    
    def find_systematic_biases(self) -> Dict[str, Any]:
        """Find systematic biases in predictions."""
        biases = {
            'by_duration': defaultdict(list),
            'by_efficiency': defaultdict(list),
            'by_spending': defaultdict(list),
            'by_total_activity': defaultdict(list),
            'by_cluster': defaultdict(list)
        }
        
        for err in self.errors:
            inp = err['input']
            days = inp['trip_duration_days']
            miles = inp['miles_traveled']
            receipts = inp['total_receipts_amount']
            
            # Categorize by duration
            if days <= 2:
                dur_cat = 'short'
            elif days <= 5:
                dur_cat = 'medium'
            else:
                dur_cat = 'long'
            biases['by_duration'][dur_cat].append(err['error'])
            
            # Categorize by efficiency
            if days > 0:
                mpd = miles / days
                if mpd < 100:
                    eff_cat = 'low'
                elif mpd < 200:
                    eff_cat = 'medium'
                else:
                    eff_cat = 'high'
                biases['by_efficiency'][eff_cat].append(err['error'])
            
            # Categorize by spending
            if receipts < 100:
                spend_cat = 'low'
            elif receipts < 500:
                spend_cat = 'medium'
            else:
                spend_cat = 'high'
            biases['by_spending'][spend_cat].append(err['error'])
            
            # Total activity
            total = miles + receipts
            if total < 200:
                act_cat = 'low'
            elif total < 800:
                act_cat = 'medium'
            else:
                act_cat = 'high'
            biases['by_total_activity'][act_cat].append(err['error'])
        
        # Calculate mean biases
        bias_summary = {}
        for category, data in biases.items():
            bias_summary[category] = {}
            for subcat, errors in data.items():
                if errors:
                    bias_summary[category][subcat] = {
                        'mean_error': statistics.mean(errors),
                        'count': len(errors)
                    }
        
        return bias_summary
    
    def get_worst_cases(self, n: int = 20) -> List[Dict]:
        """Get the worst prediction cases."""
        sorted_errors = sorted(self.errors, key=lambda x: x['abs_error'], reverse=True)
        return sorted_errors[:n]


class FinalOptimizer:
    """Final optimization combining all insights."""
    
    def __init__(self):
        self.best_params = None
        self.best_error = float('inf')
        
    def optimize(self, train_cases: List[Dict], val_cases: List[Dict], iterations: int = 100):
        """Run final optimization."""
        print("Starting final optimization...")
        
        # Initialize with base parameters
        params = self._get_initial_params()
        
        for i in range(iterations):
            # Make predictions
            predictions = [self._predict(case['input'], params) for case in train_cases]
            
            # Analyze patterns
            analyzer = PatternAnalyzer(train_cases, predictions)
            biases = analyzer.find_systematic_biases()
            
            # Calculate current error
            errors = [abs(pred - case['expected_output']) for pred, case in zip(predictions, train_cases)]
            mean_error = statistics.mean(errors)
            
            if mean_error < self.best_error:
                self.best_error = mean_error
                self.best_params = params.copy()
                print(f"Iteration {i}: New best error ${mean_error:.2f}")
                
                # Validate
                val_predictions = [self._predict(case['input'], params) for case in val_cases]
                val_errors = [abs(pred - case['expected_output']) for pred, case in zip(val_predictions, val_cases)]
                val_error = statistics.mean(val_errors)
                print(f"  Validation error: ${val_error:.2f}")
            
            # Update parameters based on biases
            params = self._update_params_from_biases(params, biases)
            
            # Random perturbation
            if random.random() < 0.3:
                params = self._perturb_params(params)
        
        return self.best_params
    
    def _get_initial_params(self) -> Dict:
        """Get initial parameters combining all insights."""
        return {
            # Base rates
            'base_per_diem': 100.0,
            'five_day_multiplier': 1.15,
            
            # Mileage tiers and rates
            'mileage_tiers': [100, 300, 600, 1000],
            'mileage_rates': [0.58, 0.52, 0.47, 0.42, 0.38],
            
            # Efficiency parameters
            'efficiency_low': 180,
            'efficiency_high': 220,
            'efficiency_bonus': 0.08,
            
            # Receipt parameters
            'receipt_tiers': [50, 200, 600, 1200],
            'receipt_rates': [0.7, 0.85, 0.92, 0.88, 0.6],
            
            # Bias corrections
            'duration_bias': {'short': 1.0, 'medium': 1.0, 'long': 1.0},
            'efficiency_bias': {'low': 1.0, 'medium': 1.0, 'high': 1.0},
            'spending_bias': {'low': 1.0, 'medium': 1.0, 'high': 1.0},
            
            # Cluster multipliers
            'cluster_mults': {
                'road_warrior': 1.05,
                'optimal': 1.15,
                'extended_low': 0.92,
                'standard': 1.0,
                'local': 0.96,
                'high_spend': 0.85
            }
        }
    
    def _predict(self, input_data: Dict, params: Dict) -> float:
        """Make prediction with given parameters."""
        days = input_data['trip_duration_days']
        miles = input_data['miles_traveled']
        receipts = input_data['total_receipts_amount']
        
        # Classify trip
        cluster = self._classify_trip(days, miles, receipts)
        
        # Base per diem
        per_diem = params['base_per_diem'] * days
        if days == 5:
            per_diem *= params['five_day_multiplier']
        
        # Mileage calculation
        mileage = self._calculate_mileage(miles, params)
        
        # Efficiency bonus
        efficiency_bonus = 0
        if days > 0:
            mpd = miles / days
            if params['efficiency_low'] <= mpd <= params['efficiency_high']:
                efficiency_bonus = (per_diem + mileage) * params['efficiency_bonus']
        
        # Receipt calculation
        receipt_reimb = self._calculate_receipts(receipts, params)
        
        # Total
        total = per_diem + mileage + efficiency_bonus + receipt_reimb
        
        # Apply cluster multiplier
        total *= params['cluster_mults'][cluster]
        
        # Apply bias corrections
        total = self._apply_bias_corrections(total, days, miles, receipts, params)
        
        # Add noise
        noise_seed = int((days * 1000 + miles * 10 + receipts * 100) % 1000)
        random.seed(noise_seed)
        noise = random.uniform(-0.01, 0.01)
        total *= (1 + noise)
        
        # Magic cents
        cents = int(round(receipts * 100)) % 100
        if cents in [49, 99]:
            total += random.uniform(2, 5)
        
        return round(total, 2)
    
    def _classify_trip(self, days: int, miles: float, receipts: float) -> str:
        """Classify trip into cluster."""
        if days == 0:
            return 'standard'
        
        mpd = miles / days
        rpd = receipts / days
        
        if mpd > 350 and days <= 3:
            return 'road_warrior'
        elif days == 5 and 150 <= mpd <= 250 and rpd < 120:
            return 'optimal'
        elif days >= 7 and mpd < 150:
            return 'extended_low'
        elif rpd > 130:
            return 'high_spend'
        elif miles < 80 and days <= 2:
            return 'local'
        else:
            return 'standard'
    
    def _calculate_mileage(self, miles: float, params: Dict) -> float:
        """Calculate mileage with tiers."""
        total = 0
        remaining = miles
        prev_tier = 0
        
        for i, tier in enumerate(params['mileage_tiers']):
            if remaining <= 0:
                break
            tier_miles = min(remaining, tier - prev_tier)
            total += tier_miles * params['mileage_rates'][i]
            remaining -= tier_miles
            prev_tier = tier
        
        if remaining > 0:
            total += remaining * params['mileage_rates'][-1]
        
        return total
    
    def _calculate_receipts(self, receipts: float, params: Dict) -> float:
        """Calculate receipt reimbursement."""
        if receipts == 0:
            return 0
        
        for i, tier in enumerate(params['receipt_tiers']):
            if receipts <= tier:
                return receipts * params['receipt_rates'][i]
        
        # High receipts
        base = params['receipt_tiers'][-1] * params['receipt_rates'][-2]
        excess = receipts - params['receipt_tiers'][-1]
        excess_rate = params['receipt_rates'][-1] * (1 - excess / 5000)
        excess_rate = max(0.2, excess_rate)
        
        return base + excess * excess_rate
    
    def _apply_bias_corrections(self, total: float, days: int, miles: float, 
                               receipts: float, params: Dict) -> float:
        """Apply bias corrections based on categories."""
        # Duration bias
        if days <= 2:
            total *= params['duration_bias']['short']
        elif days <= 5:
            total *= params['duration_bias']['medium']
        else:
            total *= params['duration_bias']['long']
        
        # Efficiency bias
        if days > 0:
            mpd = miles / days
            if mpd < 100:
                total *= params['efficiency_bias']['low']
            elif mpd < 200:
                total *= params['efficiency_bias']['medium']
            else:
                total *= params['efficiency_bias']['high']
        
        # Spending bias
        if receipts < 100:
            total *= params['spending_bias']['low']
        elif receipts < 500:
            total *= params['spending_bias']['medium']
        else:
            total *= params['spending_bias']['high']
        
        return total
    
    def _update_params_from_biases(self, params: Dict, biases: Dict) -> Dict:
        """Update parameters based on systematic biases."""
        new_params = params.copy()
        
        # Adjust bias corrections
        for category in ['duration', 'efficiency', 'spending']:
            if f'by_{category}' in biases:
                for subcat, data in biases[f'by_{category}'].items():
                    if data and 'mean_error' in data:
                        # Adjust to reduce bias
                        current = new_params[f'{category}_bias'].get(subcat, 1.0)
                        adjustment = 1.0 - (data['mean_error'] / 1000)  # Small adjustment
                        new_params[f'{category}_bias'][subcat] = current * adjustment
        
        return new_params
    
    def _perturb_params(self, params: Dict) -> Dict:
        """Randomly perturb parameters."""
        new_params = params.copy()
        
        # Perturb numeric parameters
        if random.random() < 0.5:
            new_params['base_per_diem'] += random.uniform(-2, 2)
            new_params['base_per_diem'] = max(80, min(120, new_params['base_per_diem']))
        
        if random.random() < 0.5:
            idx = random.randint(0, len(new_params['mileage_rates']) - 1)
            new_params['mileage_rates'][idx] += random.uniform(-0.02, 0.02)
            new_params['mileage_rates'][idx] = max(0.2, min(0.7, new_params['mileage_rates'][idx]))
        
        return new_params


def generate_final_calculator(params: Dict):
    """Generate the final optimized calculator."""
    code = f'''#!/usr/bin/env python3
"""
ACME Corp Reimbursement Calculator - Final Optimized Version
Generated after comprehensive analysis and optimization
"""

import random


def calculate_reimbursement(trip_duration_days: int, miles_traveled: float, 
                           total_receipts_amount: float) -> float:
    """Calculate reimbursement using final optimized model."""
    
    # Final optimized parameters
    BASE_PER_DIEM = {params['base_per_diem']:.2f}
    FIVE_DAY_MULT = {params['five_day_multiplier']:.3f}
    
    MILEAGE_TIERS = {params['mileage_tiers']}
    MILEAGE_RATES = {params['mileage_rates']}
    
    EFFICIENCY_RANGE = ({params['efficiency_low']}, {params['efficiency_high']})
    EFFICIENCY_BONUS = {params['efficiency_bonus']:.3f}
    
    RECEIPT_TIERS = {params['receipt_tiers']}
    RECEIPT_RATES = {params['receipt_rates']}
    
    CLUSTER_MULTS = {{
        'road_warrior': {params['cluster_mults']['road_warrior']:.3f},
        'optimal': {params['cluster_mults']['optimal']:.3f},
        'extended_low': {params['cluster_mults']['extended_low']:.3f},
        'standard': {params['cluster_mults']['standard']:.3f},
        'local': {params['cluster_mults']['local']:.3f},
        'high_spend': {params['cluster_mults']['high_spend']:.3f}
    }}
    
    BIAS_CORRECTIONS = {{
        'duration': {params['duration_bias']},
        'efficiency': {params['efficiency_bias']},
        'spending': {params['spending_bias']}
    }}
    
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
'''
    
    with open('reimbursement_calculator_final.py', 'w') as f:
        f.write(code)


def main():
    """Run final optimization."""
    # Load cases
    with open('../public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Split data
    random.shuffle(cases)
    train_size = int(0.8 * len(cases))
    train_cases = cases[:train_size]
    val_cases = cases[train_size:]
    
    # Run optimization
    optimizer = FinalOptimizer()
    best_params = optimizer.optimize(train_cases, val_cases, iterations=50)
    
    # Generate final calculator
    generate_final_calculator(best_params)
    
    print("\nFinal optimized calculator saved to reimbursement_calculator_final.py")
    print(f"Best training error: ${optimizer.best_error:.2f}")


if __name__ == "__main__":
    random.seed(42)
    main()