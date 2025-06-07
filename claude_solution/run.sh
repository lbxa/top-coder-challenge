#!/bin/bash

# ACME Corp Reimbursement Calculator
# Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>

# Get input parameters
TRIP_DURATION_DAYS=$1
MILES_TRAVELED=$2
TOTAL_RECEIPTS_AMOUNT=$3

# Run the optimized calculator (best performer)
python3 -c "
from reimbursement_calculator_optimized import calculate_reimbursement
result = calculate_reimbursement($TRIP_DURATION_DAYS, $MILES_TRAVELED, $TOTAL_RECEIPTS_AMOUNT)
print(f'{result:.2f}')
"