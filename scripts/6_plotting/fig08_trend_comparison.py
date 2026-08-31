"""
Figure 8: Comparison of Sen's slope trends between observed and
bias-corrected rainfall (validation period, 1985-2014). Supports
Section 6.4.2.

Input : outputs/trend_consistency_results.xlsx (from Script 4)
Output: outputs/figures/fig08_trend_comparison.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

input_file = "outputs/trend_consistency_results.xlsx"
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD DATA
# =====================================================
df = pd.read_excel(input_file, index_col=0)
df = df.reset_index().rename(columns={
    "model": "Model",
    "Sen_slope_model": "Sen_Slope",
    "p_model": "P_value"
})

# Separate the observed reference row from model rows
observed_slope = df.loc[df["Model"] == "IMD_Observed", "Sen_Slope"].values[0]
df = df[df["Model"] != "IMD_Observed"]

# =====================================================
# GLOBAL STYLE
# =====================================================
plt.rcParams.update({
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12
})

# =====================================================
# SORT DATA
# =====================================================
df = df.sort_values("Sen_Slope")

# =====================================================
# PLOT
# =====================================================
plt.figure(figsize=(10, 6))

colors = ['red' if p < 0.05 else 'gray' for p in df["P_value"]]
plt.barh(df["Model"], df["Sen_Slope"], color=colors)
plt.axvline(observed_slope, linestyle="--", linewidth=1.5, label="Observed trend")

x_text = df["Sen_Slope"].max() + 0.3
for i, p in enumerate(df["P_value"]):
    plt.text(x_text, i, f"p={p:.2f}", va='center', fontsize=11)

plt.xlabel("Sen's Slope (mm/year)")
plt.ylabel("Models")
plt.xlim(df["Sen_Slope"].min() - 0.5, df["Sen_Slope"].max() + 0.8)
plt.legend(frameon=False)
plt.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()

plt.savefig(output_folder / "fig08_trend_comparison.png", dpi=300)
plt.show()

print("Figure 8 saved.")
