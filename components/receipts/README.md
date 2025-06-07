# Receipt Processor Component

## Overview

The Receipt Processor is the most complex component of the reimbursement system, handling receipt validation, penalties, and reimbursement calculations based on trip duration and spending patterns.

## Key Findings from Analysis

### 1. Receipt Processing Patterns

Based on analysis of 1,000 public test cases:

- **Small receipts (<$20/day)**: Severely penalized, often resulting in near-zero reimbursement
- **Moderate receipts ($20-50/day)**: Receive ~80% reimbursement
- **Normal receipts ($50-100/day)**: Generally full reimbursement unless over daily thresholds
- **High receipts (>threshold/day)**: Subject to overspending penalties that vary by trip length

### 2. Trip-Length Dependent Thresholds

The system applies different spending thresholds based on trip duration:

- **Short trips (1-3 days)**: $100/day threshold
- **Medium trips (4-7 days)**: $150/day threshold  
- **Long trips (8+ days)**: $120/day threshold

### 3. Overspending Penalties

When daily spending exceeds the threshold, penalties are applied:

- **Short trips**: ~45% of overage is penalized (55% retention)
- **Medium trips**: ~40% of overage is penalized (60% retention)
- **Long trips**: ~50% of overage is penalized (50% retention)

### 4. Processing Ratios by Trip Length

Average receipt retention rates for high spenders (>$100/day):

- **1-2 days**: ~57%
- **3-5 days**: ~61%
- **6-7 days**: ~67%
- **8-10 days**: ~51%
- **11+ days**: ~59%

## Current Hypotheses (Refined)

1. **Tiered spending thresholds** based on trip length
2. **Progressive penalty system** for overspending
3. **Severe penalties** for very low daily spending (<$20/day)
4. **Moderate penalties** for low-moderate spending ($20-50/day)
5. **Receipt amount cannot reduce total reimbursement below zero**

## Implementation Details

The `ReceiptProcessor` class implements the following logic:

1. **Base calculation**: Start with full receipt amount
2. **Apply overspending penalties**: Based on trip length and daily spending
3. **Apply small receipt penalties**: For low daily spending amounts
4. **Ensure non-negative**: Receipt pay cannot go below zero

## Parameters

Current optimized parameters:

```python
# Spending thresholds ($/day)
short_trip_threshold = 100.0      # 1-3 days
medium_trip_threshold = 150.0     # 4-7 days  
long_trip_threshold = 120.0       # 8+ days

# Penalty factors (lower = more penalty)
short_trip_penalty_factor = 0.45  # 45% of overage
medium_trip_penalty_factor = 0.40 # 40% of overage
long_trip_penalty_factor = 0.50   # 50% of overage

# Small receipt parameters
small_receipt_threshold = 20.0    # $/day
small_receipt_penalty_factor = 0.95  # 95% penalty (5% reimbursement)

# Moderate spending parameters
moderate_spending_threshold = 50.0   # $/day
moderate_spending_factor = 0.8       # 80% reimbursement
```

## Testing & Optimization

The component includes:

- `test_receipts.py`: Unit tests for basic functionality
- `analyze_receipts.py`: Pattern analysis across all public cases
- `validate_receipts_hypothesis.py`: Hypothesis validation
- `optimize_receipts_params.py`: Parameter optimization using grid search

## Future Improvements

Areas for potential refinement:

1. **Weekend receipt bonus**: Different processing for weekend receipts
2. **Maximum daily cap**: Hard limit on daily reimbursement (e.g., $150/day)
3. **Category-specific processing**: Different rates for different expense categories
4. **Progressive tier system**: More granular tiers instead of three categories
5. **Time-of-year adjustments**: Seasonal variations in thresholds

## Integration Notes

This component is designed to work within the modular architecture where:
- It receives trip duration and total receipt amount as inputs
- It returns the processed receipt payment amount
- It integrates with other components (per diem, mileage, bonuses, etc.)

The receipt processor is typically the third step in the calculation pipeline, after base per diem and mileage calculations.