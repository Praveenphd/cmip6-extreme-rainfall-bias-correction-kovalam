"""
Figure 6: Comparison of model rankings under equal weighting vs.
extreme-focused weighting, with Spearman rank correlation. Supports
Section 6.3.

Input : outputs/model_selection_scores.xlsx (from Script 2)
Output: outputs/figures/fig06_rank_comparison.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from pathlib import Path

# =====================================================
# LOAD DATA
# =====================================================
input_file = "outputs/model_selection_scores.xlsx"
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(input_file, index_col=0)

# =====================================================
# EXTRACT RANKS
# =====================================================
x = df["Rank_equal"]
y = df["Rank_extreme"]

# =====================================================
# COMPUTE SPEARMAN
# =====================================================
rho, pval = spearmanr(x, y)

# =====================================================
# PLOT
# =====================================================
plt.figure(figsize=(6, 6))
plt.scatter(x, y)

min_val = min(x.min(), y.min())
max_val = max(x.max(), y.max())
plt.plot([min_val, max_val], [min_val, max_val])

for model, xi, yi in zip(df.index, x, y):
    if xi <= 7 or yi <= 7:
        short_name = model.split("_")[0]
        plt.annotate(short_name, (xi, yi), xytext=(3, 3),
                     textcoords="offset points", fontsize=8)

plt.text(
    0.05, 0.95,
    f"Spearman rho = {rho:.2f}\np < 0.001",
    transform=plt.gca().transAxes,
    verticalalignment='top'
)

plt.xlabel("Rank (Equal Weighting)")
plt.ylabel("Rank (Extreme-Focused Weighting)")
plt.gca().invert_xaxis()
plt.gca().invert_yaxis()
plt.grid(True)
plt.tight_layout()

plt.savefig(output_folder / "fig06_rank_comparison.png", dpi=300)
plt.show()

print("Figure 6 saved.")
