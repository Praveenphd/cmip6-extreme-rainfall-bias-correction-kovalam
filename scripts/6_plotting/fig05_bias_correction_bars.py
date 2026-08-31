"""
Figure 5: Comparison of observed, raw, and bias-corrected extreme
rainfall indices (RX1, RX5, P99) for the top 7 ranked models.
Supports Section 6.2.

Input : outputs/model_selection_scores.xlsx (from Script 2)
Output: outputs/figures/fig05_bias_correction_bars.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =====================================================
# LOAD DATA
# =====================================================
input_file = "outputs/model_selection_scores.xlsx"
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(input_file, index_col=0)

# =====================================================
# SORT & SELECT TOP 7
# =====================================================
df = df.sort_values("Rank_extreme")
top7 = df.head(7).copy()

# =====================================================
# CLEAN MODEL NAMES
# =====================================================
top7["Model"] = [name.split("_pr")[0] for name in top7.index]
models = top7["Model"].values
x = np.arange(len(models))
width = 0.25
indices = ["RX1", "RX5", "P99"]

# =====================================================
# UNIT LABELS PER INDEX (RX1, P99 are daily rates; RX5 is a multi-day sum)
# =====================================================
unit_labels = {
    "RX1": "Rainfall (mm/day)",
    "RX5": "Rainfall (mm)",
    "P99": "Rainfall (mm/day)"
}

# =====================================================
# PLOT
# =====================================================
fig, axes = plt.subplots(1, 3, figsize=(22, 7))

for i, idx in enumerate(indices):
    obs = top7[f"OBS_{idx}"].values
    raw = top7[f"RAW_{idx}"].values
    cor = top7[f"COR_{idx}"].values

    axes[i].bar(x - width, obs, width, label="Observed")
    axes[i].bar(x, raw, width, label="Raw")
    axes[i].bar(x + width, cor, width, label="Corrected")

    axes[i].set_title(idx, fontsize=16)
    axes[i].set_xticks(x)
    axes[i].set_xticklabels(models, rotation=90, ha='right', fontsize=14)
    axes[i].set_ylabel(unit_labels[idx], fontsize=16)
    axes[i].tick_params(axis='y', labelsize=14)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=3, fontsize=14)

plt.subplots_adjust(top=0.82, bottom=0.2, wspace=0.3)
plt.savefig(output_folder / "fig05_bias_correction_bars.png", dpi=600, bbox_inches='tight')
plt.show()

print("Figure 5 saved.")
