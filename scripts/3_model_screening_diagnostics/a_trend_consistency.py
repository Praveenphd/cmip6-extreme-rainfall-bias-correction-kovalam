"""
Trend consistency check between observed and bias-corrected rainfall.

Computes Kendall's tau and Sen's slope for annual maximum rainfall over
the validation period (1985-2014), for both the IMD observed series and
each bias-corrected GCM. Flags any model showing a statistically
significant trend where none exists in the observed series, indicating
an artificial trend introduced by bias correction.

Input : data/imd/ (IMD gridded rainfall CSV)
        outputs/top7_bias_corrected/ (bias-corrected CSVs from Script 3)
Output: outputs/trend_consistency_results.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import kendalltau

# ==========================================
# USER INPUT
# ==========================================
imd_csv = "data/imd/imd_grid_kovalam.csv"
corrected_folder = Path("outputs/top7_bias_corrected")
val_start = "1985-01-01"
val_end = "2014-12-31"
output_file = "outputs/trend_consistency_results.xlsx"

# ==========================================
# FUNCTION: SEN'S SLOPE
# ==========================================
def sens_slope(y):
    n = len(y)
    slopes = []
    for i in range(n):
        for j in range(i + 1, n):
            slopes.append((y[j] - y[i]) / (j - i))
    return np.median(slopes)

# ==========================================
# OBSERVED TREND
# ==========================================
imd = pd.read_csv(imd_csv)
imd["date"] = pd.to_datetime(imd["Date"], format="%m/%d/%Y")
imd = imd[(imd["date"] >= val_start) & (imd["date"] <= val_end)]
imd["year"] = imd["date"].dt.year
annual_max_obs = imd.groupby("year")["Rainfall"].max()
years = np.arange(len(annual_max_obs))
tau_obs, p_obs = kendalltau(years, annual_max_obs.values)
slope_obs = sens_slope(annual_max_obs.values)

print("\nObserved Trend (Validation Period)")
print("Kendall tau:", round(tau_obs, 3))
print("p-value:", round(p_obs, 5))
print("Sen slope:", round(slope_obs, 3), "mm/year")

# ==========================================
# MODEL TREND TEST
# ==========================================
results = []
for file in corrected_folder.glob("*_BiasCorrected.csv"):
    model_name = file.stem.replace("_BiasCorrected", "")
    df = pd.read_csv(file)
    df["date"] = pd.to_datetime(df["date"])
    df = df[(df["date"] >= val_start) & (df["date"] <= val_end)]
    df["year"] = df["date"].dt.year
    annual_max_model = df.groupby("year")["BIAS_CORRECTED"].max()
    years_mod = np.arange(len(annual_max_model))
    tau_mod, p_mod = kendalltau(years_mod, annual_max_model.values)
    slope_mod = sens_slope(annual_max_model.values)

    if p_obs > 0.05 and p_mod < 0.05:
        flag = "Artificial Trend"
    else:
        flag = "Consistent"

    results.append({
        "model": model_name,
        "tau_model": tau_mod,
        "p_model": p_mod,
        "Sen_slope_model": slope_mod,
        "Trend_flag": flag
    })

df_results = pd.DataFrame(results).set_index("model")
Path("outputs").mkdir(exist_ok=True)
df_results.to_excel(output_file)

print("\nTrend consistency results saved to:", output_file)
