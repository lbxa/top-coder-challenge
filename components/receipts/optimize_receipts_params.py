"""
Optimizer for ReceiptProcessor parameters.

This script systematically tests different parameter combinations to find
the optimal values that minimize the average error in reimbursement calculations.
"""

import subprocess
import json
import re
from pathlib import Path
from itertools import product


def run_evaluation():
    """Run the evaluation script and return the average error."""
    try:
        # Run evaluation from the project root
        result = subprocess.run(
            ["./eval.sh"],
            capture_output=True,
            text=True,
            cwd="/Users/lchubarbos001/u/top-coder-challenge"
        )
        
        # Parse average error from output
        output = result.stdout
        match = re.search(r"Average error: \$([0-9.]+)", output)
        if match:
            return float(match.group(1))
        else:
            print("Could not parse average error from evaluation output")
            print(output)
            return float('inf')
    except Exception as e:
        print(f"Error running evaluation: {e}")
        return float('inf')


def update_receipts_params(params):
    """Update the receipts.py file with new parameters."""
    receipts_path = Path(__file__).parent / "receipts.py"
    
    with open(receipts_path, 'r') as f:
        content = f.read()
    
    # Update each parameter in the file
    for param, value in params.items():
        if param == "short_trip_threshold":
            content = re.sub(
                r'self\.short_trip_threshold = [0-9.]+',
                f'self.short_trip_threshold = {value}',
                content
            )
        elif param == "medium_trip_threshold":
            content = re.sub(
                r'self\.medium_trip_threshold = [0-9.]+',
                f'self.medium_trip_threshold = {value}',
                content
            )
        elif param == "long_trip_threshold":
            content = re.sub(
                r'self\.long_trip_threshold = [0-9.]+',
                f'self.long_trip_threshold = {value}',
                content
            )
        elif param == "short_trip_penalty_factor":
            content = re.sub(
                r'self\.short_trip_penalty_factor = [0-9.]+',
                f'self.short_trip_penalty_factor = {value}',
                content
            )
        elif param == "medium_trip_penalty_factor":
            content = re.sub(
                r'self\.medium_trip_penalty_factor = [0-9.]+',
                f'self.medium_trip_penalty_factor = {value}',
                content
            )
        elif param == "long_trip_penalty_factor":
            content = re.sub(
                r'self\.long_trip_penalty_factor = [0-9.]+',
                f'self.long_trip_penalty_factor = {value}',
                content
            )
        elif param == "small_receipt_threshold":
            content = re.sub(
                r'self\.small_receipt_threshold = [0-9.]+',
                f'self.small_receipt_threshold = {value}',
                content
            )
        elif param == "small_receipt_penalty_factor":
            content = re.sub(
                r'self\.small_receipt_penalty_factor = [0-9.]+',
                f'self.small_receipt_penalty_factor = {value}',
                content
            )
        elif param == "moderate_spending_threshold":
            content = re.sub(
                r'self\.moderate_spending_threshold = [0-9.]+',
                f'self.moderate_spending_threshold = {value}',
                content
            )
        elif param == "moderate_spending_factor":
            content = re.sub(
                r'self\.moderate_spending_factor = [0-9.]+',
                f'self.moderate_spending_factor = {value}',
                content
            )
    
    with open(receipts_path, 'w') as f:
        f.write(content)


def analyze_public_cases():
    """Analyze public cases to understand receipt patterns."""
    with open("/Users/lchubarbos001/u/top-coder-challenge/public_cases.json", 'r') as f:
        cases = json.load(f)
    
    print("\nAnalyzing receipt patterns in public cases...")
    
    # Group by trip length categories
    short_trips = []  # 1-3 days
    medium_trips = []  # 4-7 days
    long_trips = []  # 8+ days
    
    for case in cases:
        days = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        if receipts > 0:  # Only analyze cases with receipts
            receipts_per_day = receipts / days
            
            if 1 <= days <= 3:
                short_trips.append({
                    'days': days,
                    'receipts': receipts,
                    'receipts_per_day': receipts_per_day,
                    'expected': expected
                })
            elif 4 <= days <= 7:
                medium_trips.append({
                    'days': days,
                    'receipts': receipts,
                    'receipts_per_day': receipts_per_day,
                    'expected': expected
                })
            elif days >= 8:
                long_trips.append({
                    'days': days,
                    'receipts': receipts,
                    'receipts_per_day': receipts_per_day,
                    'expected': expected
                })
    
    # Find spending thresholds
    print(f"\nShort trips (1-3 days): {len(short_trips)} cases")
    if short_trips:
        high_spending = [t for t in short_trips if t['receipts_per_day'] > 70]
        print(f"  High spending (>$70/day): {len(high_spending)} cases")
        if high_spending:
            print(f"  Spending range: ${min(t['receipts_per_day'] for t in high_spending):.2f} - ${max(t['receipts_per_day'] for t in high_spending):.2f}/day")
    
    print(f"\nMedium trips (4-7 days): {len(medium_trips)} cases")
    if medium_trips:
        high_spending = [t for t in medium_trips if t['receipts_per_day'] > 100]
        print(f"  High spending (>$100/day): {len(high_spending)} cases")
        if high_spending:
            print(f"  Spending range: ${min(t['receipts_per_day'] for t in high_spending):.2f} - ${max(t['receipts_per_day'] for t in high_spending):.2f}/day")
    
    print(f"\nLong trips (8+ days): {len(long_trips)} cases")
    if long_trips:
        high_spending = [t for t in long_trips if t['receipts_per_day'] > 80]
        print(f"  High spending (>$80/day): {len(high_spending)} cases")
        if high_spending:
            print(f"  Spending range: ${min(t['receipts_per_day'] for t in high_spending):.2f} - ${max(t['receipts_per_day'] for t in high_spending):.2f}/day")
    
    # Find small receipt patterns
    all_trips = short_trips + medium_trips + long_trips
    small_receipts = [t for t in all_trips if 0 < t['receipts_per_day'] < 25]
    print(f"\nSmall receipts (<$25/day): {len(small_receipts)} cases")
    if small_receipts:
        print(f"  Range: ${min(t['receipts_per_day'] for t in small_receipts):.2f} - ${max(t['receipts_per_day'] for t in small_receipts):.2f}/day")


def optimize_parameters():
    """Optimize receipt processor parameters using grid search."""
    
    # Get baseline error
    print("Getting baseline error with current parameters...")
    baseline_error = run_evaluation()
    print(f"Baseline average error: ${baseline_error:.2f}")
    
    # Define parameter ranges to test
    param_ranges = {
        # Spending thresholds
        'short_trip_threshold': [90, 100, 110, 120],
        'medium_trip_threshold': [140, 150, 160, 170],
        'long_trip_threshold': [110, 120, 130, 140],
        
        # Penalty factors (lower = more penalty)
        'short_trip_penalty_factor': [0.40, 0.45, 0.50, 0.55],
        'medium_trip_penalty_factor': [0.35, 0.40, 0.45],
        'long_trip_penalty_factor': [0.45, 0.50, 0.55],
        
        # Small receipt parameters
        'small_receipt_threshold': [15, 20, 25],
        'small_receipt_penalty_factor': [0.90, 0.95, 0.97],
        'moderate_spending_threshold': [40, 50, 60],
        'moderate_spending_factor': [0.7, 0.8, 0.85]
    }
    
    # First optimize thresholds
    print("\n" + "="*50)
    print("Phase 1: Optimizing spending thresholds...")
    print("="*50)
    
    best_error = baseline_error
    best_params = {
        'short_trip_threshold': 100.0,
        'medium_trip_threshold': 150.0,
        'long_trip_threshold': 120.0
    }
    
    for short_t, medium_t, long_t in product(
        param_ranges['short_trip_threshold'],
        param_ranges['medium_trip_threshold'],
        param_ranges['long_trip_threshold']
    ):
        params = {
            'short_trip_threshold': short_t,
            'medium_trip_threshold': medium_t,
            'long_trip_threshold': long_t
        }
        
        print(f"\nTesting thresholds: short=${short_t}, medium=${medium_t}, long=${long_t}")
        update_receipts_params(params)
        error = run_evaluation()
        print(f"  Average error: ${error:.2f}")
        
        if error < best_error:
            best_error = error
            best_params.update(params)
            print(f"  ✓ New best error!")
    
    # Apply best thresholds
    update_receipts_params(best_params)
    
    # Then optimize penalty factors
    print("\n" + "="*50)
    print("Phase 2: Optimizing penalty factors...")
    print("="*50)
    
    for short_p, medium_p, long_p in product(
        param_ranges['short_trip_penalty_factor'],
        param_ranges['medium_trip_penalty_factor'],
        param_ranges['long_trip_penalty_factor']
    ):
        params = {
            'short_trip_penalty_factor': short_p,
            'medium_trip_penalty_factor': medium_p,
            'long_trip_penalty_factor': long_p
        }
        
        print(f"\nTesting penalties: short={short_p}, medium={medium_p}, long={long_p}")
        update_receipts_params(params)
        error = run_evaluation()
        print(f"  Average error: ${error:.2f}")
        
        if error < best_error:
            best_error = error
            best_params.update(params)
            print(f"  ✓ New best error!")
    
    # Apply best penalty factors
    update_receipts_params(best_params)
    
    # Finally optimize small receipt parameters
    print("\n" + "="*50)
    print("Phase 3: Optimizing small and moderate receipt parameters...")
    print("="*50)
    
    for small_t, small_p, mod_t, mod_f in product(
        param_ranges['small_receipt_threshold'],
        param_ranges['small_receipt_penalty_factor'],
        param_ranges['moderate_spending_threshold'],
        param_ranges['moderate_spending_factor']
    ):
        params = {
            'small_receipt_threshold': small_t,
            'small_receipt_penalty_factor': small_p,
            'moderate_spending_threshold': mod_t,
            'moderate_spending_factor': mod_f
        }
        
        print(f"\nTesting receipts: small<${small_t}/day (factor={small_p}), moderate<${mod_t}/day (factor={mod_f})")
        update_receipts_params(params)
        error = run_evaluation()
        print(f"  Average error: ${error:.2f}")
        
        if error < best_error:
            best_error = error
            best_params.update(params)
            print(f"  ✓ New best error!")
    
    # Apply all best parameters
    print("\n" + "="*50)
    print("Optimization Complete!")
    print("="*50)
    print(f"\nBest average error: ${best_error:.2f}")
    print(f"Improvement: ${baseline_error - best_error:.2f}")
    print("\nBest parameters:")
    for param, value in best_params.items():
        print(f"  {param}: {value}")
    
    # Apply best parameters
    update_receipts_params(best_params)
    
    # Run final evaluation
    print("\nRunning final evaluation with best parameters...")
    final_error = run_evaluation()
    print(f"Final average error: ${final_error:.2f}")


if __name__ == "__main__":
    print("Receipt Processor Parameter Optimizer")
    print("="*50)
    
    # First analyze the public cases
    analyze_public_cases()
    
    # Then run optimization
    print("\n\nStarting parameter optimization...")
    print("This will take several minutes as we test different combinations.")
    print("="*50)
    
    optimize_parameters()