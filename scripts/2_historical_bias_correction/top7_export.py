"""
Export bias-corrected historical time series for the top-ranked GCMs.

Reads model rankings from Script 2's output, selects the top 7 models
by Rank_extreme, re-applies the hybrid EQM+GPD bias correction (trained
on 1955-1984) to each, and exports both individual model files and a
combined wide-format file.

Input : data/imd/ (IMD gridded rainfall CSV)
        data/gcm_csv/ (raw GCM CSVs from Script 1)
        outputs/model_selection_scores.xlsx (from Script 2)
Output: outputs/top7_bias_corrected/<model>_BiasCorrected.csv (one per model)
        outputs/top7_bias_corrected/Top7_All_BiasCorrected.xlsx
"""

import pandas as pd
import numpy as np
from scipy.stats import genpareto
from pathlib import Path

# =====================================================
# USER INPUT
# =====================================================
imd_csv = "data/imd/imd_grid_kovalam.csv"
gcm_folder = Path("data/gcm_csv")
ranking_file = "outputs/model_selection_scores.xlsx"
output_folder = Path("outputs/top7_bias_corrected")

wet_thr = 1.0
train_end = "1984-12-31"

output_folder.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD RANKING & SELECT TOP 7
# =====================================================
rank_df = pd.read_excel(ranking_file, index_col=0)
top7_models = rank_df.sort_values("Rank_extreme").head(7).index.tolist()

print("\nTop 7 Models:")
for m in top7_models:
    print(m)

# =====================================================
# LOAD IMD
# =====================================================
imd = pd.read_csv(imd_csv)
imd["date"] = pd.to_datetime(imd["Date"], format="%m/%d/%Y")
imd = imd[["date", "Rainfall"]].rename(columns={"Rainfall": "IMD"})
imd = imd.sort_values("date").reset_index(drop=True)

# =====================================================
# HYBRID BIAS CORRECTION FUNCTION
# =====================================================
def hybrid_bias_correction(obs_train, gcm_train, gcm_full):

    P_obs = np.mean(obs_train >= wet_thr)
    P_gcm = np.mean(gcm_train >= wet_thr)

    gcm_adj = gcm_full.copy()
    diff = P_gcm - P_obs
    adjust_count = int(abs(diff) * len(gcm_adj))

    if diff > 0:
        wet_idx = np.where(gcm_adj >= wet_thr)[0]
        sorted_idx = wet_idx[np.argsort(gcm_adj[wet_idx])]
        gcm_adj[sorted_idx[:adjust_count]] = 0.0
    elif diff < 0:
        dry_idx = np.where(gcm_adj < wet_thr)[0]
        sorted_idx = dry_idx[np.argsort(-gcm_adj[dry_idx])]
        gcm_adj[sorted_idx[:adjust_count]] = wet_thr

    obs_wet = obs_train[obs_train >= wet_thr]
    p95 = np.percentile(obs_wet, 95)

    corrected = gcm_adj.copy()
    bulk_mask = gcm_adj < p95
    tail_mask = gcm_adj >= p95

    # ----- Bulk EQM -----
    gcm_bulk_train = gcm_train[gcm_train < p95]
    obs_bulk_train = obs_train[obs_train < p95]

    if len(gcm_bulk_train) > 40 and len(obs_bulk_train) > 40:

        gcm_sorted = np.sort(gcm_bulk_train)
        obs_sorted = np.sort(obs_bulk_train)

        q_gcm = np.linspace(0, 1, len(gcm_sorted))
        q_obs = np.linspace(0, 1, len(obs_sorted))

        def eqm_map(x):
            q = np.interp(x, gcm_sorted, q_gcm)
            return np.interp(q, q_obs, obs_sorted)

        corrected[bulk_mask] = np.array([eqm_map(x) for x in gcm_adj[bulk_mask]])

    # ----- Tail GPD -----
    obs_excess = obs_train[obs_train >= p95] - p95
    gcm_excess_train = gcm_train[gcm_train >= p95] - p95

    if len(gcm_excess_train) > 50:

        shape_o, _, scale_o = genpareto.fit(obs_excess, floc=0)
        shape_g, _, scale_g = genpareto.fit(gcm_excess_train, floc=0)

        gcm_excess_full = gcm_adj[tail_mask] - p95

        corrected_tail = []
        for x in gcm_excess_full:
            q = genpareto.cdf(x, shape_g, loc=0, scale=scale_g)
            mapped = genpareto.ppf(q, shape_o, loc=0, scale=scale_o)
            corrected_tail.append(mapped + p95)

        corrected[tail_mask] = corrected_tail

    return corrected


# =====================================================
# PROCESS TOP 7 MODELS
# =====================================================
combined_df = None

for model_name in top7_models:

    print("\nProcessing:", model_name)

    file_list = list(gcm_folder.glob(f"{model_name}.csv"))
    if not file_list:
        print("File not found for:", model_name)
        continue

    gcm = pd.read_csv(file_list[0])
    gcm["date"] = pd.to_datetime(gcm["time"]).dt.floor("D")
    gcm = gcm[["date", "gcm_pr_mm_day"]].rename(columns={"gcm_pr_mm_day": "GCM"})
    gcm = gcm.sort_values("date").reset_index(drop=True)

    df_merge = pd.merge(imd, gcm, on="date", how="inner")

    obs = df_merge["IMD"].values
    raw = df_merge["GCM"].values
    dates = df_merge["date"]

    train_mask = df_merge["date"] <= train_end
    obs_train = obs[train_mask]
    gcm_train = raw[train_mask]

    corrected = hybrid_bias_correction(obs_train, gcm_train, raw)

    model_df = pd.DataFrame({
        "date": dates,
        "IMD": obs,
        "RAW_GCM": raw,
        "BIAS_CORRECTED": corrected
    })

    model_df.to_csv(output_folder / f"{model_name}_BiasCorrected.csv", index=False)

    model_corrected = pd.DataFrame({
        "date": dates,
        model_name: corrected
    })

    if combined_df is None:
        combined_df = model_corrected
    else:
        combined_df = pd.merge(combined_df, model_corrected, on="date", how="outer")

combined_df = combined_df.sort_values("date").reset_index(drop=True)
combined_df.to_excel(output_folder / "Top7_All_BiasCorrected.xlsx", index=False)

print("\nAll Top 7 bias-corrected time series exported successfully.")
