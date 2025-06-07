# Reimbursement Calculator Experiment Log

## Goal
Reverse-engineer ACME Corp's legacy reimbursement system with 100% accuracy on 1000 test cases.

## Key Insights from Interviews
- **Lisa (Accounting)**: $100/day baseline, 5-day bonus exists, mileage is tiered, receipts have sweet spots
- **Kevin (Procurement)**: 180-220 miles/day efficiency bonus, 6 clusters exist, tested extensively
- **Marcus (Sales)**: System rewards efficiency, 5-6 day trips are optimal
- **RED HERRINGS**: Lunar cycles, seasonal variations, department rules

## Experiment History

### Baseline (from optimized_params.json)
- Score: 11,871
- Exact matches: 0%
- Average error: $117.71
- **Issues**: ML approach failed, parameters not capturing true patterns

### V1: Ratio-based approach
- Score: 624,524
- Average error: $624.52
- **Issues**: Overestimating significantly, receipt ratios wrong

### V2: Receipt-focused with cents bug
- Score: 232,186
- Average error: $232.19
- **Key finding**: Cents bug (.49/.99) causes PENALTIES not bonuses

### V3: Comprehensive with clusters
- Score: 50,963
- Average error: $508.63
- **Issues**: Cluster logic not refined enough

### V4: Production version (current)
- Score: 23,413
- Average error: $233.13
- **Improvements**: Better receipt ratios by trip duration for high amounts
- **Remaining issues**: Still missing some patterns

## Key Patterns Discovered

1. **Receipt Amount Dominance**: 55.9% importance in ML model
2. **Cents Bug**: .49/.99 endings get 18-70% of normal reimbursement
3. **High Receipt Ratios** (>$2000):
   - 1-2 days: ~0.61
   - 3-4 days: ~0.655
   - 5-6 days: ~0.74
   - 7-8 days: ~0.71
   - 9-10 days: ~0.76
   - 11-12 days: ~0.78
   - 13-14 days: ~0.84

4. **Per-day rates**:
   - 1 day: $873 average
   - Declining with trip length

## Next Steps
1. Create comprehensive visualization of clusters
2. Analyze interaction effects more deeply
3. Fine-tune parameters based on visual insights
4. Test edge cases systematically