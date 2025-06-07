#!/usr/bin/env python3
"""
Generate comprehensive plots to analyze reimbursement patterns
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from calculator_v2 import calculate_reimbursement

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Calculate errors for current implementation
errors = []
for case in cases:
    inp = case['input']
    expected = case['expected_output']
    calculated = calculate_reimbursement(
        inp['trip_duration_days'],
        inp['miles_traveled'],
        inp['total_receipts_amount']
    )
    error = calculated - expected
    error_pct = (error / expected * 100) if expected > 0 else 0
    
    errors.append({
        'input': inp,
        'expected': expected,
        'calculated': calculated,
        'error': error,
        'error_pct': error_pct,
        'abs_error': abs(error)
    })

# Create figure with multiple subplots
fig = plt.figure(figsize=(20, 24))

# 1. Error distribution by trip duration
ax1 = plt.subplot(4, 3, 1)
duration_errors = {}
for e in errors:
    d = e['input']['trip_duration_days']
    if d not in duration_errors:
        duration_errors[d] = []
    duration_errors[d].append(e['error'])

durations = sorted(duration_errors.keys())
error_data = [duration_errors[d] for d in durations]
bp1 = ax1.boxplot(error_data, labels=durations, patch_artist=True)
for patch in bp1['boxes']:
    patch.set_facecolor('lightblue')
ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax1.set_xlabel('Trip Duration (days)')
ax1.set_ylabel('Error ($)')
ax1.set_title('Error Distribution by Trip Duration')
ax1.grid(True, alpha=0.3)

# 2. Error vs Receipt Amount
ax2 = plt.subplot(4, 3, 2)
receipts = [e['input']['total_receipts_amount'] for e in errors]
error_vals = [e['error'] for e in errors]
colors = ['red' if e < 0 else 'blue' for e in error_vals]
ax2.scatter(receipts, error_vals, c=colors, alpha=0.5, s=20)
ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax2.set_xlabel('Receipt Amount ($)')
ax2.set_ylabel('Error ($)')
ax2.set_title('Error vs Receipt Amount (Red=Underestimate, Blue=Overestimate)')
ax2.grid(True, alpha=0.3)

# 3. Error vs Miles Traveled
ax3 = plt.subplot(4, 3, 3)
miles = [e['input']['miles_traveled'] for e in errors]
ax3.scatter(miles, error_vals, c=colors, alpha=0.5, s=20)
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax3.set_xlabel('Miles Traveled')
ax3.set_ylabel('Error ($)')
ax3.set_title('Error vs Miles Traveled')
ax3.grid(True, alpha=0.3)

# 4. Receipt Ratio Analysis by Trip Duration
ax4 = plt.subplot(4, 3, 4)
for days in range(1, 15):
    day_cases = [c for c in cases if c['input']['trip_duration_days'] == days]
    if day_cases:
        receipt_amounts = []
        ratios = []
        for c in day_cases:
            if c['input']['total_receipts_amount'] > 0:
                receipt_amounts.append(c['input']['total_receipts_amount'])
                ratios.append(c['expected_output'] / c['input']['total_receipts_amount'])
        if receipt_amounts:
            ax4.scatter(receipt_amounts, ratios, label=f'{days}d', alpha=0.6, s=30)

ax4.set_xlabel('Receipt Amount ($)')
ax4.set_ylabel('Reimbursement / Receipt Ratio')
ax4.set_title('Receipt Ratios by Trip Duration')
ax4.set_xlim(0, 2500)
ax4.set_ylim(0, 10)
ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
ax4.grid(True, alpha=0.3)

# 5. Cents Bug Analysis
ax5 = plt.subplot(4, 3, 5)
cents_bug_errors = []
normal_errors = []
for e in errors:
    cents = round((e['input']['total_receipts_amount'] * 100) % 100)
    if cents in [49, 99]:
        cents_bug_errors.append(e['abs_error'])
    else:
        normal_errors.append(e['abs_error'])

ax5.boxplot([normal_errors, cents_bug_errors], labels=['Normal', 'Cents Bug (.49/.99)'])
ax5.set_ylabel('Absolute Error ($)')
ax5.set_title('Error Comparison: Cents Bug vs Normal')
ax5.grid(True, alpha=0.3)

# 6. Efficiency (Miles per Day) Analysis
ax6 = plt.subplot(4, 3, 6)
mpd_errors = {}
for e in errors:
    mpd = e['input']['miles_traveled'] / e['input']['trip_duration_days']
    bucket = int(mpd // 50) * 50  # 50-mile buckets
    if bucket not in mpd_errors:
        mpd_errors[bucket] = []
    mpd_errors[bucket].append(e['error'])

mpd_buckets = sorted(mpd_errors.keys())
mpd_data = [mpd_errors[b] for b in mpd_buckets]
bp6 = ax6.boxplot(mpd_data, labels=[f'{b}-{b+50}' for b in mpd_buckets], patch_artist=True)
for patch in bp6['boxes']:
    patch.set_facecolor('lightgreen')
ax6.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax6.set_xlabel('Miles per Day')
ax6.set_ylabel('Error ($)')
ax6.set_title('Error by Efficiency (Miles/Day)')
ax6.tick_params(axis='x', rotation=45)
ax6.grid(True, alpha=0.3)

# 7. High Error Cases Analysis
ax7 = plt.subplot(4, 3, 7)
high_errors = sorted(errors, key=lambda x: x['abs_error'], reverse=True)[:50]
days_high = [e['input']['trip_duration_days'] for e in high_errors]
receipts_high = [e['input']['total_receipts_amount'] for e in high_errors]
ax7.scatter(days_high, receipts_high, c='red', s=50, alpha=0.7)
ax7.set_xlabel('Trip Duration (days)')
ax7.set_ylabel('Receipt Amount ($)')
ax7.set_title('Top 50 Highest Error Cases')
ax7.grid(True, alpha=0.3)

# 8. Expected vs Calculated
ax8 = plt.subplot(4, 3, 8)
expected_vals = [e['expected'] for e in errors]
calculated_vals = [e['calculated'] for e in errors]
ax8.scatter(expected_vals, calculated_vals, alpha=0.5, s=10)
ax8.plot([0, 2500], [0, 2500], 'r--', label='Perfect Match')
ax8.set_xlabel('Expected Reimbursement ($)')
ax8.set_ylabel('Calculated Reimbursement ($)')
ax8.set_title('Expected vs Calculated')
ax8.legend()
ax8.grid(True, alpha=0.3)

# 9. Error Percentage by Receipt Range
ax9 = plt.subplot(4, 3, 9)
receipt_ranges = [(0, 100), (100, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 3000)]
range_errors = []
range_labels = []
for low, high in receipt_ranges:
    range_errs = [e['error_pct'] for e in errors 
                  if low <= e['input']['total_receipts_amount'] < high]
    if range_errs:
        range_errors.append(range_errs)
        range_labels.append(f'${low}-${high}')

bp9 = ax9.boxplot(range_errors, labels=range_labels, patch_artist=True)
for patch in bp9['boxes']:
    patch.set_facecolor('lightyellow')
ax9.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax9.set_xlabel('Receipt Range')
ax9.set_ylabel('Error Percentage (%)')
ax9.set_title('Error % by Receipt Range')
ax9.tick_params(axis='x', rotation=45)
ax9.grid(True, alpha=0.3)

# 10. Pattern: 1-day trips
ax10 = plt.subplot(4, 3, 10)
one_day = [e for e in errors if e['input']['trip_duration_days'] == 1]
od_receipts = [e['input']['total_receipts_amount'] for e in one_day]
od_errors = [e['error'] for e in one_day]
ax10.scatter(od_receipts, od_errors, c='purple', alpha=0.6)
ax10.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax10.set_xlabel('Receipt Amount ($)')
ax10.set_ylabel('Error ($)')
ax10.set_title('1-Day Trip Errors')
ax10.grid(True, alpha=0.3)

# 11. Pattern: 5-day trips
ax11 = plt.subplot(4, 3, 11)
five_day = [e for e in errors if e['input']['trip_duration_days'] == 5]
fd_receipts = [e['input']['total_receipts_amount'] for e in five_day]
fd_errors = [e['error'] for e in five_day]
ax11.scatter(fd_receipts, fd_errors, c='orange', alpha=0.6)
ax11.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax11.set_xlabel('Receipt Amount ($)')
ax11.set_ylabel('Error ($)')
ax11.set_title('5-Day Trip Errors (Should have bonus)')
ax11.grid(True, alpha=0.3)

# 12. Pattern: Long trips (12-14 days)
ax12 = plt.subplot(4, 3, 12)
long_trips = [e for e in errors if e['input']['trip_duration_days'] >= 12]
lt_receipts = [e['input']['total_receipts_amount'] for e in long_trips]
lt_errors = [e['error'] for e in long_trips]
ax12.scatter(lt_receipts, lt_errors, c='green', alpha=0.6)
ax12.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax12.set_xlabel('Receipt Amount ($)')
ax12.set_ylabel('Error ($)')
ax12.set_title('Long Trip (12-14d) Errors')
ax12.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('error_analysis_plots.png', dpi=150, bbox_inches='tight')
plt.close()

print("Generated error_analysis_plots.png")

# Generate second set of plots focusing on specific patterns
fig2 = plt.figure(figsize=(20, 16))

# 1. Receipt multiplier patterns
ax1 = plt.subplot(3, 3, 1)
receipt_bins = np.linspace(0, 3000, 31)
multipliers = []
bin_centers = []
for i in range(len(receipt_bins)-1):
    low, high = receipt_bins[i], receipt_bins[i+1]
    bin_cases = [c for c in cases if low <= c['input']['total_receipts_amount'] < high]
    if bin_cases:
        avg_ratio = np.mean([c['expected_output'] / c['input']['total_receipts_amount'] 
                           for c in bin_cases if c['input']['total_receipts_amount'] > 0])
        multipliers.append(avg_ratio)
        bin_centers.append((low + high) / 2)

ax1.plot(bin_centers, multipliers, 'b-', linewidth=2)
ax1.set_xlabel('Receipt Amount ($)')
ax1.set_ylabel('Average Reimbursement/Receipt Ratio')
ax1.set_title('Receipt Multiplier Curve')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 20)

# 2. Miles per day sweet spot analysis
ax2 = plt.subplot(3, 3, 2)
mpd_all = []
reimb_all = []
for c in cases:
    mpd = c['input']['miles_traveled'] / c['input']['trip_duration_days']
    mpd_all.append(mpd)
    reimb_all.append(c['expected_output'])

ax2.scatter(mpd_all, reimb_all, alpha=0.5, s=20)
ax2.axvspan(180, 220, alpha=0.2, color='red', label='Kevin\'s "sweet spot"')
ax2.set_xlabel('Miles per Day')
ax2.set_ylabel('Reimbursement ($)')
ax2.set_title('Reimbursement vs Efficiency')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 1000)

# 3. Trip duration * miles interaction
ax3 = plt.subplot(3, 3, 3)
interactions = []
reimbursements = []
for c in cases:
    interaction = c['input']['trip_duration_days'] * c['input']['miles_traveled']
    interactions.append(interaction)
    reimbursements.append(c['expected_output'])

ax3.scatter(interactions, reimbursements, alpha=0.5, s=20, c='green')
ax3.set_xlabel('Trip Duration × Miles')
ax3.set_ylabel('Reimbursement ($)')
ax3.set_title('Interaction Effect Analysis')
ax3.grid(True, alpha=0.3)

# 4. Cents bug detailed analysis
ax4 = plt.subplot(3, 3, 4)
for receipt_range, color in [((0, 500), 'blue'), ((500, 1000), 'green'), 
                            ((1000, 1500), 'orange'), ((1500, 3000), 'red')]:
    low, high = receipt_range
    normal_reimb = []
    bug_reimb = []
    
    for c in cases:
        if low <= c['input']['total_receipts_amount'] < high:
            cents = round((c['input']['total_receipts_amount'] * 100) % 100)
            if cents in [49, 99]:
                bug_reimb.append(c['expected_output'])
            else:
                normal_reimb.append(c['expected_output'])
    
    if normal_reimb and bug_reimb:
        bars = ax4.bar([f'${low}-${high}\nNormal', f'${low}-${high}\nBug'], 
                       [np.mean(normal_reimb), np.mean(bug_reimb)], 
                       color=[color, color])
        bars[0].set_alpha(0.7)
        bars[1].set_alpha(0.3)

ax4.set_ylabel('Average Reimbursement ($)')
ax4.set_title('Cents Bug Impact by Receipt Range')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)

# 5. Per-day rates by trip duration
ax5 = plt.subplot(3, 3, 5)
per_day_rates = []
durations = []
for d in range(1, 15):
    day_cases = [c for c in cases if c['input']['trip_duration_days'] == d]
    if day_cases:
        avg_rate = np.mean([c['expected_output'] / d for c in day_cases])
        per_day_rates.append(avg_rate)
        durations.append(d)

ax5.plot(durations, per_day_rates, 'bo-', linewidth=2, markersize=8)
ax5.set_xlabel('Trip Duration (days)')
ax5.set_ylabel('Average Per-Day Rate ($)')
ax5.set_title('Per-Day Reimbursement Rates')
ax5.grid(True, alpha=0.3)

# 6. 5-day trip analysis
ax6 = plt.subplot(3, 3, 6)
five_day_cases = [c for c in cases if c['input']['trip_duration_days'] == 5]
other_cases = [c for c in cases if 4 <= c['input']['trip_duration_days'] <= 6 
               and c['input']['trip_duration_days'] != 5]

fd_receipts = [c['input']['total_receipts_amount'] for c in five_day_cases]
fd_reimb = [c['expected_output'] for c in five_day_cases]
other_receipts = [c['input']['total_receipts_amount'] for c in other_cases]
other_reimb = [c['expected_output'] for c in other_cases]

ax6.scatter(fd_receipts, fd_reimb, c='red', label='5-day trips', alpha=0.6, s=30)
ax6.scatter(other_receipts, other_reimb, c='blue', label='4,6-day trips', alpha=0.4, s=20)
ax6.set_xlabel('Receipt Amount ($)')
ax6.set_ylabel('Reimbursement ($)')
ax6.set_title('5-Day Trip Bonus Analysis')
ax6.legend()
ax6.grid(True, alpha=0.3)

# 7. High receipt patterns by duration
ax7 = plt.subplot(3, 3, 7)
high_receipt_cases = [c for c in cases if c['input']['total_receipts_amount'] > 2000]
hr_days = [c['input']['trip_duration_days'] for c in high_receipt_cases]
hr_ratios = [c['expected_output'] / c['input']['total_receipts_amount'] 
             for c in high_receipt_cases]

# Create box plot by duration
duration_ratios = {}
for d, r in zip(hr_days, hr_ratios):
    if d not in duration_ratios:
        duration_ratios[d] = []
    duration_ratios[d].append(r)

sorted_durations = sorted(duration_ratios.keys())
ratio_data = [duration_ratios[d] for d in sorted_durations]
bp7 = ax7.boxplot(ratio_data, labels=sorted_durations, patch_artist=True)
ax7.set_xlabel('Trip Duration (days)')
ax7.set_ylabel('Reimbursement/Receipt Ratio')
ax7.set_title('High Receipt (>$2000) Ratios by Duration')
ax7.grid(True, alpha=0.3)

# 8. Error heatmap by duration and receipt range
ax8 = plt.subplot(3, 3, 8)
duration_range = range(1, 15)
receipt_ranges = [(0, 200), (200, 500), (500, 1000), (1000, 1500), (1500, 3000)]
error_matrix = np.zeros((len(duration_range), len(receipt_ranges)))

for i, d in enumerate(duration_range):
    for j, (low, high) in enumerate(receipt_ranges):
        range_errors = [e['abs_error'] for e in errors 
                       if e['input']['trip_duration_days'] == d 
                       and low <= e['input']['total_receipts_amount'] < high]
        if range_errors:
            error_matrix[i, j] = np.mean(range_errors)

im = ax8.imshow(error_matrix.T, aspect='auto', cmap='hot')
ax8.set_yticks(range(len(receipt_ranges)))
ax8.set_yticklabels([f'${r[0]}-${r[1]}' for r in receipt_ranges])
ax8.set_xticks(range(len(duration_range)))
ax8.set_xticklabels(duration_range)
ax8.set_xlabel('Trip Duration (days)')
ax8.set_ylabel('Receipt Range')
ax8.set_title('Average Error Heatmap')
plt.colorbar(im, ax=ax8)

# 9. Specific problem patterns
ax9 = plt.subplot(3, 3, 9)
# Identify specific problematic patterns
problem_patterns = []
for e in errors:
    if e['abs_error'] > 300:  # High error cases
        pattern = f"{e['input']['trip_duration_days']}d/${int(e['input']['total_receipts_amount']//100)*100}"
        problem_patterns.append(pattern)

from collections import Counter
pattern_counts = Counter(problem_patterns)
top_patterns = pattern_counts.most_common(10)

patterns, counts = zip(*top_patterns) if top_patterns else ([], [])
ax9.barh(patterns, counts)
ax9.set_xlabel('Count')
ax9.set_ylabel('Pattern (Duration/Receipt Range)')
ax9.set_title('Most Common High-Error Patterns')
ax9.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('pattern_analysis_plots.png', dpi=150, bbox_inches='tight')
plt.close()

print("Generated pattern_analysis_plots.png")

# Summary statistics
print("\n=== SUMMARY STATISTICS ===")
print(f"Total cases: {len(cases)}")
print(f"Average error: ${np.mean([e['abs_error'] for e in errors]):.2f}")
print(f"Cases with error > $100: {sum(1 for e in errors if e['abs_error'] > 100)}")
print(f"Cases with error > $500: {sum(1 for e in errors if e['abs_error'] > 500)}")
print(f"\nMost problematic patterns:")
for pattern, count in top_patterns[:5]:
    print(f"  {pattern}: {count} cases")