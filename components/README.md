# Modular Reimbursement System Components

This directory contains the modular implementation of the ACME Corp reimbursement system, designed for parallel optimization by multiple AI agents.

## Architecture Overview

The system is decomposed into 5 independent components plus a coordination layer:

```
main.py (orchestrator)
├── components/per_diem.py      - Base daily rate calculation
├── components/mileage.py       - Tiered mileage rate system  
├── components/receipts.py      - Complex receipt processing with penalties
├── components/bonuses.py       - All bonus calculations
├── components/bugs.py          - System quirks and bugs
└── components/optimizer.py     - Parameter optimization coordination
```

## Component Responsibilities

### 1. Per Diem Calculator (`per_diem.py`)
**Complexity: LOW** - Ideal for new AI agents
- **Purpose**: Calculate base daily payment
- **Key Parameters**: `daily_rate` (~$100/day)
- **Focus Areas**: 
  - Validate exact daily rate
  - Check for trip-length dependent rates
  - Investigate weekend/weekday differences

### 2. Mileage Calculator (`mileage.py`) 
**Complexity: MEDIUM**
- **Purpose**: Calculate tiered mileage payments
- **Key Parameters**: `tier_1_threshold`, `tier_1_rate`, `tier_2_rate`
- **Focus Areas**:
  - Optimize tier breakpoints and rates
  - Investigate additional tiers
  - Check for mileage caps

### 3. Receipt Processor (`receipts.py`)
**Complexity: HIGH** - Most complex component
- **Purpose**: Process receipts with trip-length dependent penalties
- **Key Parameters**: Multiple thresholds and penalty factors
- **Focus Areas**:
  - Optimize penalty thresholds for each trip length
  - Fine-tune penalty factors
  - Investigate edge cases

### 4. Bonus Calculator (`bonuses.py`)
**Complexity: MEDIUM**
- **Purpose**: Calculate all positive adjustments
- **Key Parameters**: Bonus amounts and trigger conditions
- **Focus Areas**:
  - Optimize 5-day bonus amount
  - Fine-tune efficiency bonus range
  - Discover additional bonuses

### 5. Bug Processor (`bugs.py`)
**Complexity: LOW-MEDIUM**
- **Purpose**: Replicate system bugs and quirks
- **Key Parameters**: Bug trigger conditions and amounts
- **Focus Areas**:
  - Optimize cents bug parameters
  - Discover additional bugs
  - Handle edge cases

### 6. System Optimizer (`optimizer.py`)
**Complexity: HIGH** - Coordination layer
- **Purpose**: Coordinate optimization across all components
- **Features**: Parameter extraction, performance evaluation, optimization algorithms

## AI Agent Workflow

### For Individual Component Optimization:

```python
# Example: Optimizing the per diem component
from components.per_diem import PerDiemCalculator
from components.optimizer import SystemOptimizer

# Create optimizer to access test cases and evaluation
optimizer = SystemOptimizer()

# Focus on per diem component
per_diem_calc = optimizer.per_diem_calc

# Get current parameters
params = per_diem_calc.get_parameters()
print(f"Current daily rate: {params['daily_rate']}")

# Test different values
for rate in [95.0, 100.0, 105.0]:
    per_diem_calc.set_parameters({'daily_rate': rate})
    performance = optimizer.evaluate_performance()
    print(f"Rate ${rate}: {performance['exact_matches']} exact matches")
```

### For System-Wide Optimization:

```python
# Example: Using the system optimizer
from components.optimizer import SystemOptimizer

optimizer = SystemOptimizer()

# Get baseline performance
baseline = optimizer.evaluate_performance()
print(f"Baseline: {baseline['exact_matches']} exact matches")

# Run automated optimization
results = optimizer.optimize_parameters(
    method="differential_evolution",
    max_iterations=100
)

print(f"Optimized: {results['performance']['exact_matches']} exact matches")
```

## Parameter Management

Each component implements a standard interface:

- `get_parameters()` - Returns dict of current parameters
- `set_parameters(params_dict)` - Updates parameters from dict
- Component-specific calculation methods

The `SystemOptimizer` coordinates parameters across all components with prefixed names:
- `per_diem_daily_rate`
- `mileage_tier_1_rate`
- `receipts_short_trip_threshold`
- etc.

## Testing and Validation

Run the test suite to verify the modular system:

```bash
python test_modular_system.py
```

Evaluate against all 1,000 test cases:

```bash
./eval.sh
```

## Parallel Development Strategy

Multiple AI agents can work simultaneously on:

1. **Agent 1**: Per diem component optimization
2. **Agent 2**: Mileage tier structure analysis  
3. **Agent 3**: Receipt penalty system (most complex)
4. **Agent 4**: Bonus discovery and optimization
5. **Agent 5**: Bug replication and edge cases
6. **Agent 6**: System-wide parameter coordination

Each agent can:
- Focus on their component in isolation
- Use the `SystemOptimizer` for evaluation
- Share optimized parameters through the standard interface
- Coordinate through the parameter management system

## Integration Points

Components interact through the main calculation flow:

1. Calculate base components (per diem + mileage)
2. Process receipts (with penalties)
3. Add bonuses
4. Apply bugs/quirks
5. Return final amount

The modular design ensures changes to one component don't break others, enabling safe parallel development.

## Next Steps

1. Run `python test_modular_system.py` to verify setup
2. Choose a component based on complexity preference
3. Use `SystemOptimizer` for evaluation and testing
4. Focus on improving exact match count against test cases
5. Coordinate with other agents through parameter sharing 