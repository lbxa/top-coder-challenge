#!/usr/bin/env python3
"""
Simple Duration Optimizer - Focused approach
"""

import json
import subprocess


def test_params(five_day_bonus):
    """Test specific 5-day bonus amount."""
    # Update duration.py
    with open('components/duration/duration.py', 'r') as f:
        content = f.read()
    
    # Replace the 5-day bonus amount
    import re
    new_content = re.sub(
        r'self\.five_day_bonus_amount = \d+\.?\d*',
        f'self.five_day_bonus_amount = {five_day_bonus}',
        content
    )
    
    with open('components/duration/duration.py', 'w') as f:
        f.write(new_content)
    
    # Run evaluation
    result = subprocess.run(['./eval.sh'], capture_output=True, text=True)
    
    # Extract metrics
    avg_error = None
    exact_matches = None
    
    for line in result.stdout.split('\n'):
        if 'Average error:' in line:
            avg_error = float(line.split('$')[1])
        elif 'Exact matches' in line and '(' in line:
            exact_matches = int(line.split(':')[1].split('(')[0].strip())
    
    return avg_error, exact_matches


def main():
    print("Testing 5-day bonus amounts...")
    
    # Analyze 5-day cases specifically
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    five_day_cases = [c for c in cases if c['input']['trip_duration_days'] == 5]
    print(f"Found {len(five_day_cases)} 5-day trip cases")
    
    # Test different bonus amounts
    best_bonus = 0
    best_error = float('inf')
    
    for bonus in [0, 25, 50, 75, 100, 125, 150]:
        print(f"\nTesting 5-day bonus = ${bonus}")
        avg_error, exact_matches = test_params(bonus)
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Exact matches: {exact_matches}")
        
        if avg_error < best_error:
            best_error = avg_error
            best_bonus = bonus
    
    print(f"\nBest 5-day bonus: ${best_bonus}")
    
    # Apply best parameters
    test_params(best_bonus)


if __name__ == "__main__":
    main()