"""
Figure 7a/7b: Cumulative distribution functions (CDF) and Q-Q plots
comparing observed, raw, and bias-corrected rainfall for the top 7
models. Supports Section 6.4.1.

Input : outputs/top7_bias_corrected/ (bias-corrected CSVs from Script 3)
Output: outputs/figures/fig07a_cdf_top7.png
        outputs/figures/fig07b_qq_top7.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

folder = Path("outputs/top7_bias_corrected")
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

files = list(folder.glob("*_BiasCorrected.csv"))

# =====================================================
# GLOBAL STYLE
# =====================================================
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 12,
    "axes.titlesize": 12,
    "axes.labelsize": 14,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 12
})

# =====================================================
# FIG 7a: CDF
# =====================================================
def ecdf(data):
    x = np.sort(data)
    y = np.arange(1, len(x) + 1) / len(x)
    return x, y

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, file in enumerate(files[:7]):
    df = pd.read_csv(file)
    obs = df["IMD"].values
    raw = df["RAW_GCM"].values
    cor = df["BIAS_CORRECTED"].values

    x_obs, y_obs = ecdf(obs)
    x_raw, y_raw = ecdf(raw)
    x_cor, y_cor = ecdf(cor)

    ax = axes[i]
    ax.plot(x_obs, y_obs, linewidth=1.8, label="Observed")
    ax.plot(x_raw, y_raw, linestyle='--', linewidth=1.8, label="Raw")
    ax.plot(x_cor, y_cor, linestyle='-', linewidth=1.8, label="Corrected")

    model_name = file.stem.split("_pr")[0]
    ax.set_title(model_name)
    ax.tick_params(axis='both')

fig.delaxes(axes[-1])
fig.text(0.5, 0.04, 'Rainfall (mm/day)', ha='center')
fig.text(0.07, 0.5, 'Cumulative Probability', va='center', rotation='vertical')

handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=3, frameon=False)

plt.tight_layout(rect=[0.08, 0.06, 1, 0.92])
plt.savefig(output_folder / "fig07a_cdf_top7.png", dpi=300)
plt.show()

print("Figure 7a saved.")

# =====================================================
# FIG 7b: Q-Q PLOTS
# =====================================================
def prepare_qq(obs, sim):
    obs_sorted = np.sort(obs)
    sim_sorted = np.sort(sim)
    n = min(len(obs_sorted), len(sim_sorted))
    return obs_sorted[:n], sim_sorted[:n]

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, file in enumerate(files[:7]):
    df = pd.read_csv(file)
    obs = df["IMD"].values
    raw = df["RAW_GCM"].values
    cor = df["BIAS_CORRECTED"].values

    obs_raw, raw_sorted = prepare_qq(obs, raw)
    obs_cor, cor_sorted = prepare_qq(obs, cor)

    ax = axes[i]
    ax.scatter(obs_raw, raw_sorted, label="Raw", s=8)
    ax.scatter(obs_cor, cor_sorted, label="Corrected", s=8)

    max_val = max(obs.max(), cor.max())
    ax.plot([0, max_val], [0, max_val], linestyle='--', linewidth=1.2)

    model_name = file.stem.split("_pr")[0]
    ax.set_title(model_name)
    ax.tick_params(axis='both')

fig.delaxes(axes[-1])
fig.text(0.5, 0.04, 'Observed Rainfall (mm/day)', ha='center')
fig.text(0.03, 0.5, 'Simulated Rainfall (mm/day)', va='center', rotation='vertical')

handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=2, frameon=False)

plt.tight_layout(rect=[0.05, 0.05, 1, 0.92])
plt.savefig(output_folder / "fig07b_qq_top7.png", dpi=300)
plt.show()

print("Figure 7b saved.")
