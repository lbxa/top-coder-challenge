# ACME Corp Reimbursement Calculator Solution

This folder contains the complete solution for reverse-engineering ACME Corp's legacy reimbursement system.

## Solution Summary

After extensive analysis including k-means clustering, pattern recognition, and parameter optimization, we've developed multiple implementations to replicate the legacy system's behavior.

### Key Discoveries

1. **6 Distinct Calculation Paths**: The system uses different formulas based on trip characteristics (confirming Kevin's theory)
2. **5-Day Bonus**: 5-day trips receive approximately 15% bonus on per diem
3. **Tiered Mileage Rates**: Mileage reimbursement decreases with distance (0.58→0.52→0.47→0.42→0.38 $/mile)
4. **Efficiency Sweet Spot**: 180-220 miles/day receives ~8% bonus
5. **Receipt Penalties**: Small receipts (<$50) and high spending (>$600) are penalized
6. **Magic Cents Bug**: Receipts ending in .49 or .99 receive small bonus ($3-6)

### Files

- `reimbursement_calculator.py` - Initial implementation based on clustering analysis
- `optimize_parameters.py` - Parameter optimization using evolutionary algorithm
- `reimbursement_calculator_optimized.py` - **BEST PERFORMER** - Optimized calculator (Mean error: $117.71)
- `advanced_calculator.py` - Ensemble approach with specialized models
- `simple_robust_calculator.py` - Simplified robust implementation
- `test_accuracy.py` - Testing script for evaluation
- `compare_all.py` - Comparison of all implementations

### Best Implementation

**Use `reimbursement_calculator_optimized.py` for production**

Performance on 1000 public cases:
- Mean absolute error: $117.71 (12.2%)
- Median absolute error: $84.52 (6.2%)
- 65.6% of cases within 10% error
- 32.4% of cases within $50 error

### Usage

```python
from reimbursement_calculator_optimized import calculate_reimbursement

# Calculate reimbursement
reimbursement = calculate_reimbursement(
    trip_duration_days=5,
    miles_traveled=200,
    total_receipts_amount=450.00
)
print(f"Reimbursement: ${reimbursement:.2f}")
```

### Implementation Strategy

The solution combines:
1. Machine learning optimization for parameter tuning
2. Rule-based logic for known patterns (5-day bonus, efficiency sweet spot)
3. Cluster-specific adjustments based on trip type
4. Deterministic noise to match system variability

### Known Limitations

- Some edge cases still have high error
- System appears to have additional hidden factors not fully captured
- Very high mileage trips (>1000 miles) are challenging to predict accurately

### Future Improvements

1. Deep learning approach with more complex feature interactions
2. Time-based patterns (if timestamps were available)
3. Department-specific rules (if department data were available)
4. More sophisticated ensemble methods

## Testing

To test the implementation:

```bash
python3 test_optimized.py
```

To compare all implementations:

```bash
python3 compare_all.py
```