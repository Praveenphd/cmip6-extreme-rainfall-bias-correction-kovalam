"""
Figure 12: Model-wise projected changes in extreme rainfall indices
relative to historical baseline, for SSP2-4.5 and SSP5-8.5. Supports
Section 7.1.

Input : outputs/future_bias_corrected/ssp245/ and .../ssp585/
        (bias-corrected CSVs from Script 7)
Output: outputs/figures/fig12_modelwise_heatmap.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

wet_thr = 1.0

def compute_indices(series, dates):
    df = pd.DataFrame({"date": dates, "rain": series})
    df["year"] = df["date"].dt.year
    annual_max = df.groupby("year")["rain"].max()
    RX1 = annual_max.mean()
    RX3 = df.groupby("year")["rain"].apply(lambda x: x.rolling(3).sum().max()).mean()
    RX5 = df.groupby("year")["rain"].apply(lambda x: x.rolling(5).sum().max()).mean()
    P99 = np.percentile(series, 99)
    RL10 = np.percentile(annual_max, 90)
    AC1 = pd.Series(series).autocorr(lag=1)

    def max_spell(arr):
        max_len = 0
        current = 0
        for val in arr:
            if val:
                current += 1
                max_len = max(max_len, current)
            else:
                current = 0
        return max_len

    CWD = max_spell(series >= wet_thr)
    CDD = max_spell(series < wet_thr)
    return {"RX1": RX1, "RX3": RX3, "RX5": RX5, "P99": P99,
            "RL10": RL10, "CWD": CWD, "CDD": CDD}

# =====================================================
# USER SETTINGS
# =====================================================
data_folder_245 = Path("outputs/future_bias_corrected/ssp245")
data_folder_585 = Path("outputs/future_bias_corrected/ssp585")
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

periods = {
    "Near-term\n(2021-2040)": ("2021-01-01", "2040-12-31"),
    "Mid-term\n(2041-2060)": ("2041-01-01", "2060-12-31"),
    "Long-term\n(2081-2100)": ("2081-01-01", "2100-12-31")
}

models = ["BCC-CSM2-MR", "CanESM5", "IPSL-CM6A-LR", "GFDL-ESM4"]
indices = ["RX1", "RX3", "RX5", "P99", "RL10", "CWD", "CDD"]

# =====================================================
# BUILD DATA MATRIX
# =====================================================
def build_matrix(data_folder):
    row_labels = []
    data = []
    for model in models:
        hist = pd.read_csv(data_folder / f"{model}_Historical_Corrected.csv")
        hist["date"] = pd.to_datetime(hist["date"])
        hist_idx = compute_indices(hist["BIAS_CORRECTED"].values, hist["date"])

        fut = pd.read_csv(data_folder / f"{model}_Future_Corrected.csv")
        fut["date"] = pd.to_datetime(fut["date"])

        for period_label, (start, end) in periods.items():
            period_df = fut[(fut["date"] >= start) & (fut["date"] <= end)]
            fut_idx = compute_indices(period_df["BIAS_CORRECTED"].values, period_df["date"])
            row = [round(100 * (fut_idx[k] - hist_idx[k]) / hist_idx[k], 1) for k in indices]
            data.append(row)
            row_labels.append(f"{model}\n{period_label}")

    return np.array(data), row_labels

data_245, row_labels = build_matrix(data_folder_245)
data_585, _ = build_matrix(data_folder_585)

# =====================================================
# PLOT
# =====================================================
fig, axes = plt.subplots(1, 2, figsize=(18, 13))
fig.subplots_adjust(wspace=0.35)

scenarios = ["SSP2-4.5", "SSP5-8.5"]
datasets = [data_245, data_585]

cmap = plt.cm.RdBu_r
vmin, vmax = -60, 60
separator_positions = [3, 6, 9]

for ax, data, scenario in zip(axes, datasets, scenarios):
    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")

    ax.set_xticks(np.arange(len(indices)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(indices, fontsize=12, fontweight="bold")
    ax.set_yticklabels(row_labels, fontsize=12)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            color = "white" if abs(val) > 35 else "black"
            ax.text(j, i, f"{val:+.0f}%", ha="center", va="center",
                    fontsize=14, color=color, fontweight="bold")

    for sep in separator_positions:
        ax.axhline(sep - 0.5, color="black", linewidth=2)

    for sep in range(1, len(row_labels)):
        if sep not in separator_positions:
            ax.axhline(sep - 0.5, color="gray", linewidth=0.5, linestyle="--")

    for j in range(len(indices) - 1):
        ax.axvline(j + 0.5, color="gray", linewidth=0.4)

    ax.set_title(scenario, fontsize=14, fontweight="bold", pad=12)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
cb = fig.colorbar(im, cax=cbar_ax)
cb.set_label("Change from Historical Baseline (%)", fontsize=12, labelpad=10)
cb.ax.tick_params(labelsize=12)

plt.savefig(output_folder / "fig12_modelwise_heatmap.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

print("Figure 12 saved.")
