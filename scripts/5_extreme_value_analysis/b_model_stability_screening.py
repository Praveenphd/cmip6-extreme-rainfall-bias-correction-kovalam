"""
Multi-criteria stability screening of GCMs based on GEV return level
diagnostics.

Screens models on five criteria: monotonicity of empirical return
levels, GEV shape parameter stability, GEV-empirical agreement at the
50-year return period, confidence interval width at the 100-year
return period, and smoothness of empirical change factors across
return periods. Models scoring 5/5 are retained for the final ensemble
(Section 6.6).

Input : outputs/future_bias_corrected/<scenario>/return_level_results.xlsx
        (from Script 8)
Output: outputs/future_bias_corrected/<scenario>/model_stability_screening.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================
scenario = "ssp245"   # Change to "ssp585" for the other scenario

rl_file = f"outputs/future_bias_corrected/{scenario}/return_level_results.xlsx"
output_file = f"outputs/future_bias_corrected/{scenario}/model_stability_screening.xlsx"

shape_limit = 0.5
gev_emp_tolerance = 0.20     # 20% agreement tolerance
ci_ratio_limit = 2.5         # CI width relative to RL threshold

df = pd.read_excel(rl_file)
models = df["Model"].unique()
results = []

# =====================================================
# LOOP THROUGH MODELS
# =====================================================
for model in models:
    df_m = df[df["Model"] == model].sort_values("ReturnPeriod")
    T = df_m["ReturnPeriod"].values
    emp_hist = df_m["Emp_Hist"].values
    emp_future = df_m["Emp_Future"].values
    gev_future = df_m["GEV_Future"].values
    cf_emp = df_m["Emp_ChangeFactor"].values
    shape_hist = df_m["GEV_shape_hist"].iloc[0]
    shape_future = df_m["GEV_shape_future"].iloc[0]

    # 1. Monotonicity of empirical RL (future)
    mono_emp = np.all(np.diff(emp_future) >= -1e-6)

    # 2. Shape stability
    shape_flag = (
        abs(shape_hist) < shape_limit and
        abs(shape_future) < shape_limit
    )

    # 3. GEV vs Empirical Agreement (50-year)
    if 50 in T:
        idx_50 = list(T).index(50)
        gev_emp_diff = abs(gev_future[idx_50] - emp_future[idx_50]) / emp_future[idx_50]
        gev_emp_flag = gev_emp_diff < gev_emp_tolerance
    else:
        gev_emp_diff = np.nan
        gev_emp_flag = False

    # 4. CI Width Check (100-year)
    if 100 in T:
        idx_100 = list(T).index(100)
        ci_low = df_m["GEV_Future_CI_Low"].values[idx_100]
        ci_high = df_m["GEV_Future_CI_High"].values[idx_100]
        rl_val = gev_future[idx_100]
        if np.isfinite(ci_low) and np.isfinite(ci_high):
            ci_width_ratio = (ci_high - ci_low) / rl_val
            ci_flag = ci_width_ratio < ci_ratio_limit
        else:
            ci_width_ratio = np.nan
            ci_flag = False
    else:
        ci_width_ratio = np.nan
        ci_flag = False

    # 5. Change Factor Smoothness
    smooth_cf = np.all(np.diff(cf_emp) >= -0.20)

    # Scoring (0-5)
    score = sum([mono_emp, shape_flag, gev_emp_flag, ci_flag, smooth_cf])

    results.append({
        "Model": model,
        "Empirical_Monotonic": mono_emp,
        "Shape_Stable": shape_flag,
        "GEV_Emp_Diff_50yr": gev_emp_diff,
        "GEV_Emp_Agree": gev_emp_flag,
        "CI_Width_Ratio_100yr": ci_width_ratio,
        "CI_Stable": ci_flag,
        "Smooth_ChangeFactor": smooth_cf,
        "Stability_Score_0to5": score,
        "Shape_Hist": shape_hist,
        "Shape_Future": shape_future
    })

df_screen = pd.DataFrame(results)
df_screen = df_screen.sort_values("Stability_Score_0to5", ascending=False)
df_screen.to_excel(output_file, index=False)

print("\nFinal model stability screening completed.")
