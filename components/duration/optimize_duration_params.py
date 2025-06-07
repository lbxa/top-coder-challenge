#!/usr/bin/env python3
"""
Duration Parameter Optimizer

Analyzes test cases to find optimal duration parameters.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_evaluation():
    """Run eval.sh and capture results."""
    try:
        result = subprocess.run(['./eval.sh'], capture_output=True, text=True)
        output = result.stdout
        
        # Extract key metrics
        for line in output.split('\n'):
            if 'Average error:' in line:
                avg_error = float(line.split('$')[1])
            elif 'Exact matches' in line and '(' in line:
                exact_matches = int(line.split(':')[1].split('(')[0].strip())
                
        return avg_error, exact_matches
    except Exception as e:
        print(f"Error running evaluation: {e}")
        return float('inf'), 0


def analyze_duration_patterns():
    """Analyze public cases for duration patterns."""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    duration_errors = {}
    
    # Group cases by duration
    for case in cases:
        duration = case['input']['trip_duration_days']
        if duration not in duration_errors:
            duration_errors[duration] = []
        
        # Run single case to get actual output
        cmd = ['./run.sh', 
               str(duration),
               str(case['input']['miles_traveled']),
               str(case['input']['total_receipts_amount'])]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            actual = float(result.stdout.strip())
            expected = case['expected_output']
            error = actual - expected
            duration_errors[duration].append({
                'error': error,
                'case': case,
                'actual': actual,
                'expected': expected
            })
        except:
            pass
    
    # Analyze patterns
    print("\nDuration Analysis:")
    for duration in sorted(duration_errors.keys()):
        errors = duration_errors[duration]
        if errors:
            avg_error = sum(e['error'] for e in errors) / len(errors)
            print(f"\nDuration {duration} days:")
            print(f"  Cases: {len(errors)}")
            print(f"  Avg Error: ${avg_error:.2f}")
            
            # Show sample errors
            sorted_errors = sorted(errors, key=lambda x: abs(x['error']), reverse=True)
            if len(sorted_errors) > 0:
                for e in sorted_errors[:3]:
                    print(f"    Error: ${e['error']:.2f}, Miles: {e['case']['input']['miles_traveled']}, Receipts: ${e['case']['input']['total_receipts_amount']}")


def test_duration_params(params):
    """Test specific duration parameters."""
    # Update duration.py with new parameters
    duration_file = Path(__file__).parent / 'duration.py'
    
    with open(duration_file, 'r') as f:
        content = f.read()
    
    # Replace parameters
    new_content = content
    for param, value in params.items():
        if param == 'five_day_bonus_enabled':
            old_line = f"self.five_day_bonus_enabled = {not value}"
            new_line = f"self.five_day_bonus_enabled = {value}"
            new_content = new_content.replace(old_line, new_line)
            # Also try the current value
            old_line = f"self.five_day_bonus_enabled = {value}"
            new_content = new_content.replace(old_line, new_line)
        elif param == 'five_day_bonus_amount':
            # Find and replace the line
            import re
            pattern = r'self\.five_day_bonus_amount = \d+\.?\d*'
            new_content = re.sub(pattern, f'self.five_day_bonus_amount = {value}', new_content)
        elif param == 'short_trip_multiplier':
            import re
            pattern = r'self\.short_trip_multiplier = \d+\.?\d*'
            new_content = re.sub(pattern, f'self.short_trip_multiplier = {value}', new_content)
        elif param == 'long_trip_diminishing_factor':
            import re
            pattern = r'self\.long_trip_diminishing_factor = \d+\.?\d*'
            new_content = re.sub(pattern, f'self.long_trip_diminishing_factor = {value}', new_content)
    
    with open(duration_file, 'w') as f:
        f.write(new_content)
    
    # Run evaluation
    return run_evaluation()


def optimize():
    """Main optimization loop."""
    print("Starting Duration Parameter Optimization")
    print("=" * 50)
    
    # First, analyze patterns
    analyze_duration_patterns()
    
    # Test different parameter combinations
    best_params = {}
    best_score = float('inf')
    best_exact = 0
    
    # Test 5-day bonus variations
    print("\n\nTesting 5-day bonus variations...")
    for bonus_amount in [0, 25, 50, 75, 100, 125, 150]:
        params = {'five_day_bonus_amount': bonus_amount}
        avg_error, exact_matches = test_duration_params(params)
        print(f"  5-day bonus ${bonus_amount}: avg_error=${avg_error:.2f}, exact_matches={exact_matches}")
        
        if avg_error < best_score:
            best_score = avg_error
            best_exact = exact_matches
            best_params = params.copy()
    
    # Test if 5-day bonus should be disabled
    print("\nTesting 5-day bonus enabled/disabled...")
    for enabled in [True, False]:
        params = {'five_day_bonus_enabled': enabled, 'five_day_bonus_amount': best_params.get('five_day_bonus_amount', 50)}
        avg_error, exact_matches = test_duration_params(params)
        print(f"  5-day bonus enabled={enabled}: avg_error=${avg_error:.2f}, exact_matches={exact_matches}")
        
        if avg_error < best_score:
            best_score = avg_error
            best_exact = exact_matches
            best_params = params.copy()
    
    # Test short trip multipliers
    print("\nTesting short trip multipliers...")
    for multiplier in [0.8, 0.9, 1.0, 1.1, 1.2]:
        params = best_params.copy()
        params['short_trip_multiplier'] = multiplier
        avg_error, exact_matches = test_duration_params(params)
        print(f"  Short trip multiplier {multiplier}: avg_error=${avg_error:.2f}, exact_matches={exact_matches}")
        
        if avg_error < best_score:
            best_score = avg_error
            best_exact = exact_matches
            best_params = params.copy()
    
    # Test long trip diminishing factors
    print("\nTesting long trip diminishing factors...")
    for factor in [0.85, 0.90, 0.95, 1.0, 1.05]:
        params = best_params.copy()
        params['long_trip_diminishing_factor'] = factor
        avg_error, exact_matches = test_duration_params(params)
        print(f"  Long trip factor {factor}: avg_error=${avg_error:.2f}, exact_matches={exact_matches}")
        
        if avg_error < best_score:
            best_score = avg_error
            best_exact = exact_matches
            best_params = params.copy()
    
    print("\n" + "=" * 50)
    print(f"Best parameters found:")
    print(f"  Parameters: {best_params}")
    print(f"  Average error: ${best_score:.2f}")
    print(f"  Exact matches: {best_exact}")
    
    # Apply best parameters
    test_duration_params(best_params)
    
    return best_params


if __name__ == "__main__":
    optimize()