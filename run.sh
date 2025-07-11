#!/bin/bash

# Black Box Challenge - Hybrid Approach Implementation
# This script takes three parameters and outputs the reimbursement amount
# Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>

# Use uv to run Python (as per workspace rules)
uv run python main.py "$1" "$2" "$3"