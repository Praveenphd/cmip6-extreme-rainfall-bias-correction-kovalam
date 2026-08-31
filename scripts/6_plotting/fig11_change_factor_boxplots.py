"""
Figure 11: Distribution of empirical change factors across
stability-screened models, for EM-SSP2-4.5 and EM-SSP5-8.5, by return
period. Supports Section 6.7.

Input : outputs/future_bias_corrected/ssp245/return_level_results.xlsx
        outputs/future_bias_corrected/ssp585/return_level_results.xlsx
        (from Script 8, run once per scenario)
Output: outputs/figures/fig11_change_factor_boxplots.jpg
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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
df_245.columns = df_245.columns.str.strip()
df_585.columns = df_585.columns.str.strip()
df_245 = df_245[["Model", "ReturnPeriod", "Emp_ChangeFactor"]]
df_585 = df_585[["Model", "ReturnPeriod", "Emp_ChangeFactor"]]
df_245["Scenario"] = "SSP245"
df_585["Scenario"] = "SSP585"
df = pd.concat([df_245, df_585])

# =====================================================
# PREPARE DATA
# =====================================================
return_periods = sorted(df["ReturnPeriod"].unique())
data_245, data_585 = [], []
for T in return_periods:
    vals_245 = df[(df["ReturnPeriod"] == T) & (df["Scenario"] == "SSP245")]["Emp_ChangeFactor"].values
    vals_585 = df[(df["ReturnPeriod"] == T) & (df["Scenario"] == "SSP585")]["Emp_ChangeFactor"].values
    data_245.append(vals_245)
    data_585.append(vals_585)

pos_245 = np.arange(len(return_periods)) * 2.0
pos_585 = pos_245 + 0.7

# =====================================================
# PLOT
# =====================================================
plt.figure(figsize=(8, 5))
bp1 = plt.boxplot(data_245, positions=pos_245, widths=0.5, patch_artist=True, showfliers=False)
bp2 = plt.boxplot(data_585, positions=pos_585, widths=0.5, patch_artist=True, showfliers=False)

for box in bp1['boxes']:
    box.set(facecolor='lightblue', edgecolor='black')
for box in bp2['boxes']:
    box.set(facecolor='lightcoral', edgecolor='black')

q1_offset = 0.02
for i in range(len(return_periods)):
    for vals, pos in [(data_245[i], pos_245[i]), (data_585[i], pos_585[i])]:
        median = np.median(vals)
        q1 = np.percentile(vals, 25)
        q3 = np.percentile(vals, 75)
        plt.text(pos, q3, f"{q3:.2f}", fontsize=9, va='bottom')
        plt.text(pos, median, f"{median:.2f}", fontsize=10, va='bottom')
        plt.text(pos, q1 - q1_offset, f"{q1:.2f}", fontsize=9, va='top')

mid_pos = (pos_245 + pos_585) / 2
plt.xticks(mid_pos, return_periods)
plt.xlabel("Return Period (Years)")
plt.ylabel("Change Factor")
plt.grid(axis='y', linestyle='--', alpha=0.4)

plt.plot([], [], color='lightblue', label='EM-SSP2-4.5')
plt.plot([], [], color='lightcoral', label='EM-SSP5-8.5')
plt.legend()
plt.tight_layout()

plt.savefig(output_folder / "fig11_change_factor_boxplots.jpg", dpi=300)
plt.show()

print("Figure 11 saved.")
