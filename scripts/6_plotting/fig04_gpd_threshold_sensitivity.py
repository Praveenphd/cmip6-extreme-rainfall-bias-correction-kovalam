"""
Figure 4a/4b: Sensitivity of GPD shape and scale parameters to
threshold selection. Supports Section 6.1.

Uses precomputed values from outputs/threshold_stability.xlsx
(Script 5), for three representative models, at P95.

Input : outputs/threshold_stability.xlsx (from Script 5)
Output: outputs/figures/fig04a_gpd_shape_sensitivity.jpg
        outputs/figures/fig04b_gpd_scale_sensitivity.jpg
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

# =====================================================
# FONT SETTINGS
# =====================================================
label_font = 14
tick_font = 12
legend_font = 12
title_font = 14

# =====================================================
# FIG 4a: SHAPE PARAMETER
# =====================================================
data_shape = {
    "Percentile": [90, 92, 94, 95, 96, 97, 98],
    "Obs_shape": [0.18075573, 0.154443697, 0.205375296, 0.245852155,
                  0.223637323, 0.34062672, 0.191799999],
    "GCM_shape": [1.006938175, 0.945704948, 0.802337203, 0.680240294,
                  0.602142905, 0.308381916, -0.167235139]
}
df_shape = pd.DataFrame(data_shape)

plt.figure(figsize=(8, 5))
plt.plot(df_shape["Percentile"], df_shape["Obs_shape"], marker='o', label="Observed")
plt.plot(df_shape["Percentile"], df_shape["GCM_shape"], marker='o', label="GCM")
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
data_scale = {
    "Percentile": [90, 92, 94, 95, 96, 97, 98],
    "Obs_scale": [24.43720355, 26.66406732, 25.35458335, 24.40546763,
                  26.78954516, 23.44733298, 33.85811553],
    "GCM_scale": [5.796099609, 7.866432366, 12.39315345, 16.79621792,
                  21.60881785, 36.27197929, 73.41638346]
}
df_scale = pd.DataFrame(data_scale)

plt.figure(figsize=(8, 5))
plt.plot(df_scale["Percentile"], df_scale["Obs_scale"], marker='o',
         linewidth=1.8, label="Observed")
plt.plot(df_scale["Percentile"], df_scale["GCM_scale"], marker='o',
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
