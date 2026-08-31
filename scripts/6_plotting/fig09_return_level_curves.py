"""
Figure 9: Return level curves under Historical, SSP2-4.5, and SSP5-8.5
scenarios for three representative models. Supports Section 6.5.

Input : outputs/future_bias_corrected/ssp245/return_level_results.xlsx
        outputs/future_bias_corrected/ssp585/return_level_results.xlsx
        (from Script 8, run once per scenario)
Output: outputs/figures/fig09_return_level_curves.jpg
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

file_245 = "outputs/future_bias_corrected/ssp245/return_level_results.xlsx"
file_585 = "outputs/future_bias_corrected/ssp585/return_level_results.xlsx"
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD DATA
# =====================================================
df_245 = pd.read_excel(file_245)
df_585 = pd.read_excel(file_585)

# =====================================================
# MODEL COLORS (fixed per model)
# =====================================================
model_colors = {
    "BCC-CSM2-MR": "blue",
    "CanESM5": "green",
    "IPSL-CM6A-LR": "red"
}

# =====================================================
# PLOT
# =====================================================
plt.figure(figsize=(10, 6))
for model, color in model_colors.items():
    df_m245 = df_245[df_245["Model"] == model].sort_values("ReturnPeriod")
    df_m585 = df_585[df_585["Model"] == model].sort_values("ReturnPeriod")

    plt.plot(
        df_m245["ReturnPeriod"], df_m245["GEV_Hist"],
        linestyle=':', marker='o', color=color, label=f"{model} Historical"
    )
    plt.plot(
        df_m245["ReturnPeriod"], df_m245["GEV_Future"],
        linestyle='-', marker='o', color=color, label=f"{model} SSP2-4.5"
    )
    plt.plot(
        df_m585["ReturnPeriod"], df_m585["GEV_Future"],
        linestyle='--', marker='o', color=color, label=f"{model} SSP5-8.5"
    )

plt.xlabel("Return Period (years)")
plt.ylabel("Return Level (mm/day)")
plt.legend(ncol=2)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

plt.savefig(output_folder / "fig09_return_level_curves.jpg", dpi=300)
plt.show()

print("Figure 9 saved.")
