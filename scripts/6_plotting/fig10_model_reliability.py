"""
Figure 10: Model reliability assessment across SSP2-4.5 and SSP5-8.5
scenarios, based on GEV-empirical agreement (50-year) and CI width
ratio (100-year). Supports Section 6.6.

Input : outputs/future_bias_corrected/ssp245/model_stability_screening.xlsx
        outputs/future_bias_corrected/ssp585/model_stability_screening.xlsx
        (from Script 9, run once per scenario)
Output: outputs/figures/fig10_model_reliability.jpg
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

file_245 = "outputs/future_bias_corrected/ssp245/model_stability_screening.xlsx"
file_585 = "outputs/future_bias_corrected/ssp585/model_stability_screening.xlsx"
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD DATA
# =====================================================
df_245 = pd.read_excel(file_245)
df_585 = pd.read_excel(file_585)
df_245["Scenario"] = "SSP245"
df_585["Scenario"] = "SSP585"
df = pd.concat([df_245, df_585], ignore_index=True)

# Remove extreme outlier
df = df[df["GEV_Emp_Diff_50yr"] < 1]

# =====================================================
# UNIQUE MODELS + COLORS
# =====================================================
models = df["Model"].unique()
colors = plt.cm.tab10(range(len(models)))
color_map = dict(zip(models, colors))

# =====================================================
# PLOT
# =====================================================
plt.figure(figsize=(9, 6))
for model in models:
    sub = df[df["Model"] == model]
    for _, row in sub.iterrows():
        marker = "o" if row["Scenario"] == "SSP245" else "s"
        plt.scatter(
            row["GEV_Emp_Diff_50yr"],
            row["CI_Width_Ratio_100yr"],
            color=color_map[model],
            marker=marker,
            s=80
        )

for model in models:
    plt.scatter([], [], color=color_map[model], label=model)

plt.scatter([], [], color='black', marker='o', label='SSP2-4.5')
plt.scatter([], [], color='black', marker='s', label='SSP5-8.5')

plt.xlabel("GEV-Empirical Relative Difference (50-year)")
plt.ylabel("CI Width Ratio (100-year)")
plt.xlim(0, 0.5)
plt.ylim(0, 1.1)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.grid()
plt.tight_layout()

plt.savefig(output_folder / "fig10_model_reliability.jpg", dpi=300)
plt.show()

print("Figure 10 saved.")
