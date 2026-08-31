"""
Figure 14: Projected changes in wet spell (CWD) and dry spell (CDD)
duration, ensemble median with individual model spread. Supports
Section 7.2.

Input : outputs/future_bias_corrected/ssp245/ and .../ssp585/
        (bias-corrected CSVs from Script 7)
Output: outputs/figures/fig14_cwd_cdd_panels.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

wet_thr = 1.0

def compute_indices(series, dates):
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
    return {"CWD": CWD, "CDD": CDD}

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
indices = ["CWD", "CDD"]
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
                    "Model": model, "Scenario": scenario, "Period": period_label,
                    "Index": idx, "Pct": pct, "Abs": fut_idx[idx], "Hist": hist_idx[idx]
                })

df = pd.DataFrame(results)

# =====================================================
# PLOT
# =====================================================
period_labels = list(periods.keys())
n_periods = len(period_labels)

colors_245 = "#2166ac"
colors_585 = "#d6604d"
model_colors = {
    "BCC-CSM2-MR": "#1b7837", "CanESM5": "#762a83",
    "IPSL-CM6A-LR": "#e08214", "GFDL-ESM4": "#4d4d4d"
}

bar_width = 0.25
x = np.arange(n_periods)

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.subplots_adjust(wspace=0.25, hspace=0.25)

for row, idx in enumerate(indices):

    # --- LEFT PANEL: Absolute values ---
    ax_abs = axes[row, 0]
    scenario_data_abs = {}
    for scenario, color, offset in [("SSP245", colors_245, -bar_width), ("SSP585", colors_585, bar_width)]:
        medians, mins, maxs = [], [], []
        for period_label in period_labels:
            vals = df[(df["Scenario"] == scenario) & (df["Period"] == period_label) & (df["Index"] == idx)]["Abs"].values
            medians.append(np.median(vals)); mins.append(np.min(vals)); maxs.append(np.max(vals))
        medians, mins, maxs = np.array(medians), np.array(mins), np.array(maxs)
        scenario_data_abs[scenario] = {"medians": medians, "mins": mins, "maxs": maxs}

        err_low, err_high = medians - mins, maxs - medians
        ax_abs.bar(x + offset, medians, bar_width, color=color, alpha=0.8)
        ax_abs.errorbar(x + offset, medians, yerr=[err_low, err_high], fmt="none", color="black", capsize=4, linewidth=1.2)

        for pi, period_label in enumerate(period_labels):
            for model in models:
                val = df[(df["Model"] == model) & (df["Scenario"] == scenario) & (df["Period"] == period_label) & (df["Index"] == idx)]["Abs"].values[0]
                ax_abs.scatter(pi + offset, val, color=model_colors[model], s=60, zorder=5, alpha=0.9)

        for i, val in enumerate(medians):
            ax_abs.text(x[i] + offset, val, f"{val:.0f}", ha="center", va="bottom", fontsize=10,
                        fontweight="bold", color=color, zorder=10,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=1.0))

    hist_median = np.median([df[(df["Model"] == m) & (df["Index"] == idx)]["Hist"].iloc[0] for m in models])
    ax_abs.axhline(hist_median, color="black", linewidth=1.5, linestyle="--", label=f"Historical median ({hist_median:.0f} days)")

    all_maxs = np.concatenate([scenario_data_abs["SSP245"]["maxs"], scenario_data_abs["SSP585"]["maxs"]])
    all_mins = np.concatenate([scenario_data_abs["SSP245"]["mins"], scenario_data_abs["SSP585"]["mins"]])
    dr = max(all_maxs) - min(all_mins)
    ax_abs.set_ylim(min(all_mins) - dr * 0.2, max(all_maxs) + dr * 0.4)

    ax_abs.set_title(f"{idx} - Absolute Values (days)", fontsize=15, fontweight="bold")
    ax_abs.set_xticks(x)
    ax_abs.set_xticklabels(["Near-term", "Mid-term", "Late-term"], fontsize=13)
    ax_abs.set_ylabel("Days", fontsize=13)
    ax_abs.grid(axis="y", linestyle="--", alpha=0.4)
    ax_abs.tick_params(labelsize=12)
    ax_abs.legend(fontsize=14, loc="upper left")

    # --- RIGHT PANEL: Percentage change ---
    ax_pct = axes[row, 1]
    scenario_data_pct = {}
    for scenario, color, offset in [("SSP245", colors_245, -bar_width), ("SSP585", colors_585, bar_width)]:
        medians, mins, maxs = [], [], []
        for period_label in period_labels:
            vals = df[(df["Scenario"] == scenario) & (df["Period"] == period_label) & (df["Index"] == idx)]["Pct"].values
            medians.append(np.median(vals)); mins.append(np.min(vals)); maxs.append(np.max(vals))
        medians, mins, maxs = np.array(medians), np.array(mins), np.array(maxs)
        scenario_data_pct[scenario] = {"medians": medians, "mins": mins, "maxs": maxs}

        err_low, err_high = medians - mins, maxs - medians
        ax_pct.bar(x + offset, medians, bar_width, color=color, alpha=0.8)
        ax_pct.errorbar(x + offset, medians, yerr=[err_low, err_high], fmt="none", color="black", capsize=4, linewidth=1.2)

        for pi, period_label in enumerate(period_labels):
            for model in models:
                val = df[(df["Model"] == model) & (df["Scenario"] == scenario) & (df["Period"] == period_label) & (df["Index"] == idx)]["Pct"].values[0]
                ax_pct.scatter(pi + offset, val, color=model_colors[model], s=60, zorder=5, alpha=0.9)

        for i, val in enumerate(medians):
            ax_pct.text(x[i] + offset, val, f"{val:+.1f}%", ha="center",
                        va="bottom" if val >= 0 else "top", fontsize=11,
                        fontweight="bold", color=color, zorder=10,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=1.0))

    all_maxs_p = np.concatenate([scenario_data_pct["SSP245"]["maxs"], scenario_data_pct["SSP585"]["maxs"]])
    all_mins_p = np.concatenate([scenario_data_pct["SSP245"]["mins"], scenario_data_pct["SSP585"]["mins"]])
    dr_p = max(all_maxs_p) - min(all_mins_p)
    ax_pct.set_ylim(min(all_mins_p) - dr_p * 0.3, max(all_maxs_p) + dr_p * 0.3)

    ax_pct.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax_pct.set_title(f"{idx} - Change from Baseline (%)", fontsize=15, fontweight="bold")
    ax_pct.set_xticks(x)
    ax_pct.set_xticklabels(["Near-term", "Mid-term", "Late-term"], fontsize=13)
    ax_pct.set_ylabel("Change (%)", fontsize=13)
    ax_pct.grid(axis="y", linestyle="--", alpha=0.4)
    ax_pct.tick_params(labelsize=12)

patch_245 = mpatches.Patch(color=colors_245, alpha=0.85, label="EM-SSP2-4.5")
patch_585 = mpatches.Patch(color=colors_585, alpha=0.85, label="EM-SSP5-8.5")
model_patches = [mpatches.Patch(color=model_colors[m], label=m) for m in models]

fig.legend(handles=[patch_245, patch_585] + model_patches, loc="lower center",
           ncol=6, fontsize=12, frameon=True, bbox_to_anchor=(0.5, 0.04))

plt.savefig(output_folder / "fig14_cwd_cdd_panels.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

print("Figure 14 saved.")
