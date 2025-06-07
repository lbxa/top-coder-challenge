#!/usr/bin/env python3
"""
Deep analysis of reimbursement patterns with visualizations
"""

import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Convert to arrays for analysis
data = []
for i, case in enumerate(cases):
    inp = case['input']
    out = case['expected_output']
    
    # Calculate derived features
    miles_per_day = inp['miles_traveled'] / inp['trip_duration_days']
    receipts_per_day = inp['total_receipts_amount'] / inp['trip_duration_days']
    reimbursement_per_day = out / inp['trip_duration_days']
    
    # Check for cents bug
    cents = round((inp['total_receipts_amount'] * 100) % 100)
    has_cents_bug = 1 if cents in [49, 99] else 0
    
    data.append({
        'case_id': i,
        'trip_duration_days': inp['trip_duration_days'],
        'miles_traveled': inp['miles_traveled'],
        'total_receipts_amount': inp['total_receipts_amount'],
        'reimbursement': out,
        'miles_per_day': miles_per_day,
        'receipts_per_day': receipts_per_day,
        'reimbursement_per_day': reimbursement_per_day,
        'has_cents_bug': has_cents_bug,
        'receipt_ratio': out / inp['total_receipts_amount'] if inp['total_receipts_amount'] > 0 else 0
    })

# Perform clustering
features = ['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 
           'miles_per_day', 'receipts_per_day']
X = np.array([[d[f] for f in features] for d in data])

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-means clustering with 6 clusters (as Kevin discovered)
kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# Add cluster labels to data
for i, d in enumerate(data):
    d['cluster'] = clusters[i]

# Create comprehensive visualizations
fig = plt.figure(figsize=(20, 15))
colors = plt.cm.Set3(np.linspace(0, 1, 6))

# 1. 3D visualization of key dimensions
ax1 = fig.add_subplot(2, 3, 1, projection='3d')
for cluster in range(6):
    cluster_data = [d for d in data if d['cluster'] == cluster]
    ax1.scatter([d['miles_per_day'] for d in cluster_data],
               [d['receipts_per_day'] for d in cluster_data],
               [d['reimbursement_per_day'] for d in cluster_data],
               c=[colors[cluster]], label=f'Cluster {cluster}', alpha=0.6, s=50)
ax1.set_xlabel('Miles per Day')
ax1.set_ylabel('Receipts per Day ($)')
ax1.set_zlabel('Reimbursement per Day ($)')
ax1.set_title('3D Cluster Visualization: Efficiency Metrics')
ax1.legend(bbox_to_anchor=(1.1, 1))

# 2. PCA visualization
ax2 = fig.add_subplot(2, 3, 2)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
for cluster in range(6):
    cluster_mask = clusters == cluster
    ax2.scatter(X_pca[cluster_mask, 0], X_pca[cluster_mask, 1], 
               c=[colors[cluster]], label=f'Cluster {cluster}', alpha=0.6)
ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
ax2.set_title('PCA Projection of Clusters')
ax2.legend()

# 3. Cluster size and average reimbursement
ax3 = fig.add_subplot(2, 3, 3)
cluster_stats = {}
for cluster in range(6):
    cluster_data = [d for d in data if d['cluster'] == cluster]
    cluster_stats[cluster] = {
        'count': len(cluster_data),
        'avg_reimbursement': np.mean([d['reimbursement'] for d in cluster_data])
    }

counts = [cluster_stats[c]['count'] for c in range(6)]
avg_reimbs = [cluster_stats[c]['avg_reimbursement'] for c in range(6)]
bubble_sizes = [c * 5 for c in counts]

scatter = ax3.scatter(range(6), avg_reimbs, s=bubble_sizes, 
                     c=colors, alpha=0.6, edgecolors='black')
ax3.set_xlabel('Cluster ID')
ax3.set_ylabel('Average Reimbursement ($)')
ax3.set_title('Cluster Size and Average Reimbursement')
ax3.set_xticks(range(6))

for cluster in range(6):
    ax3.annotate(f"n={counts[cluster]}", 
                (cluster, avg_reimbs[cluster]),
                xytext=(5, 5), textcoords='offset points')

# 4. Efficiency distribution by cluster
ax4 = fig.add_subplot(2, 3, 4)
efficiency_data = []
for cluster in range(6):
    cluster_data = [d['miles_per_day'] for d in data if d['cluster'] == cluster]
    efficiency_data.append(cluster_data)

bp = ax4.boxplot(efficiency_data, labels=[f'C{i}' for i in range(6)], patch_artist=True)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
ax4.set_xlabel('Cluster')
ax4.set_ylabel('Miles per Day')
ax4.set_title('Efficiency Distribution by Cluster')
ax4.axhline(y=180, color='green', linestyle='--', alpha=0.5, label='Sweet spot start')
ax4.axhline(y=220, color='green', linestyle='--', alpha=0.5, label='Sweet spot end')
ax4.legend()

# 5. Receipt spending patterns by cluster
ax5 = fig.add_subplot(2, 3, 5)
spending_data = []
for cluster in range(6):
    cluster_data = [d['receipts_per_day'] for d in data if d['cluster'] == cluster]
    spending_data.append(cluster_data)

bp = ax5.boxplot(spending_data, labels=[f'C{i}' for i in range(6)], patch_artist=True)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
ax5.set_xlabel('Cluster')
ax5.set_ylabel('Receipts per Day ($)')
ax5.set_title('Daily Spending Distribution by Cluster')
ax5.axhline(y=75, color='red', linestyle='--', alpha=0.5, label='Short trip optimal')
ax5.axhline(y=120, color='orange', linestyle='--', alpha=0.5, label='Medium trip max')
ax5.legend()

# 6. Trip duration distribution by cluster
ax6 = fig.add_subplot(2, 3, 6)
duration_counts = {}
for cluster in range(6):
    duration_counts[cluster] = {}
    cluster_data = [d for d in data if d['cluster'] == cluster]
    for d in cluster_data:
        dur = d['trip_duration_days']
        duration_counts[cluster][dur] = duration_counts[cluster].get(dur, 0) + 1

# Create stacked bar chart
bottom = np.zeros(6)
for duration in range(1, 15):
    values = []
    for cluster in range(6):
        total = sum(duration_counts[cluster].values())
        count = duration_counts[cluster].get(duration, 0)
        values.append(count / total * 100 if total > 0 else 0)
    
    if sum(values) > 0:
        ax6.bar(range(6), values, bottom=bottom, label=f'{duration} days', alpha=0.8)
        bottom += values

ax6.set_xlabel('Cluster')
ax6.set_ylabel('Percentage of Trips')
ax6.set_title('Trip Duration Distribution by Cluster')
ax6.set_xticks(range(6))
ax6.set_xticklabels([f'C{i}' for i in range(6)])
ax6.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig('cluster_analysis.png', dpi=150, bbox_inches='tight')
plt.close()  # Close instead of show to avoid GUI

# Print cluster characteristics
print("=== CLUSTER CHARACTERISTICS ===")
for cluster in range(6):
    cluster_data = [d for d in data if d['cluster'] == cluster]
    print(f"\nCluster {cluster} (n={len(cluster_data)}):")
    
    # Calculate averages
    avg_days = np.mean([d['trip_duration_days'] for d in cluster_data])
    avg_miles = np.mean([d['miles_traveled'] for d in cluster_data])
    avg_receipts = np.mean([d['total_receipts_amount'] for d in cluster_data])
    avg_reimb = np.mean([d['reimbursement'] for d in cluster_data])
    avg_mpd = np.mean([d['miles_per_day'] for d in cluster_data])
    avg_rpd = np.mean([d['receipts_per_day'] for d in cluster_data])
    
    print(f"  Avg trip duration: {avg_days:.1f} days")
    print(f"  Avg miles: {avg_miles:.0f}")
    print(f"  Avg receipts: ${avg_receipts:.0f}")
    print(f"  Avg reimbursement: ${avg_reimb:.0f}")
    print(f"  Avg miles/day: {avg_mpd:.0f}")
    print(f"  Avg receipts/day: ${avg_rpd:.0f}")
    
    # Check for cents bug prevalence
    cents_bug_count = sum(1 for d in cluster_data if d['has_cents_bug'])
    print(f"  Cents bug cases: {cents_bug_count} ({cents_bug_count/len(cluster_data)*100:.1f}%)")

# Analyze receipt ratios by cluster and receipt range
print("\n=== RECEIPT RATIOS BY CLUSTER AND AMOUNT ===")
receipt_ranges = [(0, 100), (100, 500), (500, 1000), (1000, 2000), (2000, 5000)]
for cluster in range(6):
    cluster_data = [d for d in data if d['cluster'] == cluster]
    print(f"\nCluster {cluster}:")
    for low, high in receipt_ranges:
        range_data = [d for d in cluster_data if low <= d['total_receipts_amount'] < high]
        if range_data:
            avg_ratio = np.mean([d['receipt_ratio'] for d in range_data])
            print(f"  ${low}-${high}: {len(range_data)} cases, avg ratio: {avg_ratio:.3f}")