"""
Figure 15a/15b: Projected changes in mean rainfall intensity per wet
day, and high-intensity rainfall day frequency (>=50/100/150 mm).
Supports Section 7.4.

Input : outputs/future_bias_corrected/ssp245/ and .../ssp585/
        (bias-corrected CSVs from Script 7)
Output: outputs/figures/fig15a_intensity_per_wet_day.png
        outputs/figures/fig15b_threshold_exceedance.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

wet_thr = 1.0

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
thresholds = [50, 100, 150]
data_folders = {"SSP245": data_folder_245, "SSP585": data_folder_585}

# =====================================================
# COLLECT DATA
# =====================================================
intensity_results = []
threshold_results = []

for scenario, data_folder in data_folders.items():
    for model in models:
        hist = pd.read_csv(data_folder / f"{model}_Historical_Corrected.csv")
        hist["date"] = pd.to_datetime(hist["date"])
        n_hist_yrs = 60

        wet_hist = hist[hist["BIAS_CORRECTED"] >= wet_thr]["BIAS_CORRECTED"]
        hist_intensity = wet_hist.mean()
        hist_thr_days = {
            thr: (hist["BIAS_CORRECTED"] >= thr).sum() / n_hist_yrs
            for thr in thresholds
        }

        fut = pd.read_csv(data_folder / f"{model}_Future_Corrected.csv")
        fut["date"] = pd.to_datetime(fut["date"])

        for period_label, (start, end) in periods.items():
            period_df = fut[(fut["date"] >= start) & (fut["date"] <= end)]
            n_yrs = (pd.to_datetime(end) - pd.to_datetime(start)).days / 365.25

            wet_fut = period_df[period_df["BIAS_CORRECTED"] >= wet_thr]["BIAS_CORRECTED"]
            fut_intensity = wet_fut.mean()

            intensity_results.append({
                "Model": model, "Scenario": scenario, "Period": period_label,
                "Fut_Intensity": fut_intensity, "Hist_Intensity": hist_intensity
            })

            for thr in thresholds:
                fut_days = (period_df["BIAS_CORRECTED"] >= thr).sum() / n_yrs
                threshold_results.append({
                    "Model": model, "Scenario": scenario, "Period": period_label,
                    "Threshold": thr, "Fut_Days": fut_days, "Hist_Days": hist_thr_days[thr]
                })

df_int = pd.DataFrame(intensity_results)
df_thr = pd.DataFrame(threshold_results)

period_labels = list(periods.keys())
n_periods = len(period_labels)

colors_245 = "#2166ac"
colors_585 = "#d6604d"
model_colors = {
    "BCC-CSM2-MR": "#1b7837", "CanESM5": "#762a83",
    "IPSL-CM6A-LR": "#e08214", "GFDL-ESM4": "#4d4d4d"
}

bar_width = 0.35
x = np.arange(n_periods)

# =====================================================
# FIGURE 15a - Mean Intensity Per Wet Day
# =====================================================
fig, ax = plt.subplots(figsize=(7, 4))
fig.subplots_adjust(right=0.72)

scenario_data_int = {}
for scenario, color, offset in [("SSP245", colors_245, -bar_width / 2), ("SSP585", colors_585, bar_width / 2)]:
    medians, mins, maxs = [], [], []
    for period_label in period_labels:
        vals = df_int[(df_int["Scenario"] == scenario) & (df_int["Period"] == period_label)]["Fut_Intensity"].values
        medians.append(np.median(vals)); mins.append(np.min(vals)); maxs.append(np.max(vals))
    medians, mins, maxs = np.array(medians), np.array(mins), np.array(maxs)
    scenario_data_int[scenario] = {"medians": medians, "mins": mins, "maxs": maxs}

    err_low, err_high = medians - mins, maxs - medians
    ax.bar(x + offset, medians, bar_width, color=color, alpha=0.85)
    ax.errorbar(x + offset, medians, yerr=[err_low, err_high], fmt="none", color="black", capsize=5, linewidth=1.4)

    for pi, period_label in enumerate(period_labels):
        for model in models:
            val = df_int[(df_int["Model"] == model) & (df_int["Scenario"] == scenario) & (df_int["Period"] == period_label)]["Fut_Intensity"].values[0]
            ax.scatter(pi + offset, val, color=model_colors[model], s=70, zorder=5, alpha=0.95)

    for i, val in enumerate(medians):
        ax.text(x[i] + offset, val, f"{val:.1f}", ha="center", va="bottom", fontsize=11,
                fontweight="bold", color=color, zorder=10,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=1.0))

hist_int_median = np.median(df_int["Hist_Intensity"].unique())
ax.axhline(hist_int_median, color="black", linewidth=1.8, linestyle="--")

all_maxs = np.concatenate([scenario_data_int["SSP245"]["maxs"], scenario_data_int["SSP585"]["maxs"]])
all_mins = np.concatenate([scenario_data_int["SSP245"]["mins"], scenario_data_int["SSP585"]["mins"]])
dr = max(all_maxs) - min(all_mins)
ax.set_ylim(min(all_mins) - dr * 0.15, max(all_maxs) + dr * 0.45)

ax.set_xticks(x)
ax.set_xticklabels(["Near-term", "Mid-term", "Long-term"], fontsize=13)
ax.set_ylabel("Intensity (mm/wet-day)", fontsize=13)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.tick_params(labelsize=12)

patch_245 = mpatches.Patch(color=colors_245, alpha=0.85, label="EM-SSP2-4.5")
patch_585 = mpatches.Patch(color=colors_585, alpha=0.85, label="EM-SSP5-8.5")
hist_line = plt.Line2D([0], [0], color="black", linewidth=1.8, linestyle="--",
                        label=f"Historical ({hist_int_median:.1f} mm/wet-day)")
model_patches = [mpatches.Patch(color=model_colors[m], label=m) for m in models]

ax.legend(handles=[patch_245, patch_585, hist_line] + model_patches, fontsize=10,
          loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0, frameon=True)

plt.savefig(output_folder / "fig15a_intensity_per_wet_day.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()
print("Figure 15a saved.")

# =====================================================
# FIGURE 15b - Threshold Exceedance (3 panels)
# =====================================================
thr_titles = {50: "Days per Year >=50 mm", 100: "Days per Year >=100 mm", 150: "Days per Year >=150 mm"}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.subplots_adjust(wspace=0.4, bottom=0.18)

for ax, thr in zip(axes, thresholds):

    scenario_data_thr = {}
    for scenario, color, offset in [("SSP245", colors_245, -bar_width / 2), ("SSP585", colors_585, bar_width / 2)]:
        medians, mins, maxs = [], [], []
        for period_label in period_labels:
            vals = df_thr[(df_thr["Scenario"] == scenario) & (df_thr["Period"] == period_label) & (df_thr["Threshold"] == thr)]["Fut_Days"].values
            medians.append(np.median(vals)); mins.append(np.min(vals)); maxs.append(np.max(vals))
        medians, mins, maxs = np.array(medians), np.array(mins), np.array(maxs)
        scenario_data_thr[scenario] = {"medians": medians, "mins": mins, "maxs": maxs}

        err_low, err_high = medians - mins, maxs - medians
        ax.bar(x + offset, medians, bar_width, color=color, alpha=0.85)
        ax.errorbar(x + offset, medians, yerr=[err_low, err_high], fmt="none", color="black", capsize=5, linewidth=1.4)

        for pi, period_label in enumerate(period_labels):
            for model in models:
                val = df_thr[(df_thr["Model"] == model) & (df_thr["Scenario"] == scenario) & (df_thr["Period"] == period_label) & (df_thr["Threshold"] == thr)]["Fut_Days"].values[0]
                ax.scatter(pi + offset, val, color=model_colors[model], s=70, zorder=5, alpha=0.95)

        for i, val in enumerate(medians):
            ax.text(x[i] + offset, val, f"{val:.2f}", ha="center", va="bottom", fontsize=11,
                    fontweight="bold", color=color, zorder=10,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=1.0))

    hist_val = np.median(df_thr[df_thr["Threshold"] == thr]["Hist_Days"].unique())
    ax.axhline(hist_val, color="black", linewidth=1.8, linestyle="--", label=f"Historical ({hist_val:.2f} days/yr)")

    all_maxs = np.concatenate([scenario_data_thr["SSP245"]["maxs"], scenario_data_thr["SSP585"]["maxs"]])
    all_mins = np.concatenate([scenario_data_thr["SSP245"]["mins"], scenario_data_thr["SSP585"]["mins"]])
    dr = max(all_maxs) - min(all_mins)
    ax.set_ylim(0, max(all_maxs) + dr * 0.5)

    ax.set_title(thr_titles[thr], fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["Near-term", "Mid-term", "Long-term"], fontsize=14)
    ax.set_ylabel("Days per Year", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.tick_params(labelsize=13)
    ax.legend(fontsize=9, loc="upper left")

patch_245 = mpatches.Patch(color=colors_245, alpha=0.85, label="EM-SSP2-4.5")
patch_585 = mpatches.Patch(color=colors_585, alpha=0.85, label="EM-SSP5-8.5")
model_patches = [mpatches.Patch(color=model_colors[m], label=m) for m in models]

fig.legend(handles=[patch_245, patch_585] + model_patches, loc="lower center",
           ncol=6, fontsize=13, frameon=True, bbox_to_anchor=(0.5, -0.02))

plt.savefig(output_folder / "fig15b_threshold_exceedance.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()
print("Figure 15b saved.")
