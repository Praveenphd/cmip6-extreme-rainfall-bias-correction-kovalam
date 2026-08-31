"""
Figure 4a/4b: Sensitivity of GPD shape and scale parameters to
threshold selection. Supports Section 6.1.

Input : outputs/threshold_stability.xlsx (from Script 5)
Output: outputs/figures/fig04a_gpd_shape_sensitivity.jpg
        outputs/figures/fig04b_gpd_scale_sensitivity.jpg
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

input_file = "outputs/threshold_stability.xlsx"
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

label_font = 14
tick_font = 12
legend_font = 12

# =====================================================
# LOAD AND AGGREGATE ACROSS THE THREE REPRESENTATIVE MODELS
# =====================================================
df = pd.read_excel(input_file)

agg = df.groupby("Percentile").agg(
    Obs_shape=("Obs_shape", "mean"),
    GCM_shape=("GCM_shape", "mean"),
    Obs_scale=("Obs_scale", "mean"),
    GCM_scale=("GCM_scale", "mean")
).reset_index()

# =====================================================
# FIG 4a: SHAPE PARAMETER
# =====================================================
plt.figure(figsize=(8, 5))
plt.plot(agg["Percentile"], agg["Obs_shape"], marker='o', label="Observed")
plt.plot(agg["Percentile"], agg["GCM_shape"], marker='o', label="GCM")
plt.axvline(95, linestyle='--', label="Selected threshold (P95)")

plt.xlabel("Percentile Threshold", fontsize=label_font)
plt.ylabel("Shape Parameter", fontsize=label_font)
plt.xticks(fontsize=tick_font)
plt.yticks(fontsize=tick_font)
plt.legend(fontsize=legend_font)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(output_folder / "fig04a_gpd_shape_sensitivity.jpg", dpi=300)
plt.show()

# =====================================================
# FIG 4b: SCALE PARAMETER
# =====================================================
plt.figure(figsize=(8, 5))
plt.plot(agg["Percentile"], agg["Obs_scale"], marker='o',
         linewidth=1.8, label="Observed")
plt.plot(agg["Percentile"], agg["GCM_scale"], marker='o',
         linewidth=1.8, label="GCM")
plt.axvline(95, linestyle='--', linewidth=1.5, label="Selected threshold (P95)")

plt.xlabel("Percentile Threshold", fontsize=label_font)
plt.ylabel("Scale Parameter", fontsize=label_font)
plt.xticks(fontsize=tick_font)
plt.yticks(fontsize=tick_font)
plt.legend(fontsize=legend_font)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(output_folder / "fig04b_gpd_scale_sensitivity.jpg", dpi=300)
plt.show()

print("Figures 4a and 4b saved.")
