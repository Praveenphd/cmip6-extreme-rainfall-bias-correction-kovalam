"""
GEV-based return level analysis with bootstrap confidence intervals.

For each bias-corrected GCM (historical and future), fits the
Generalized Extreme Value (GEV) distribution to annual maxima and
computes empirical and GEV-based return levels for a range of return
periods. Confidence intervals are estimated via parametric bootstrap
with stability filtering on the fitted shape parameter. Supports
Section 6.5-6.6 and Figure 9.

Input : outputs/future_bias_corrected/<scenario>/<model>_Historical_Corrected.csv
        outputs/future_bias_corrected/<scenario>/<model>_Future_Corrected.csv
        (from Script 7 — run separately per scenario)
Output: outputs/future_bias_corrected/<scenario>/return_level_results.xlsx
"""

import pandas as pd
import numpy as np
from scipy.stats import genextreme
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================
scenario = "ssp245"   # Change to "ssp585" for the other scenario

corrected_folder = Path(f"outputs/future_bias_corrected/{scenario}")
output_file = corrected_folder / "return_level_results.xlsx"

return_periods = [10, 25, 50, 100]
n_boot = 300              # Balanced speed vs stability
shape_limit = 0.5         # Filter unrealistic shape
min_scale = 1e-6          # Prevent zero/negative scale

results = []

# =====================================================
# EMPIRICAL RETURN LEVEL
# =====================================================
def empirical_rl(data, T):
    data_sorted = np.sort(data)[::-1]
    n = len(data_sorted)
    ranks = np.arange(1, n + 1)
    return_period = (n + 1) / ranks
    return np.interp(T, return_period[::-1], data_sorted[::-1])

# =====================================================
# BOOTSTRAP GEV PARAMETERS (FILTERED)
# =====================================================
def bootstrap_gev_params(data, n_boot=400):

    param_samples = []

    for _ in range(n_boot):
        sample = np.random.choice(data, size=len(data), replace=True)

        try:
            c, loc, scale = genextreme.fit(sample)

            if (
                np.isfinite(c) and
                np.isfinite(loc) and
                np.isfinite(scale) and
                abs(c) < shape_limit and
                scale > min_scale
            ):
                param_samples.append((c, loc, scale))

        except Exception:
            continue

    return param_samples

# =====================================================
# LOOP THROUGH MODELS
# =====================================================
for hist_file in corrected_folder.glob("*_Historical_Corrected.csv"):

    model_name = hist_file.stem.replace("_Historical_Corrected", "")
    future_file = corrected_folder / f"{model_name}_Future_Corrected.csv"

    if not future_file.exists():
        continue

    print(f"\nProcessing {model_name}")

    df_hist = pd.read_csv(hist_file)
    df_future = pd.read_csv(future_file)

    df_hist["date"] = pd.to_datetime(df_hist["date"])
    df_future["date"] = pd.to_datetime(df_future["date"])

    df_hist["year"] = df_hist["date"].dt.year
    df_future["year"] = df_future["date"].dt.year

    ann_hist = df_hist.groupby("year")["BIAS_CORRECTED"].max().values
    ann_future = df_future.groupby("year")["BIAS_CORRECTED"].max().values

    c_hist, loc_hist, scale_hist = genextreme.fit(ann_hist)
    c_future, loc_future, scale_future = genextreme.fit(ann_future)

    boot_hist = bootstrap_gev_params(ann_hist, n_boot)
    boot_future = bootstrap_gev_params(ann_future, n_boot)

    for T in return_periods:

        emp_hist = empirical_rl(ann_hist, T)
        emp_future = empirical_rl(ann_future, T)

        gev_hist = genextreme.ppf(1 - 1 / T, c_hist, loc_hist, scale_hist)
        gev_future = genextreme.ppf(1 - 1 / T, c_future, loc_future, scale_future)

        rl_hist_samples = np.array([
            genextreme.ppf(1 - 1 / T, c, loc, scale)
            for (c, loc, scale) in boot_hist
        ])
        rl_future_samples = np.array([
            genextreme.ppf(1 - 1 / T, c, loc, scale)
            for (c, loc, scale) in boot_future
        ])

        rl_hist_samples = rl_hist_samples[np.isfinite(rl_hist_samples)]
        rl_future_samples = rl_future_samples[np.isfinite(rl_future_samples)]

        if len(rl_hist_samples) > 20:
            ci_hist_low = np.percentile(rl_hist_samples, 2.5)
            ci_hist_high = np.percentile(rl_hist_samples, 97.5)
        else:
            ci_hist_low = np.nan
            ci_hist_high = np.nan

        if len(rl_future_samples) > 20:
            ci_future_low = np.percentile(rl_future_samples, 2.5)
            ci_future_high = np.percentile(rl_future_samples, 97.5)
        else:
            ci_future_low = np.nan
            ci_future_high = np.nan

        results.append({
            "Model": model_name,
            "ReturnPeriod": T,
            "Emp_Hist": emp_hist,
            "Emp_Future": emp_future,
            "Emp_ChangeFactor": emp_future / emp_hist,
            "GEV_Hist": gev_hist,
            "GEV_Future": gev_future,
            "GEV_ChangeFactor": gev_future / gev_hist,
            "GEV_Hist_CI_Low": ci_hist_low,
            "GEV_Hist_CI_High": ci_hist_high,
            "GEV_Future_CI_Low": ci_future_low,
            "GEV_Future_CI_High": ci_future_high,
            "GEV_shape_hist": c_hist,
            "GEV_shape_future": c_future
        })

df_results = pd.DataFrame(results)
df_results.to_excel(output_file, index=False)

print("\nReturn level analysis (bootstrap) completed successfully.")
