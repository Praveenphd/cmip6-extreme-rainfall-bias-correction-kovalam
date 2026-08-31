"""
Figure 13: Ensemble projected changes in extreme rainfall indices
(RX1, RX3, RX5, P99, RL10), median and model range, for EM-SSP2-4.5
and EM-SSP5-8.5. Supports Section 7.2.

Input : outputs/future_bias_corrected/ssp245/ and .../ssp585/
        (bias-corrected CSVs from Script 7)
Output: outputs/figures/fig13_ensemble_projections.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    return {"RX1": RX1, "RX3": RX3, "RX5": RX5, "P99": P99, "RL10": RL10}

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
indices = ["RX1", "RX3", "RX5", "P99", "RL10"]

data_folders = {"SSP245": data_folder_245, "SSP585": data_folder_585}

# =====================================================
# COLLECT DATA
# =====================================================
results = []

for scenario, data_folder in data_folders.items():
    for model in models:
        hist = pd.read_csv(data_folder / f"{model}_Historical_Corrected.csv")
        hist["date"] = pd.to_datetime(hist["date"])
        hist_idx = compute_indices(hist["BIAS_CORRECTED"].values, hist["date"])

        fut = pd.read_csv(data_folder / f"{model}_Future_Corrected.csv")
        fut["date"] = pd.to_datetime(fut["date"])

        for period_label, (start, end) in periods.items():
            period_df = fut[(fut["date"] >= start) & (fut["date"] <= end)]
            fut_idx = compute_indices(period_df["BIAS_CORRECTED"].values, period_df["date"])
            for idx in indices:
                pct = 100 * (fut_idx[idx] - hist_idx[idx]) / hist_idx[idx]
                results.append({
                    "Model": model, "Scenario": scenario,
                    "Period": period_label, "Index": idx, "Pct": pct
                })

df = pd.DataFrame(results)

# =====================================================
# PLOT
# =====================================================
period_labels = list(periods.keys())
n_periods = len(period_labels)

colors_245 = "#2166ac"
colors_585 = "#d6604d"
bar_width = 0.35
x = np.arange(n_periods)

fig, axes = plt.subplots(2, 3, figsize=(24, 16), sharey=False)
fig.subplots_adjust(wspace=0.4, hspace=0.25)

axes_flat = axes.flatten()
axes_flat[5].set_visible(False)

for ax, idx in zip(axes_flat[:5], indices):

    scenario_data = {}
    for scenario, color, offset in [("SSP245", colors_245, -bar_width / 2),
                                     ("SSP585", colors_585, bar_width / 2)]:
        medians, mins, maxs = [], [], []
        for period_label in period_labels:
            vals = df[(df["Scenario"] == scenario) & (df["Period"] == period_label) &
                      (df["Index"] == idx)]["Pct"].values
            medians.append(np.median(vals))
            mins.append(np.min(vals))
            maxs.append(np.max(vals))

        scenario_data[scenario] = {
            "medians": np.array(medians), "mins": np.array(mins),
            "maxs": np.array(maxs), "color": color, "offset": offset
        }

    all_maxs = np.concatenate([scenario_data["SSP245"]["maxs"], scenario_data["SSP585"]["maxs"]])
    all_mins = np.concatenate([scenario_data["SSP245"]["mins"], scenario_data["SSP585"]["mins"]])
    data_range = max(all_maxs) - min(all_mins)
    ax.set_ylim(min(all_mins) - data_range * 0.15, max(all_maxs) + data_range * 0.45)

    for scenario, d in scenario_data.items():
        medians, mins, maxs, color, offset = d["medians"], d["mins"], d["maxs"], d["color"], d["offset"]
        err_low = medians - mins
        err_high = maxs - medians

        ax.bar(x + offset, medians, bar_width, color=color, alpha=0.85)
        ax.errorbar(x + offset, medians, yerr=[err_low, err_high],
                    fmt="none", color="black", capsize=4, linewidth=1.2)

        for i, val in enumerate(medians):
            ax.text(x[i] + offset, val, f"{val:+.1f}%", ha="center",
                    va="bottom" if val >= 0 else "top", fontsize=14,
                    fontweight="bold", color=color, zorder=10,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              edgecolor="none", alpha=1.0))

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title(idx, fontsize=18, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["Near-term", "Mid-term", "Long-term"], fontsize=14)
    ax.set_ylabel("Change from Baseline (%)", fontsize=16)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.tick_params(labelsize=16)

patch_245 = mpatches.Patch(color=colors_245, alpha=0.85, label="EM-SSP2-4.5")
patch_585 = mpatches.Patch(color=colors_585, alpha=0.85, label="EM-SSP5-8.5")
fig.legend(handles=[patch_245, patch_585], loc="lower right",
           bbox_to_anchor=(0.75, 0.15), fontsize=16, frameon=True)

plt.savefig(output_folder / "fig13_ensemble_projections.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

print("Figure 13 saved.")
