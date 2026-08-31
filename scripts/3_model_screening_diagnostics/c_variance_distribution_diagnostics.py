"""
Variance and distributional diagnostics for bias-corrected rainfall.

Computes daily and annual-maximum variance, standard deviation ratio,
coefficient of variation, Kolmogorov-Smirnov statistic, and Q-Q slope
comparing observed (IMD), raw, and bias-corrected GCM rainfall over the
validation period (1985-2014). Supports Section 6.4.1 and Figures 6a, 6b.

Input : data/imd/ (IMD gridded rainfall CSV)
        outputs/top7_bias_corrected/ (bias-corrected CSVs from Script 3)
Output: outputs/variance_distribution_check.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import ks_2samp, linregress

# ==========================================
# USER INPUT
# ==========================================
imd_csv = "data/imd/imd_grid_kovalam.csv"
corrected_folder = Path("outputs/top7_bias_corrected")
val_start = "1985-01-01"
val_end = "2014-12-31"
output_file = "outputs/variance_distribution_check.xlsx"

# ==========================================
# LOAD OBSERVED DATA
# ==========================================
imd = pd.read_csv(imd_csv)
imd["date"] = pd.to_datetime(imd["Date"], format="%m/%d/%Y")
imd = imd[(imd["date"] >= val_start) & (imd["date"] <= val_end)]
imd = imd.rename(columns={"Rainfall": "OBS"})
imd = imd[["date", "OBS"]]

# ==========================================
# FUNCTION: QQ SLOPE (Spread Check)
# ==========================================
def qq_slope(obs, sim):
    obs_sorted = np.sort(obs)
    sim_sorted = np.sort(sim)
    min_len = min(len(obs_sorted), len(sim_sorted))
    obs_sorted = obs_sorted[:min_len]
    sim_sorted = sim_sorted[:min_len]
    slope, _, _, _, _ = linregress(obs_sorted, sim_sorted)
    return slope

# ==========================================
# LOOP THROUGH MODELS
# ==========================================
results = []
for file in corrected_folder.glob("*_BiasCorrected.csv"):
    model_name = file.stem.replace("_BiasCorrected", "")
    print("Processing:", model_name)

    df = pd.read_csv(file)
    df["date"] = pd.to_datetime(df["date"])
    df = df[(df["date"] >= val_start) & (df["date"] <= val_end)]
    df = pd.merge(imd, df, on="date", how="inner")

    obs = df["OBS"].values
    raw = df["RAW_GCM"].values
    cor = df["BIAS_CORRECTED"].values

    # Daily variance
    var_obs = np.var(obs)
    var_raw = np.var(raw)
    var_cor = np.var(cor)

    # Annual max variance
    df["year"] = df["date"].dt.year
    ann_obs = df.groupby("year")["OBS"].max().values
    ann_raw = df.groupby("year")["RAW_GCM"].max().values
    ann_cor = df.groupby("year")["BIAS_CORRECTED"].max().values

    var_ann_obs = np.var(ann_obs)
    var_ann_raw = np.var(ann_raw)
    var_ann_cor = np.var(ann_cor)

    # Standard deviation ratio
    std_ratio = np.std(cor) / np.std(obs)

    # Coefficient of variation
    cv_obs = np.std(obs) / np.mean(obs)
    cv_cor = np.std(cor) / np.mean(cor)

    # KS test
    ks_stat_raw, ks_p_raw = ks_2samp(obs, raw)
    ks_stat_cor, ks_p_cor = ks_2samp(obs, cor)

    # QQ slope
    qq_raw = qq_slope(obs, raw)
    qq_cor = qq_slope(obs, cor)

    results.append({
        "Model": model_name,
        "Var_daily_obs": var_obs,
        "Var_daily_raw": var_raw,
        "Var_daily_cor": var_cor,
        "Var_annmax_obs": var_ann_obs,
        "Var_annmax_raw": var_ann_raw,
        "Var_annmax_cor": var_ann_cor,
        "Std_ratio_cor_obs": std_ratio,
        "CV_obs": cv_obs,
        "CV_cor": cv_cor,
        "KS_stat_raw": ks_stat_raw,
        "KS_p_raw": ks_p_raw,
        "KS_stat_cor": ks_stat_cor,
        "KS_p_cor": ks_p_cor,
        "QQ_slope_raw": qq_raw,
        "QQ_slope_cor": qq_cor
    })

df_results = pd.DataFrame(results).set_index("Model")
Path("outputs").mkdir(exist_ok=True)
df_results.to_excel(output_file)

print("\nVariance & distribution diagnostics saved to:", output_file)
