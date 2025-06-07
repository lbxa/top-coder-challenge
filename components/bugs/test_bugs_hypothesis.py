#!/usr/bin/env python3
"""
Test script to validate the bugs component hypotheses.

This script tests:
1. Current cents bug implementation (.49 and .99 endings)
2. Alternative trigger values
3. Different bonus amounts
4. Edge cases and interactions
"""

import json
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from components.bugs.bugs import BugProcessor
from reimbursement_calculator import ReimbursementCalculator


def test_cents_bug_behavior():
    """Test the basic cents bug behavior with current implementation."""
    print("Testing Current Cents Bug Implementation")
    print("=" * 50)
    
    bug_processor = BugProcessor()
    
    # Test various receipt amounts
    test_amounts = [
        100.49,  # Should trigger
        100.99,  # Should trigger
        100.48,  # Should not trigger
        100.50,  # Should not trigger
        200.49,  # Should trigger
        350.99,  # Should trigger
        425.19,  # Should not trigger
        500.00,  # Should not trigger
        # Edge cases
        0.49,    # Small amount with trigger
        0.99,    # Small amount with trigger
        9999.49, # Large amount with trigger
        -100.49, # Negative amount (edge case)
    ]
    
    print(f"Current parameters: {bug_processor.get_parameters()}")
    print()
    
    for amount in test_amounts:
        adjustment = bug_processor.apply_bugs(amount)
        cents = int((amount * 100) % 100)
        print(f"Receipts: ${amount:8.2f} | Cents: {cents:2d} | Bug Adjustment: ${adjustment:6.2f}")
    
    print()


def test_alternative_trigger_values():
    """Test alternative cents values that might trigger the bug."""
    print("\nTesting Alternative Trigger Values")
    print("=" * 50)
    
    bug_processor = BugProcessor()
    
    # Test all cents values from 00 to 99
    receipt_base = 100.00
    trigger_counts = {}
    
    # Load public cases to analyze actual patterns
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Analyze cents distribution in test cases
    cents_distribution = {}
    for case in public_cases:
        receipts = case['input']['total_receipts_amount']
        cents = int((receipts * 100) % 100)
        cents_distribution[cents] = cents_distribution.get(cents, 0) + 1
    
    print("Cents Distribution in Test Cases:")
    # Show top 10 most common cents values
    sorted_cents = sorted(cents_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    for cents, count in sorted_cents:
        print(f"  .{cents:02d}: {count} occurrences")
    
    print("\nTesting Alternative Sets of Trigger Values:")
    
    # Different hypotheses for trigger values
    alternative_triggers = [
        [49, 99],           # Current
        [19, 49, 79, 99],   # All 9s
        [49, 50, 99, 00],   # Include boundaries
        [25, 50, 75, 00],   # Quarter values
        [99],               # Only 99
        [49],               # Only 49
    ]
    
    for triggers in alternative_triggers:
        bug_processor.cents_bug_values = triggers
        
        # Test on sample cases
        total_adjustment = 0
        trigger_count = 0
        
        for case in public_cases[:100]:  # Test on first 100 cases
            receipts = case['input']['total_receipts_amount']
            adjustment = bug_processor.apply_bugs(receipts)
            if adjustment > 0:
                trigger_count += 1
                total_adjustment += adjustment
        
        print(f"\nTriggers {triggers}: {trigger_count} hits, ${total_adjustment:.2f} total adjustment")


def test_different_bonus_amounts():
    """Test different bonus amounts for the cents bug."""
    print("\n\nTesting Different Bonus Amounts")
    print("=" * 50)
    
    # Load test cases
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    calculator = ReimbursementCalculator()
    bug_processor = BugProcessor()
    
    # Test different bonus amounts
    bonus_amounts = [5.00, 6.00, 7.00, 7.50, 8.00, 9.00, 10.00]
    
    print("Testing bonus amounts on cases with .49 or .99 endings:")
    
    # Find cases with trigger cents
    trigger_cases = []
    for case in public_cases:
        cents = int((case['input']['total_receipts_amount'] * 100) % 100)
        if cents in [49, 99]:
            trigger_cases.append(case)
    
    print(f"Found {len(trigger_cases)} cases with .49 or .99 endings")
    
    # Since we can't directly modify the calculator's bug processor,
    # we'll need to test this differently
    print("\nNote: Cannot directly test different bonus amounts with current architecture")
    print("The bugs component is encapsulated within the calculator")


def test_edge_cases():
    """Test edge cases and unusual scenarios."""
    print("\n\nTesting Edge Cases")
    print("=" * 50)
    
    bug_processor = BugProcessor()
    
    edge_cases = [
        # Floating point precision
        100.489999999,
        100.490000001,
        100.989999999,
        100.990000001,
        # Very small amounts
        0.01,
        0.49,
        0.99,
        # Negative amounts
        -50.49,
        -100.99,
        # Very large amounts
        999999.49,
        1000000.99,
        # Special values
        float('inf'),
        float('-inf'),
        0.0,
    ]
    
    print("Testing edge cases:")
    for amount in edge_cases:
        try:
            adjustment = bug_processor.apply_bugs(amount)
            print(f"Amount: {amount:15} | Adjustment: ${adjustment:6.2f}")
        except Exception as e:
            print(f"Amount: {amount:15} | Error: {e}")


def analyze_bug_impact():
    """Analyze the overall impact of the bugs component."""
    print("\n\nAnalyzing Bug Component Impact")
    print("=" * 50)
    
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    calculator = ReimbursementCalculator()
    
    # Count cases affected by bugs
    bug_affected_count = 0
    total_bug_adjustment = 0
    
    bug_processor = BugProcessor()
    
    for case in public_cases:
        bug_adjustment = bug_processor.apply_bugs(case['input']['total_receipts_amount'])
        if bug_adjustment > 0:
            bug_affected_count += 1
            total_bug_adjustment += bug_adjustment
    
    print(f"Cases affected by bugs: {bug_affected_count}/{len(public_cases)} ({bug_affected_count/len(public_cases)*100:.1f}%)")
    print(f"Total bug adjustments: ${total_bug_adjustment:.2f}")
    print(f"Average adjustment when triggered: ${total_bug_adjustment/max(bug_affected_count, 1):.2f}")
    
    # Analyze correlation with accuracy
    print("\nAnalyzing correlation with accuracy:")
    
    # Test with and without bugs
    with_bugs_error = 0
    without_bugs_error = 0
    
    for case in public_cases:
        # With bugs
        result_with = calculator.calculate_reimbursement(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'],
            case['input']['total_receipts_amount']
        )
        with_bugs_error += abs(result_with - case['expected_output'])
        
        # We can't easily test without bugs due to encapsulation
        # So we'll skip this comparison
    
    print(f"Total error with current implementation: ${with_bugs_error:.2f}")
    print("\nNote: Cannot test without bugs due to encapsulated architecture")


if __name__ == "__main__":
    test_cents_bug_behavior()
    test_alternative_trigger_values()
    test_different_bonus_amounts()
    test_edge_cases()
    analyze_bug_impact()