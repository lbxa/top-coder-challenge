# Reimbursement System Analysis

This directory contains a comprehensive analysis notebook to reverse-engineer ACME Corp's legacy reimbursement system.

## Setup

1. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

2. **Run the analysis:**
   ```bash
   ./run_analysis.py
   ```
   
   Or manually:
   ```bash
   uv run jupyter lab
   ```

3. **Open the analysis notebook:**
   - Navigate to `analysis.ipynb` in Jupyter Lab
   - Run all cells to perform the complete analysis

## Analysis Components

The notebook includes:

### 📊 Data Exploration
- Loading and examining public/private datasets
- Basic statistics and data quality checks
- Feature engineering (miles per day, receipts per day, etc.)

### 🎯 Trip Duration Analysis
- Validation of the 5-day trip bonus theory
- Per-day reimbursement rate analysis
- Distribution patterns by trip length

### 🛣️ Mileage Analysis
- Tiered mileage rate structure investigation
- Efficiency bonus analysis (180-220 miles/day sweet spot)
- Implied mileage rate calculations

### 🧾 Receipt Analysis
- Rounding bug detection (.49/.99 endings)
- Optimal spending range identification
- Receipt processing pattern analysis

### 🔍 Clustering Analysis
- K-means clustering to identify calculation paths
- Validation of Kevin's "6 calculation paths" theory
- Cluster characteristic analysis

### 🤖 Predictive Modeling
- Random Forest model for feature importance
- Interaction effect identification
- Model performance evaluation

### 💡 Implementation Guidance
- Key findings summary
- Implementation recommendations
- Next steps for building run.sh

## Key Insights Expected

Based on employee interviews, the analysis should reveal:

1. **Base per diem**: ~$100/day with 5-day bonus
2. **Mileage tiers**: Decreasing rates after ~100 miles
3. **Efficiency bonuses**: 180-220 miles/day sweet spot
4. **Receipt processing**: Diminishing returns, potential rounding bugs
5. **Special cases**: Edge cases and systematic anomalies

## Output

The analysis will generate:
- Statistical summaries and visualizations
- Feature importance rankings
- Cluster analysis results
- Implementation recommendations
- Specific parameter estimates for run.sh

## Next Steps

After running the analysis:
1. Use insights to implement initial run.sh
2. Test against public cases with eval.sh
3. Iteratively refine based on error patterns
4. Achieve >95% accuracy on public cases
5. Generate results for private cases 