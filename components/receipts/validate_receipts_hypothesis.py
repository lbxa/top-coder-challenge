"""
Validate receipt processing hypotheses by comparing against expected values.

This script isolates the receipt component to understand its contribution
independently of other components.
"""

import json
import statistics
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from components.receipts.receipts import ReceiptProcessor


def load_public_cases():
    """Load public test cases."""
    with open("/Users/lchubarbos001/u/top-coder-challenge/public_cases.json", 'r') as f:
        return json.load(f)


def analyze_receipt_contribution():
    """Analyze how receipts should be processed based on patterns."""
    cases = load_public_cases()
    processor = ReceiptProcessor()
    
    print("Receipt Processing Pattern Analysis")
    print("=" * 60)
    
    # Look for patterns in receipt processing
    patterns = {
        'zero_receipts': [],
        'small_receipts': [],  # < $100
        'moderate_receipts': [],  # $100-500
        'high_receipts': [],  # > $500
    }
    
    for case in cases:
        days = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        
        if receipts == 0:
            patterns['zero_receipts'].append(case)
        elif receipts < 100:
            patterns['small_receipts'].append(case)
        elif receipts < 500:
            patterns['moderate_receipts'].append(case)
        else:
            patterns['high_receipts'].append(case)
    
    # Analyze each pattern group
    for pattern_name, pattern_cases in patterns.items():
        if not pattern_cases:
            continue
            
        print(f"\n{pattern_name.replace('_', ' ').title()}: {len(pattern_cases)} cases")
        print("-" * 40)
        
        # For zero receipts, check if there's any special handling
        if pattern_name == 'zero_receipts':
            # Just count them
            trip_lengths = [c['input']['trip_duration_days'] for c in pattern_cases]
            print(f"  Trip lengths: min={min(trip_lengths)}, max={max(trip_lengths)}, avg={statistics.mean(trip_lengths):.1f}")
            continue
        
        # For non-zero receipts, analyze processing patterns
        receipt_ratios = []
        
        for case in pattern_cases[:20]:  # Sample first 20 cases
            days = case['input']['trip_duration_days']
            receipts = case['input']['total_receipts_amount']
            receipts_per_day = receipts / days if days > 0 else 0
            
            # Process with our current model
            processed = processor.process(days, receipts)
            ratio = processed / receipts if receipts > 0 else 0
            
            receipt_ratios.append({
                'days': days,
                'receipts': receipts,
                'receipts_per_day': receipts_per_day,
                'processed': processed,
                'ratio': ratio
            })
        
        # Show statistics
        if receipt_ratios:
            ratios = [r['ratio'] for r in receipt_ratios]
            print(f"  Processing ratios: min={min(ratios):.2%}, max={max(ratios):.2%}, avg={statistics.mean(ratios):.2%}")
            
            # Show a few examples
            print(f"\n  Examples:")
            for r in receipt_ratios[:5]:
                print(f"    {r['days']} days, ${r['receipts']:.2f} receipts (${r['receipts_per_day']:.2f}/day)")
                print(f"      Processed: ${r['processed']:.2f} ({r['ratio']:.2%} of receipts)")


def test_new_hypothesis():
    """Test a new hypothesis based on the analysis."""
    cases = load_public_cases()
    
    print("\n\nTesting New Hypothesis: Tiered Receipt Processing")
    print("=" * 60)
    
    # New hypothesis: Different processing rates based on amount ranges
    def process_receipts_new(days, receipts):
        if receipts == 0:
            return 0
        
        receipts_per_day = receipts / days if days > 0 else 0
        
        # Base processing
        processed = receipts
        
        # Apply different rates based on daily amount
        if receipts_per_day < 20:
            # Very low receipts - heavy penalty
            processed = receipts * 0.2  # Only 20% reimbursed
        elif receipts_per_day < 50:
            # Low receipts - moderate penalty
            processed = receipts * 0.5  # 50% reimbursed
        elif receipts_per_day < 100:
            # Normal receipts - slight penalty
            processed = receipts * 0.8  # 80% reimbursed
        elif receipts_per_day < 150:
            # Good receipts - full reimbursement
            processed = receipts * 1.0  # 100% reimbursed
        else:
            # High receipts - penalty for overspending
            base = 150 * days  # Cap at $150/day
            excess = receipts - base
            processed = base + excess * 0.5  # 50% of excess
        
        return max(0, processed)
    
    # Test this hypothesis
    total_error = 0
    count = 0
    
    for case in cases:
        days = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        
        if receipts > 0:
            processed_new = process_receipts_new(days, receipts)
            processed_old = ReceiptProcessor().process(days, receipts)
            
            # We don't have the expected receipt value directly,
            # so we'll compare the processing approaches
            print(f"\nCase: {days} days, ${receipts:.2f} receipts")
            print(f"  Current model: ${processed_old:.2f}")
            print(f"  New hypothesis: ${processed_new:.2f}")
            print(f"  Difference: ${processed_new - processed_old:.2f}")
            
            count += 1
            if count >= 10:
                break


def analyze_trip_length_patterns():
    """Analyze if trip length affects receipt processing."""
    cases = load_public_cases()
    processor = ReceiptProcessor()
    
    print("\n\nTrip Length Impact on Receipt Processing")
    print("=" * 60)
    
    # Group by trip length
    trip_groups = {
        '1-2 days': [],
        '3-5 days': [],
        '6-7 days': [],
        '8-10 days': [],
        '11+ days': []
    }
    
    for case in cases:
        days = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        
        if receipts > 0:  # Only non-zero receipts
            if days <= 2:
                trip_groups['1-2 days'].append(case)
            elif days <= 5:
                trip_groups['3-5 days'].append(case)
            elif days <= 7:
                trip_groups['6-7 days'].append(case)
            elif days <= 10:
                trip_groups['8-10 days'].append(case)
            else:
                trip_groups['11+ days'].append(case)
    
    # Analyze each group
    for group_name, group_cases in trip_groups.items():
        if not group_cases:
            continue
            
        print(f"\n{group_name}: {len(group_cases)} cases")
        
        # Calculate receipt processing patterns
        processing_data = []
        
        for case in group_cases:
            days = case['input']['trip_duration_days']
            receipts = case['input']['total_receipts_amount']
            receipts_per_day = receipts / days
            
            processed = processor.process(days, receipts)
            ratio = processed / receipts if receipts > 0 else 0
            
            processing_data.append({
                'receipts_per_day': receipts_per_day,
                'ratio': ratio
            })
        
        # Find thresholds where penalties kick in
        high_spending = [d for d in processing_data if d['receipts_per_day'] > 100]
        if high_spending:
            ratios = [d['ratio'] for d in high_spending]
            print(f"  High spending (>$100/day): {len(high_spending)} cases")
            print(f"    Processing ratio: avg={statistics.mean(ratios):.2%}")
        
        low_spending = [d for d in processing_data if d['receipts_per_day'] < 30]
        if low_spending:
            ratios = [d['ratio'] for d in low_spending]
            print(f"  Low spending (<$30/day): {len(low_spending)} cases")
            print(f"    Processing ratio: avg={statistics.mean(ratios):.2%}")


if __name__ == "__main__":
    analyze_receipt_contribution()
    test_new_hypothesis()
    analyze_trip_length_patterns()
    
    print("\n\n✅ Validation complete!")