#!/usr/bin/env python3
"""
Exploratory data analysis for reverse-engineering the reimbursement system.
Following the compute-optimal approach from MASTER-PLAN.md
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Load the data
print("Loading public cases...")
with open('../public_cases.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame([
    {
        'days': case['input']['trip_duration_days'],
        'miles': case['input']['miles_traveled'],
        'receipts': case['input']['total_receipts_amount'],
        'reimbursement': case['expected_output']
    }
    for case in data
])

# Add engineered features as suggested in MASTER-PLAN
df['miles_per_day'] = df['miles'] / df['days']
df['receipts_per_day'] = df['receipts'] / df['days']
df['receipt_cents'] = (df['receipts'] * 100).astype(int) % 100

print(f"Loaded {len(df)} cases")
print("\nData summary:")
print(df.describe())

# Create output directory for plots
import os
os.makedirs('plots', exist_ok=True)

# Plot 1: Per Diem Analysis - isolate base rate
print("\n1. Analyzing per diem rates...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1.1 Reimbursement vs Days (all data)
ax = axes[0, 0]
ax.scatter(df['days'], df['reimbursement'], alpha=0.5, s=20)
ax.set_xlabel('Trip Duration (days)')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Reimbursement vs Trip Duration')
ax.grid(True, alpha=0.3)

# 1.2 Focus on low miles/receipts to isolate per diem
low_activity = df[(df['miles'] < 50) & (df['receipts'] < 20)]
ax = axes[0, 1]
if len(low_activity) > 0:
    ax.scatter(low_activity['days'], low_activity['reimbursement'], alpha=0.7)
    # Fit line to estimate base per diem
    if len(low_activity) > 1:
        z = np.polyfit(low_activity['days'], low_activity['reimbursement'], 1)
        p = np.poly1d(z)
        ax.plot(sorted(low_activity['days']), p(sorted(low_activity['days'])), 
                "r--", alpha=0.8, label=f'Slope: ${z[0]:.2f}/day')
        ax.legend()
ax.set_xlabel('Trip Duration (days)')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Low Activity Trips (<50 miles, <$20 receipts)')
ax.grid(True, alpha=0.3)

# 1.3 Reimbursement per day vs days
df['reimb_per_day'] = df['reimbursement'] / df['days']
ax = axes[1, 0]
days_mean = df.groupby('days')['reimb_per_day'].agg(['mean', 'std', 'count'])
days_mean = days_mean[days_mean['count'] >= 5]  # Only show days with enough samples
ax.errorbar(days_mean.index, days_mean['mean'], yerr=days_mean['std'], 
            fmt='o-', capsize=5, capthick=2)
ax.axhline(y=100, color='r', linestyle='--', alpha=0.5, label='$100/day baseline')
ax.set_xlabel('Trip Duration (days)')
ax.set_ylabel('Average Reimbursement per Day ($)')
ax.set_title('Daily Rate by Trip Duration')
ax.legend()
ax.grid(True, alpha=0.3)

# 1.4 5-day bonus detection
ax = axes[1, 1]
day_counts = df['days'].value_counts().sort_index()
colors = ['red' if d == 5 else 'blue' for d in day_counts.index]
ax.bar(day_counts.index, day_counts.values, color=colors)
ax.set_xlabel('Trip Duration (days)')
ax.set_ylabel('Number of Cases')
ax.set_title('Trip Duration Distribution (5-day trips in red)')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('plots/01_per_diem_analysis.png', dpi=150)
plt.close()

# Plot 2: Mileage Tier Analysis
print("\n2. Analyzing mileage tiers...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 2.1 Raw reimbursement vs miles
ax = axes[0, 0]
ax.scatter(df['miles'], df['reimbursement'], alpha=0.5, s=20)
ax.set_xlabel('Miles Traveled')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Reimbursement vs Miles Traveled')
ax.grid(True, alpha=0.3)

# 2.2 Subtract estimated per diem to isolate mileage component
df['est_per_diem'] = df['days'] * 100  # Initial estimate
df['non_per_diem'] = df['reimbursement'] - df['est_per_diem']

ax = axes[0, 1]
ax.scatter(df['miles'], df['non_per_diem'], alpha=0.5, s=20)
ax.axvline(x=100, color='r', linestyle='--', alpha=0.5, label='100 mile threshold')
ax.set_xlabel('Miles Traveled')
ax.set_ylabel('Reimbursement - Estimated Per Diem ($)')
ax.set_title('Non-Per-Diem Component vs Miles')
ax.legend()
ax.grid(True, alpha=0.3)

# 2.3 Cents per mile analysis
df['cents_per_mile'] = df['non_per_diem'] / df['miles']
df_valid = df[df['miles'] > 0]

ax = axes[1, 0]
ax.scatter(df_valid['miles'], df_valid['cents_per_mile'], alpha=0.5, s=20)
ax.axhline(y=0.58, color='g', linestyle='--', alpha=0.5, label='$0.58/mile')
ax.axhline(y=0.45, color='orange', linestyle='--', alpha=0.5, label='$0.45/mile')
ax.set_xlabel('Miles Traveled')
ax.set_ylabel('Effective Cents per Mile')
ax.set_title('Mileage Rate vs Distance')
ax.set_ylim(-0.5, 2.0)
ax.legend()
ax.grid(True, alpha=0.3)

# 2.4 Miles per day efficiency analysis
ax = axes[1, 1]
ax.scatter(df['miles_per_day'], df['reimbursement'], alpha=0.5, s=20)
ax.axvspan(180, 220, alpha=0.2, color='green', label='Efficiency sweet spot')
ax.set_xlabel('Miles per Day')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Efficiency Analysis (Miles/Day)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/02_mileage_analysis.png', dpi=150)
plt.close()

# Plot 3: Receipt Analysis
print("\n3. Analyzing receipt patterns...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 3.1 Reimbursement vs receipts
ax = axes[0, 0]
ax.scatter(df['receipts'], df['reimbursement'], alpha=0.5, s=20)
ax.set_xlabel('Total Receipts ($)')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Reimbursement vs Receipt Amount')
ax.grid(True, alpha=0.3)

# 3.2 Receipts per day by trip duration
ax = axes[0, 1]
for days in sorted(df['days'].unique())[:10]:  # First 10 trip lengths
    subset = df[df['days'] == days]
    if len(subset) > 5:
        ax.scatter(subset['receipts_per_day'], subset['reimbursement'], 
                   alpha=0.6, s=30, label=f'{days} days')
ax.axvline(x=75, color='r', linestyle='--', alpha=0.5, label='Short trip limit')
ax.axvline(x=120, color='orange', linestyle='--', alpha=0.5, label='Medium trip limit')
ax.axvline(x=90, color='purple', linestyle='--', alpha=0.5, label='Long trip limit')
ax.set_xlabel('Receipts per Day ($)')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Receipt Spending Patterns by Trip Length')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)

# 3.3 Small receipt penalty detection
ax = axes[1, 0]
small_receipts = df[df['receipts'] < 100]
ax.scatter(small_receipts['receipts'], small_receipts['reimbursement'], alpha=0.5, s=20)
ax.axvspan(12, 50, alpha=0.2, color='red', label='Penalty zone')
ax.set_xlabel('Total Receipts ($)')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Small Receipt Analysis')
ax.set_xlim(0, 100)
ax.legend()
ax.grid(True, alpha=0.3)

# 3.4 Receipt cents bug detection
ax = axes[1, 1]
cents_49_99 = df[df['receipt_cents'].isin([49, 99])]
other = df[~df['receipt_cents'].isin([49, 99])]
ax.scatter(other['receipts'], other['reimbursement'], alpha=0.3, s=20, label='Normal')
ax.scatter(cents_49_99['receipts'], cents_49_99['reimbursement'], 
           color='red', alpha=0.8, s=40, label='Cents = 49 or 99')
ax.set_xlabel('Total Receipts ($)')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Receipt Cents Bug Detection')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/03_receipt_analysis.png', dpi=150)
plt.close()

# Plot 4: Special Cases and Bonuses
print("\n4. Analyzing special cases and bonuses...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 4.1 5-day bonus visualization
ax = axes[0, 0]
for days in [4, 5, 6]:
    subset = df[df['days'] == days]
    ax.scatter(subset['miles'], subset['reimbursement'], alpha=0.6, s=30, label=f'{days} days')
ax.set_xlabel('Miles Traveled')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('5-Day Bonus Detection')
ax.legend()
ax.grid(True, alpha=0.3)

# 4.2 Efficiency bonus (miles per day sweet spot)
ax = axes[0, 1]
efficiency_bonus = df[(df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)]
other = df[(df['miles_per_day'] < 180) | (df['miles_per_day'] > 220)]
ax.scatter(other['days'], other['reimbursement'], alpha=0.3, s=20, label='Normal')
ax.scatter(efficiency_bonus['days'], efficiency_bonus['reimbursement'], 
           color='green', alpha=0.8, s=40, label='Efficiency range')
ax.set_xlabel('Trip Duration (days)')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Efficiency Bonus (180-220 miles/day)')
ax.legend()
ax.grid(True, alpha=0.3)

# 4.3 Combined conditions analysis
ax = axes[1, 0]
# Identify potential sweet spot combos
sweet_spot = df[(df['days'] == 5) & 
                (df['miles_per_day'] >= 180) & 
                (df['miles_per_day'] <= 220) &
                (df['receipts_per_day'] < 100)]
ax.scatter(df['miles'], df['reimbursement'], alpha=0.3, s=20, label='All trips')
ax.scatter(sweet_spot['miles'], sweet_spot['reimbursement'], 
           color='gold', alpha=1.0, s=60, marker='*', label='Sweet spot combo')
ax.set_xlabel('Miles Traveled')
ax.set_ylabel('Total Reimbursement ($)')
ax.set_title('Sweet Spot Combinations')
ax.legend()
ax.grid(True, alpha=0.3)

# 4.4 Long trip penalties
ax = axes[1, 1]
long_trips = df[df['days'] >= 8]
short_trips = df[df['days'] < 8]
ax.scatter(short_trips['receipts_per_day'], short_trips['reimb_per_day'], 
           alpha=0.3, s=20, label='< 8 days')
ax.scatter(long_trips['receipts_per_day'], long_trips['reimb_per_day'], 
           color='red', alpha=0.6, s=30, label='≥ 8 days')
ax.set_xlabel('Receipts per Day ($)')
ax.set_ylabel('Reimbursement per Day ($)')
ax.set_title('Long Trip Penalty Analysis')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/04_special_cases.png', dpi=150)
plt.close()

print("\n5. Performing initial linear regression...")

# Simple linear regression as baseline
X_simple = df[['days', 'miles', 'receipts']].values
y = df['reimbursement'].values

# Multiply by 100 to work with cents (integer math)
X_cents = X_simple.copy()
X_cents[:, 2] = X_cents[:, 2] * 100  # Convert receipts to cents
y_cents = y * 100

reg = LinearRegression()
reg.fit(X_cents, y_cents)

# Round coefficients to nearest cent
coef_cents = np.round(reg.coef_).astype(int)
intercept_cents = np.round(reg.intercept_).astype(int)

print(f"\nLinear regression (in cents):")
print(f"Intercept: {intercept_cents} cents")
print(f"Days coefficient: {coef_cents[0]} cents/day")
print(f"Miles coefficient: {coef_cents[1]} cents/mile")
print(f"Receipts coefficient: {coef_cents[2]/100:.2f} (ratio)")

# Calculate predictions and residuals
y_pred_cents = reg.predict(X_cents)
residuals_cents = y_cents - y_pred_cents
residuals_dollars = residuals_cents / 100

print(f"\nLinear model MAE: ${np.mean(np.abs(residuals_dollars)):.2f}")

# Save initial findings
findings = {
    'linear_model': {
        'intercept_cents': int(intercept_cents),
        'days_coef_cents': int(coef_cents[0]),
        'miles_coef_cents': int(coef_cents[1]),
        'receipts_coef_ratio': float(coef_cents[2]/100),
        'mae_dollars': float(np.mean(np.abs(residuals_dollars)))
    },
    'data_insights': {
        'total_cases': len(df),
        'unique_days': sorted(df['days'].unique().tolist()),
        'miles_range': [int(df['miles'].min()), int(df['miles'].max())],
        'receipts_range': [float(df['receipts'].min()), float(df['receipts'].max())],
        'five_day_trips': len(df[df['days'] == 5]),
        'efficiency_range_trips': len(efficiency_bonus),
        'cents_49_99_trips': len(cents_49_99)
    }
}

with open('initial_findings.json', 'w') as f:
    json.dump(findings, f, indent=2)

print("\nAnalysis complete! Check the plots/ directory for visualizations.")
print("Initial findings saved to initial_findings.json")