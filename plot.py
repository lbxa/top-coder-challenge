import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- Configuration & Styling ---
DATA_FILE = 'public_cases.json'
OUTPUT_DIR = 'plots'
sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100

def load_and_prepare_data(filepath: str) -> pd.DataFrame:
    """Loads and prepares the data from the JSON file."""
    print(f"Loading data from {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Please ensure it's in the same directory.")
        return None

    # Flatten the nested JSON into a DataFrame
    df = pd.json_normalize(data, sep='_')
    df.rename(columns={
        'input_trip_duration_days': 'days',
        'input_miles_traveled': 'miles',
        'input_total_receipts_amount': 'receipts',
        'expected_output': 'reimbursement'
    }, inplace=True)

    print("Data loaded successfully. Engineering features...")
    # --- Feature Engineering ---
    # Avoid division by zero, although days are likely always >= 1
    df['miles_per_day'] = df['miles'] / df['days'].replace(0, 1)
    df['receipts_per_day'] = df['receipts'] / df['days'].replace(0, 1)
    df['receipt_cents'] = (df['receipts'] * 100).astype(int) % 100

    # Define a simple baseline model to calculate residuals for advanced analysis
    # This helps isolate bonuses and penalties.
    # HYPOTHESIS: $100/day + $0.58/mile (simple, non-tiered)
    df['baseline_model'] = (df['days'] * 100) + (df['miles'] * 0.58) + df['receipts']
    df['residual'] = df['reimbursement'] - df['baseline_model']
    
    print("Feature engineering complete.")
    print("DataFrame head:\n", df.head())
    
    # Create output directory if it doesn't exist
    import os
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    return df

def plot_per_diem_analysis(df: pd.DataFrame):
    """
    **REVISED**
    Hypothesis: There's a base per diem around $100/day.
    Method: Filter for trips with low miles AND low receipts using quantiles to ensure
            we have data points. This isolates the per diem effect.
    """
    print("Generating Plot 1: Per Diem Analysis...")
    low_miles_threshold = df['miles'].quantile(0.25)
    low_receipts_threshold = df['receipts'].quantile(0.25)
    
    subset = df[(df['miles'] <= low_miles_threshold) & (df['receipts'] <= low_receipts_threshold)]
    print(f"Found {len(subset)} data points for Per Diem analysis using 25th percentile thresholds.")

    if subset.empty:
        print("Warning: No data points found for Per Diem analysis even with relaxed filters.")
        return

    plt.figure()
    ax = sns.scatterplot(data=subset, x='days', y='reimbursement', label='Actual Reimbursement')
    
    x_range = np.array(ax.get_xlim())
    ax.plot(x_range, x_range * 100, 'r--', label='Hypothesized $100/day Per Diem')
    
    ax.set_title('Per Diem Analysis (for low-activity trips)', fontsize=16, pad=20)
    ax.set_xlabel('Trip Duration (days)', fontsize=12)
    ax.set_ylabel('Total Reimbursement ($)', fontsize=12)
    ax.legend()
    plt.savefig(f'{OUTPUT_DIR}/01_per_diem_analysis.png')
    plt.close()

def plot_mileage_tier_analysis(df: pd.DataFrame):
    """
    **REVISED**
    Hypothesis: Mileage reimbursement is tiered, dropping after ~100 miles.
    Method: Filter for trips with low receipts using quantiles, then estimate the
            mileage pay by subtracting the hypothesized per diem.
    """
    print("Generating Plot 2: Mileage Tier Analysis...")
    low_receipts_threshold = df['receipts'].quantile(0.25)
    subset = df[df['receipts'] <= low_receipts_threshold].copy()
    print(f"Found {len(subset)} initial data points for Mileage analysis using 25th percentile threshold.")
    
    subset['estimated_mileage_pay'] = subset['reimbursement'] - (subset['days'] * 100)
    subset = subset[subset['estimated_mileage_pay'] > 0] # Filter out non-positive values
    print(f"Found {len(subset)} data points after estimating mileage pay.")
    
    if subset.empty:
        print("Warning: No data points found for Mileage analysis after filtering.")
        return

    plt.figure()
    ax = sns.scatterplot(data=subset, x='miles', y='estimated_mileage_pay', alpha=0.7)
    ax.axvline(100, color='r', linestyle='--', label='Hypothesized Tier Change (100 miles)')

    ax.set_title('Mileage Reimbursement Tiers (for low-receipt trips)', fontsize=16, pad=20)
    ax.set_xlabel('Miles Traveled', fontsize=12)
    ax.set_ylabel('Estimated Mileage Reimbursement ($)', fontsize=12)
    ax.legend()
    plt.savefig(f'{OUTPUT_DIR}/02_mileage_tier_analysis.png')
    plt.close()

def plot_efficiency_bonus_analysis(df: pd.DataFrame):
    """
    Hypothesis: There's a bonus for a "sweet spot" of miles/day (180-220).
    Method: Plot the model residual against miles/day to find a "hump".
    """
    print("Generating Plot 3: Efficiency 'Hustle' Bonus Analysis...")
    plt.figure()
    ax = sns.scatterplot(data=df, x='miles_per_day', y='residual', alpha=0.5)
    
    ax.axvspan(180, 220, color='gold', alpha=0.3, label='Hypothesized "Sweet Spot" (180-220 miles/day)')
    
    ax.set_title('Residuals vs. Daily Efficiency (Miles/Day)', fontsize=16, pad=20)
    ax.set_xlabel('Miles per Day', fontsize=12)
    ax.set_ylabel('Residual Error ($) (Actual - Baseline Model)', fontsize=12)
    ax.set_xlim(0, 500) # Zoom in on the relevant range
    ax.legend()
    plt.savefig(f'{OUTPUT_DIR}/03_efficiency_bonus_analysis.png')
    plt.close()

def plot_5_day_bonus_analysis(df: pd.DataFrame):
    """
    Hypothesis: There's a specific, consistent bonus for 5-day trips.
    Method: Use a box plot to compare residuals across trip durations.
    """
    print("Generating Plot 4: 5-Day Trip Bonus Analysis...")
    plt.figure()
    common_durations = df['days'].value_counts().nlargest(10).index
    subset = df[df['days'].isin(common_durations)]

    ax = sns.boxplot(data=subset, x='days', y='residual', order=sorted(common_durations))
    
    ax.set_title('Residual Analysis by Trip Duration', fontsize=16, pad=20)
    ax.set_xlabel('Trip Duration (days)', fontsize=12)
    ax.set_ylabel('Residual Error ($) (Actual - Baseline Model)', fontsize=12)
    ax.axhline(0, color='r', linestyle='--')
    plt.savefig(f'{OUTPUT_DIR}/04_5_day_bonus_analysis.png')
    plt.close()
    
def plot_receipt_penalty_analysis(df: pd.DataFrame):
    """
    Hypothesis: Receipt handling varies by trip length.
    Method: Faceted plot of reimbursement vs. receipts/day, categorized by trip length.
    """
    print("Generating Plot 5: Receipt Penalty/Bonus Analysis by Trip Length...")
    def trip_length_category(days):
        if days <= 3: return 'Short (<=3 days)'
        if 4 <= days <= 7: return 'Medium (4-7 days)'
        return 'Long (>=8 days)'
    df['trip_length_cat'] = df['days'].apply(trip_length_category)

    g = sns.relplot(
        data=df, x='receipts_per_day', y='residual',
        col='trip_length_cat', col_order=['Short (<=3 days)', 'Medium (4-7 days)', 'Long (>=8 days)'],
        kind='scatter', alpha=0.4, height=6, aspect=1.2
    )
    g.fig.suptitle('Receipt Impact on Residuals by Trip Length', fontsize=18, y=1.03)
    g.set_axis_labels('Receipts per Day ($)', 'Residual Error ($)')
    g.set_titles(col_template="{col_name}")
    g.set(xlim=(-10, 200)) # Start x-axis below 0 to see points at 0
    plt.savefig(f'{OUTPUT_DIR}/05_receipt_penalty_analysis.png')
    plt.close()

def plot_cents_bug_analysis(df: pd.DataFrame):
    """
    Hypothesis: A bonus is applied if receipts end in .49 or .99.
    Method: Compare residuals for "bugged" vs. normal receipt cent values.
    """
    print("Generating Plot 6: Cents Bug Analysis...")
    df['cents_bug_cat'] = df['receipt_cents'].apply(lambda c: 'Bugged (49 or 99)' if c in [49, 99] else 'Normal')
    
    plt.figure()
    ax = sns.boxplot(data=df, x='cents_bug_cat', y='residual')
    
    ax.set_title('Residual Analysis for "Cents Bug"', fontsize=16, pad=20)
    ax.set_xlabel('Receipt Cents Category', fontsize=12)
    ax.set_ylabel('Residual Error ($) (Actual - Baseline Model)', fontsize=12)
    ax.axhline(0, color='r', linestyle='--')
    plt.savefig(f'{OUTPUT_DIR}/06_cents_bug_analysis.png')
    plt.close()


def main():
    """Main function to run the EDA plotting script."""
    df = load_and_prepare_data(DATA_FILE)
    if df is None:
        return

    plot_per_diem_analysis(df)
    plot_mileage_tier_analysis(df)
    plot_efficiency_bonus_analysis(df)
    plot_5_day_bonus_analysis(df)
    plot_receipt_penalty_analysis(df)
    plot_cents_bug_analysis(df)

    print(f"\nAll plots have been generated and saved in the '{OUTPUT_DIR}/' directory.")

if __name__ == '__main__':
    main()