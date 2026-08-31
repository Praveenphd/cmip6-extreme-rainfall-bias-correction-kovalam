"""
Hybrid EQM+GPD bias correction for historical CMIP6 precipitation,
with multi-criteria model scoring and ranking.

For each GCM, applies wet-day frequency adjustment, Empirical Quantile
Mapping (EQM) below the P95 threshold, and Generalized Pareto
Distribution (GPD) correction above it. Bias correction functions are
trained on 1955-1984 and validated on 1985-2014. Models are scored and
ranked based on extreme index bias, temporal persistence, and wet/dry
spell characteristics.

Input : data/imd/ (IMD gridded rainfall CSV)
        data/gcm_csv/ (raw GCM CSVs from Script 1)
Output: outputs/model_selection_scores.xlsx
"""

import pandas as pd
import numpy as np
from scipy.stats import genpareto, spearmanr
from pathlib import Path

# =====================================================
# USER INPUT
# =====================================================
imd_csv = "data/imd/imd_grid_kovalam.csv"
gcm_folder = Path("data/gcm_csv")
output_file = "outputs/model_selection_scores.xlsx"

wet_thr = 1.0
start_date = "1955-01-01"
end_date = "2014-12-31"

train_end = "1984-12-31"
val_start = "1985-01-01"
# =====================================================


# =====================================================
# LOAD IMD
# =====================================================
imd = pd.read_csv(imd_csv)
imd["date"] = pd.to_datetime(imd["Date"], format="%m/%d/%Y")
imd = imd[["date", "Rainfall"]].rename(columns={"Rainfall": "IMD"})
imd = imd.sort_values("date")

full_range = pd.date_range(start_date, end_date, freq="D")
imd = imd[imd["date"].isin(full_range)].reset_index(drop=True)


# =====================================================
# HYBRID BIAS CORRECTION (TRAINING ONLY)
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

    # ---- Bulk EQM ----
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

    # ---- Tail GPD ----
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
# METRICS
# =====================================================
def compute_metrics(series, dates):

    df = pd.DataFrame({"date": dates, "rain": series})
    df["year"] = df["date"].dt.year

    annual_max = df.groupby("year")["rain"].max()
    RX1 = annual_max.mean()

    RX3_list, RX5_list = [], []
    for y, group in df.groupby("year"):
        RX3_list.append(group["rain"].rolling(3).sum().max())
        RX5_list.append(group["rain"].rolling(5).sum().max())

    RX3 = np.mean(RX3_list)
    RX5 = np.mean(RX5_list)

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

    return RX1, RX3, RX5, P99, RL10, AC1, CWD, CDD


# =====================================================
# PROCESS MODELS
# =====================================================
results = []

for file in gcm_folder.glob("*.csv"):

    print("Processing:", file.stem)

    gcm = pd.read_csv(file)
    gcm["date"] = pd.to_datetime(gcm["time"]).dt.floor("D")
    gcm = gcm[["date", "gcm_pr_mm_day"]].rename(columns={"gcm_pr_mm_day": "GCM"})
    gcm = gcm[gcm["date"].isin(full_range)].reset_index(drop=True)

    df_merge = pd.merge(imd, gcm, on="date", how="inner")

    obs = df_merge["IMD"].values
    raw = df_merge["GCM"].values
    dates = df_merge["date"]

    train_mask = df_merge["date"] <= train_end
    val_mask = df_merge["date"] >= val_start

    obs_train = obs[train_mask]
    gcm_train = raw[train_mask]

    corrected = hybrid_bias_correction(obs_train, gcm_train, raw)

    obs_val = obs[val_mask]
    raw_val = raw[val_mask]
    cor_val = corrected[val_mask]
    dates_val = dates[val_mask]

    obs_m = compute_metrics(obs_val, dates_val)
    raw_m = compute_metrics(raw_val, dates_val)
    cor_m = compute_metrics(cor_val, dates_val)

    if not np.isfinite(np.sum(cor_m)):
        continue

    # Individual biases
    bias_vals = np.abs(np.array(cor_m[:5]) - np.array(obs_m[:5]))
    extreme_bias = np.mean(bias_vals)

    raw_bias = np.mean(np.abs(np.array(raw_m[:5]) - np.array(obs_m[:5])))
    improvement = (raw_bias - extreme_bias) / raw_bias if raw_bias != 0 else 0
    improvement = np.clip(improvement, 0, 1)

    results.append({
        "model": file.stem,

        "OBS_RX1": obs_m[0], "OBS_RX3": obs_m[1], "OBS_RX5": obs_m[2],
        "OBS_P99": obs_m[3], "OBS_RL10": obs_m[4],

        "RAW_RX1": raw_m[0], "RAW_RX3": raw_m[1], "RAW_RX5": raw_m[2],
        "RAW_P99": raw_m[3], "RAW_RL10": raw_m[4],

        "COR_RX1": cor_m[0], "COR_RX3": cor_m[1], "COR_RX5": cor_m[2],
        "COR_P99": cor_m[3], "COR_RL10": cor_m[4],

        "Bias_RX1": bias_vals[0], "Bias_RX3": bias_vals[1], "Bias_RX5": bias_vals[2],
        "Bias_P99": bias_vals[3], "Bias_RL10": bias_vals[4],

        "Extreme_bias": extreme_bias,
        "AC1_bias": abs(cor_m[5] - obs_m[5]),
        "CWD_bias": abs(cor_m[6] - obs_m[6]),
        "CDD_bias": abs(cor_m[7] - obs_m[7]),
        "Improvement_ratio": improvement
    })


df = pd.DataFrame(results).set_index("model")

# =====================================================
# NORMALIZATION
# =====================================================
bias_cols = ["Extreme_bias", "AC1_bias", "CWD_bias", "CDD_bias"]

df_norm = df.copy()
for col in bias_cols:
    df_norm[col] = df[col] / df[col].max()

df_norm["Improvement_ratio"] = df["Improvement_ratio"]

# =====================================================
# SCORING
# =====================================================
df["Score_equal"] = 1 - (
    df_norm["Extreme_bias"] +
    df_norm["AC1_bias"] +
    df_norm["CWD_bias"] +
    df_norm["CDD_bias"] +
    (1 - df_norm["Improvement_ratio"])
) / 5

df["Score_extreme"] = 1 - (
    0.6 * df_norm["Extreme_bias"] +
    0.15 * df_norm["AC1_bias"] +
    0.10 * df_norm["CWD_bias"] +
    0.10 * df_norm["CDD_bias"] +
    0.05 * (1 - df_norm["Improvement_ratio"])
)

df["Rank_equal"] = df["Score_equal"].rank(ascending=False)
df["Rank_extreme"] = df["Score_extreme"].rank(ascending=False)

rho, pval = spearmanr(df["Rank_equal"], df["Rank_extreme"])

print("\nSpearman rho:", round(rho, 3))
print("p-value:", round(pval, 5))

df_sorted = df.sort_values("Score_extreme", ascending=False)
Path("outputs").mkdir(exist_ok=True)
df_sorted.to_excel(output_file)

print("\nFull transparent results saved to:", output_file)
