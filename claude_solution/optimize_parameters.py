#!/usr/bin/env python3
"""
Optimize reimbursement calculator parameters using gradient-free optimization
"""

import json
import random
import statistics
from typing import Dict, List, Tuple


class ParameterOptimizer:
    """Optimize calculator parameters using evolutionary algorithm."""
    
    def __init__(self):
        # Parameter bounds for optimization
        self.param_bounds = {
            'base_per_diem': (80, 120),
            'five_day_bonus_rate': (0.05, 0.25),
            'mileage_rate_0': (0.45, 0.65),
            'mileage_rate_1': (0.40, 0.60),
            'mileage_rate_2': (0.35, 0.55),
            'mileage_rate_3': (0.30, 0.50),
            'mileage_rate_4': (0.25, 0.45),
            'mileage_tier_1': (80, 150),
            'mileage_tier_2': (250, 400),
            'mileage_tier_3': (500, 800),
            'mileage_tier_4': (900, 1200),
            'efficiency_bonus': (0.02, 0.15),
            'efficiency_low': (150, 200),
            'efficiency_high': (200, 250),
            'small_receipt_thresh': (30, 80),
            'small_receipt_penalty': (0.6, 0.9),
            'medium_receipt_low': (30, 80),
            'medium_receipt_high': (500, 800),
            'medium_receipt_coverage': (0.8, 1.0),
            'high_receipt_coverage': (0.7, 0.95),
            'cluster_mult_0': (0.9, 1.2),
            'cluster_mult_1': (1.0, 1.3),
            'cluster_mult_2': (0.8, 1.1),
            'cluster_mult_3': (0.9, 1.1),
            'cluster_mult_4': (0.85, 1.05),
            'cluster_mult_5': (0.7, 1.0),
        }
    
    def create_random_params(self) -> Dict:
        """Create random parameter set within bounds."""
        params = {}
        for key, (low, high) in self.param_bounds.items():
            params[key] = random.uniform(low, high)
        return params
    
    def mutate_params(self, params: Dict, mutation_rate: float = 0.1) -> Dict:
        """Mutate parameters slightly."""
        new_params = params.copy()
        for key, value in params.items():
            if random.random() < mutation_rate:
                low, high = self.param_bounds[key]
                delta = (high - low) * 0.1 * random.gauss(0, 1)
                new_params[key] = max(low, min(high, value + delta))
        return new_params
    
    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Create child from two parents."""
        child = {}
        for key in parent1:
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child
    
    def evaluate_params(self, params: Dict, cases: List) -> float:
        """Evaluate parameter set on cases and return mean error."""
        errors = []
        
        for case in cases:
            input_data = case['input']
            expected = case['expected_output']
            
            calculated = self.calculate_with_params(
                params,
                input_data['trip_duration_days'],
                input_data['miles_traveled'],
                input_data['total_receipts_amount']
            )
            
            error = abs(calculated - expected)
            errors.append(error)
        
        return statistics.mean(errors)
    
    def calculate_with_params(self, params: Dict, days: int, miles: float, receipts: float) -> float:
        """Calculate reimbursement with given parameters."""
        # Classify trip
        cluster = self._classify_trip(days, miles, receipts)
        
        # Per diem
        per_diem = params['base_per_diem'] * days
        if days == 5:
            per_diem *= (1 + params['five_day_bonus_rate'])
        
        # Mileage calculation with custom tiers
        mileage_tiers = [
            (params['mileage_tier_1'], params['mileage_rate_0']),
            (params['mileage_tier_2'], params['mileage_rate_1']),
            (params['mileage_tier_3'], params['mileage_rate_2']),
            (params['mileage_tier_4'], params['mileage_rate_3']),
            (float('inf'), params['mileage_rate_4'])
        ]
        
        mileage = 0.0
        remaining = miles
        prev_tier = 0
        
        for tier_limit, rate in mileage_tiers:
            if remaining <= 0:
                break
            tier_miles = min(remaining, tier_limit - prev_tier)
            mileage += tier_miles * rate
            remaining -= tier_miles
            prev_tier = tier_limit
        
        # Efficiency bonus
        efficiency_bonus = 0.0
        if days > 0:
            mpd = miles / days
            if params['efficiency_low'] <= mpd <= params['efficiency_high']:
                efficiency_bonus = (per_diem + mileage) * params['efficiency_bonus']
        
        # Receipt reimbursement
        if receipts == 0:
            receipt_reimb = 0.0
        elif receipts < params['small_receipt_thresh']:
            receipt_reimb = receipts * params['small_receipt_penalty']
        elif params['medium_receipt_low'] <= receipts <= params['medium_receipt_high']:
            receipt_reimb = receipts * params['medium_receipt_coverage']
        else:
            base = params['medium_receipt_high'] * params['high_receipt_coverage']
            excess = receipts - params['medium_receipt_high']
            excess_rate = 0.6 * (1 - excess / 3000)
            excess_rate = max(0.2, excess_rate)
            receipt_reimb = base + (excess * excess_rate)
        
        # Total with cluster adjustment
        total = per_diem + mileage + efficiency_bonus + receipt_reimb
        cluster_mult = params[f'cluster_mult_{cluster}']
        total *= cluster_mult
        
        # Add small noise
        noise_seed = int((days * 1000 + miles * 10 + receipts * 100) % 1000)
        random.seed(noise_seed)
        noise = random.uniform(-0.01, 0.01)
        total *= (1 + noise)
        
        # Magic cents
        cents = int(round(receipts * 100)) % 100
        if cents in [49, 99]:
            total += random.uniform(2, 5)
        
        return round(total, 2)
    
    def _classify_trip(self, days: int, miles: float, receipts: float) -> int:
        """Simplified cluster classification."""
        if days == 0:
            return 3
        
        mpd = miles / days
        rpd = receipts / days
        
        if mpd > 350 and days <= 3:
            return 0  # Road warrior
        elif days == 5 and 150 <= mpd <= 250 and rpd < 120:
            return 1  # Optimal (relaxed)
        elif days >= 7 and mpd < 150:
            return 2  # Extended low
        elif rpd > 130:
            return 5  # High spend
        elif miles < 80 and days <= 2:
            return 4  # Local
        else:
            return 3  # Standard
    
    def optimize(self, cases: List, generations: int = 50, population_size: int = 100):
        """Run evolutionary optimization."""
        # Initialize population
        population = [self.create_random_params() for _ in range(population_size)]
        
        # Evaluate initial population
        fitness = [(self.evaluate_params(p, cases), p) for p in population]
        fitness.sort(key=lambda x: x[0])
        
        best_error = fitness[0][0]
        best_params = fitness[0][1]
        
        print(f"Initial best error: ${best_error:.2f}")
        
        for gen in range(generations):
            # Create new generation
            new_population = []
            
            # Keep best 20%
            elite_size = population_size // 5
            for i in range(elite_size):
                new_population.append(fitness[i][1])
            
            # Generate rest through crossover and mutation
            while len(new_population) < population_size:
                # Tournament selection
                parent1 = random.choice(fitness[:population_size//2])[1]
                parent2 = random.choice(fitness[:population_size//2])[1]
                
                # Crossover
                child = self.crossover(parent1, parent2)
                
                # Mutation
                if random.random() < 0.8:
                    child = self.mutate_params(child, mutation_rate=0.2)
                
                new_population.append(child)
            
            # Evaluate new generation
            population = new_population
            fitness = [(self.evaluate_params(p, cases), p) for p in population]
            fitness.sort(key=lambda x: x[0])
            
            # Track best
            if fitness[0][0] < best_error:
                best_error = fitness[0][0]
                best_params = fitness[0][1]
                print(f"Generation {gen + 1}: New best error ${best_error:.2f}")
        
        return best_params, best_error


def main():
    """Run optimization and save results."""
    # Load cases
    with open('../public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("Starting parameter optimization...")
    print("=" * 60)
    
    # Split data
    random.shuffle(cases)
    train_size = int(0.8 * len(cases))
    train_cases = cases[:train_size]
    test_cases = cases[train_size:]
    
    # Run optimization
    optimizer = ParameterOptimizer()
    best_params, train_error = optimizer.optimize(train_cases, generations=30, population_size=50)
    
    # Test on validation set
    test_error = optimizer.evaluate_params(best_params, test_cases)
    
    print("\n" + "=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)
    print(f"Training error: ${train_error:.2f}")
    print(f"Test error: ${test_error:.2f}")
    
    # Save optimized parameters
    with open('optimized_params.json', 'w') as f:
        json.dump(best_params, f, indent=2)
    
    print("\nOptimized parameters saved to optimized_params.json")
    
    # Generate optimized calculator
    generate_optimized_calculator(best_params)
    
    print("Optimized calculator saved to reimbursement_calculator_optimized.py")


def generate_optimized_calculator(params: Dict):
    """Generate calculator with optimized parameters."""
    code = f'''#!/usr/bin/env python3
"""
ACME Corp Reimbursement Calculator - Optimized Version
Auto-generated with machine learning optimized parameters
"""

import random


def calculate_reimbursement(trip_duration_days: int, miles_traveled: float, 
                           total_receipts_amount: float) -> float:
    """Calculate reimbursement using optimized parameters."""
    
    # Optimized parameters from ML
    BASE_PER_DIEM = {params['base_per_diem']:.2f}
    FIVE_DAY_BONUS = {params['five_day_bonus_rate']:.3f}
    
    MILEAGE_TIERS = [
        ({params['mileage_tier_1']:.0f}, {params['mileage_rate_0']:.3f}),
        ({params['mileage_tier_2']:.0f}, {params['mileage_rate_1']:.3f}),
        ({params['mileage_tier_3']:.0f}, {params['mileage_rate_2']:.3f}),
        ({params['mileage_tier_4']:.0f}, {params['mileage_rate_3']:.3f}),
        (float('inf'), {params['mileage_rate_4']:.3f})
    ]
    
    EFFICIENCY_BONUS = {params['efficiency_bonus']:.3f}
    EFFICIENCY_RANGE = ({params['efficiency_low']:.0f}, {params['efficiency_high']:.0f})
    
    SMALL_RECEIPT_THRESH = {params['small_receipt_thresh']:.0f}
    SMALL_RECEIPT_PENALTY = {params['small_receipt_penalty']:.3f}
    MEDIUM_RECEIPT_RANGE = ({params['medium_receipt_low']:.0f}, {params['medium_receipt_high']:.0f})
    MEDIUM_RECEIPT_COVERAGE = {params['medium_receipt_coverage']:.3f}
    HIGH_RECEIPT_COVERAGE = {params['high_receipt_coverage']:.3f}
    
    CLUSTER_MULTIPLIERS = [
        {params['cluster_mult_0']:.3f},  # Road warrior
        {params['cluster_mult_1']:.3f},  # Optimal business
        {params['cluster_mult_2']:.3f},  # Extended low
        {params['cluster_mult_3']:.3f},  # Standard
        {params['cluster_mult_4']:.3f},  # Local
        {params['cluster_mult_5']:.3f}   # High spend
    ]
    
    # Classify trip
    if trip_duration_days == 0:
        cluster = 3
    else:
        mpd = miles_traveled / trip_duration_days
        rpd = total_receipts_amount / trip_duration_days
        
        if mpd > 350 and trip_duration_days <= 3:
            cluster = 0
        elif trip_duration_days == 5 and 150 <= mpd <= 250 and rpd < 120:
            cluster = 1
        elif trip_duration_days >= 7 and mpd < 150:
            cluster = 2
        elif rpd > 130:
            cluster = 5
        elif miles_traveled < 80 and trip_duration_days <= 2:
            cluster = 4
        else:
            cluster = 3
    
    # Per diem
    per_diem = BASE_PER_DIEM * trip_duration_days
    if trip_duration_days == 5:
        per_diem *= (1 + FIVE_DAY_BONUS)
    
    # Mileage
    mileage = 0.0
    remaining = miles_traveled
    prev_tier = 0
    
    for tier_limit, rate in MILEAGE_TIERS:
        if remaining <= 0:
            break
        tier_miles = min(remaining, tier_limit - prev_tier)
        mileage += tier_miles * rate
        remaining -= tier_miles
        prev_tier = tier_limit
    
    # Efficiency bonus
    efficiency_bonus = 0.0
    if trip_duration_days > 0:
        mpd = miles_traveled / trip_duration_days
        if EFFICIENCY_RANGE[0] <= mpd <= EFFICIENCY_RANGE[1]:
            efficiency_bonus = (per_diem + mileage) * EFFICIENCY_BONUS
    
    # Receipt reimbursement
    if total_receipts_amount == 0:
        receipt_reimb = 0.0
    elif total_receipts_amount < SMALL_RECEIPT_THRESH:
        receipt_reimb = total_receipts_amount * SMALL_RECEIPT_PENALTY
    elif MEDIUM_RECEIPT_RANGE[0] <= total_receipts_amount <= MEDIUM_RECEIPT_RANGE[1]:
        receipt_reimb = total_receipts_amount * MEDIUM_RECEIPT_COVERAGE
    else:
        base = MEDIUM_RECEIPT_RANGE[1] * HIGH_RECEIPT_COVERAGE
        excess = total_receipts_amount - MEDIUM_RECEIPT_RANGE[1]
        excess_rate = 0.6 * (1 - excess / 3000)
        excess_rate = max(0.2, excess_rate)
        receipt_reimb = base + (excess * excess_rate)
    
    # Total with cluster adjustment
    total = per_diem + mileage + efficiency_bonus + receipt_reimb
    total *= CLUSTER_MULTIPLIERS[cluster]
    
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
    
    with open('reimbursement_calculator_optimized.py', 'w') as f:
        f.write(code)


if __name__ == "__main__":
    random.seed(42)
    main()