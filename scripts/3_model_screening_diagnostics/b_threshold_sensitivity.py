"""
GPD threshold sensitivity analysis for extreme value modelling.

Fits the Generalized Pareto Distribution shape and scale parameters
across a range of percentile thresholds (P90-P98) for observed (IMD)
and modelled (GCM) rainfall, using three representative models.
Supports the selection of the P95 threshold used throughout the bias
correction pipeline, and Figures 4a (shape) and 4b (scale).

Input : data/imd/ (IMD gridded rainfall CSV)
        data/gcm_csv/ (raw GCM CSVs from Script 1)
Output: outputs/threshold_stability.xlsx
"""

import pandas as pd
import numpy as np
from scipy.stats import genpareto
from pathlib import Path

# ==========================================
# USER INPUT
# ==========================================
imd_csv = "data/imd/imd_grid_kovalam.csv"
gcm_folder = Path("data/gcm_csv")
output_file = "outputs/threshold_stability.xlsx"

models = [
    "BCC-CSM2-MR_pr_mm_day_lat12.90_lon79.88.csv",
    "GFDL-CM4_pr_mm_day_lat12.50_lon80.62.csv",
    "IPSL-CM6A-LR_pr_mm_day_lat12.68_lon80.00.csv"
]

train_end = "1984-12-31"
wet_thr = 1.0
percentiles = [90, 92, 94, 95, 96, 97, 98]

# ==========================================
# LOAD IMD (TRAINING)
# ==========================================
imd = pd.read_csv(imd_csv)
imd["date"] = pd.to_datetime(imd["Date"], format="%m/%d/%Y")
imd = imd[imd["date"] <= train_end]
imd = imd[imd["Rainfall"] >= wet_thr]

# ==========================================
# LOOP THROUGH MODELS
# ==========================================
all_results = []
for model_file in models:
    print(f"\nProcessing {model_file}")
    gcm = pd.read_csv(gcm_folder / model_file)
    gcm["date"] = pd.to_datetime(gcm["time"]).dt.floor("D")
    gcm = gcm[gcm["date"] <= train_end]

    df = pd.merge(
        imd[["date", "Rainfall"]],
        gcm[["date", "gcm_pr_mm_day"]],
        on="date",
        how="inner"
    )

    obs = df["Rainfall"].values
    raw = df["gcm_pr_mm_day"].values

    for p in percentiles:
        thr_obs = np.percentile(obs, p)
        thr_gcm = np.percentile(raw, p)

        obs_excess = obs[obs >= thr_obs] - thr_obs
        gcm_excess = raw[raw >= thr_gcm] - thr_gcm

        row = {
            "Model": model_file.replace(".csv", ""),
            "Percentile": p,
            "Obs_excess_n": len(obs_excess),
            "GCM_excess_n": len(gcm_excess),
            "Obs_shape": np.nan,
            "GCM_shape": np.nan,
            "Obs_scale": np.nan,
            "GCM_scale": np.nan
        }

        if len(obs_excess) > 30:
            shape_o, _, scale_o = genpareto.fit(obs_excess, floc=0)
            row["Obs_shape"] = shape_o
            row["Obs_scale"] = scale_o

        if len(gcm_excess) > 30:
            shape_g, _, scale_g = genpareto.fit(gcm_excess, floc=0)
            row["GCM_shape"] = shape_g
            row["GCM_scale"] = scale_g

        all_results.append(row)

df_results = pd.DataFrame(all_results)
Path("outputs").mkdir(exist_ok=True)
df_results.to_excel(output_file, index=False)

print("\nSaved as", output_file)
