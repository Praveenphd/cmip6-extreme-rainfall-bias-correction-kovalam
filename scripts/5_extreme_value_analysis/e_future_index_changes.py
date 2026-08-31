"""
Future percentage changes in extreme rainfall indices, internal
(model-own) baseline.

For each stability-screened model, computes RX1, RX3, RX5, P99, RL10,
AC1, CWD, and CDD over three future time slices (near-term, mid-term,
late-century), expressed as percentage change relative to that same
model's own bias-corrected historical baseline (1955-2014). Also
computes the ensemble median across models per period. Supports
Section 7 and Figures 11-15b.

Input : outputs/future_bias_corrected/<scenario>/ (bias-corrected CSVs
        from Script 7)
        outputs/future_bias_corrected/<scenario>/model_stability_screening.xlsx
        (from Script 9)
Output: outputs/future_bias_corrected/<scenario>/future_index_changes_model.xlsx
        outputs/future_bias_corrected/<scenario>/future_index_changes_ensemble_median.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================
scenario = "ssp245"   # Change to "ssp585" for the other scenario

data_folder = Path(f"outputs/future_bias_corrected/{scenario}")
screen_file = data_folder / "model_stability_screening.xlsx"

hist_start = "1955-01-01"
hist_end = "2014-12-31"

future_periods = {
    "Near_Future": ("2015-01-01", "2044-12-31"),
    "Mid_Century": ("2045-01-01", "2074-12-31"),
    "Late_Century": ("2075-01-01", "2100-12-31")
}

wet_thr = 1.0

output_model_file = data_folder / "future_index_changes_model.xlsx"
output_ensemble_file = data_folder / "future_index_changes_ensemble_median.xlsx"

# =====================================================
# LOAD STABLE MODELS
# =====================================================
df_screen = pd.read_excel(screen_file)
stable_models = df_screen[df_screen["Stability_Score_0to5"] == 5]["Model"].tolist()

print("Stable Models Used:")
for m in stable_models:
    print(m)

# =====================================================
# INDEX FUNCTION
# =====================================================
def compute_indices(series, dates):

    df = pd.DataFrame({"date": dates, "rain": series})
    df["year"] = df["date"].dt.year

    annual_max = df.groupby("year")["rain"].max()

    RX1 = annual_max.mean()
    RX3 = df.groupby("year")["rain"].apply(lambda x: x.rolling(3).sum().max()).mean()
    RX5 = df.groupby("year")["rain"].apply(lambda x: x.rolling(5).sum().max()).mean()
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

    return {
        "RX1": RX1, "RX3": RX3, "RX5": RX5, "P99": P99,
        "RL10": RL10, "AC1": AC1, "CWD": CWD, "CDD": CDD
    }

# =====================================================
# PROCESS MODELS
# =====================================================
all_results = []

for model in stable_models:

    print(f"\nProcessing {model}")

    hist_file = data_folder / f"{model}_Historical_Corrected.csv"
    hist_df = pd.read_csv(hist_file)
    hist_df["date"] = pd.to_datetime(hist_df["date"])

    hist_df = hist_df[
        (hist_df["date"] >= hist_start) &
        (hist_df["date"] <= hist_end)
    ]

    hist_indices = compute_indices(hist_df["BIAS_CORRECTED"].values, hist_df["date"])

    fut_file = data_folder / f"{model}_Future_Corrected.csv"
    fut_df = pd.read_csv(fut_file)
    fut_df["date"] = pd.to_datetime(fut_df["date"])

    for period_name, (start, end) in future_periods.items():

        period_df = fut_df[
            (fut_df["date"] >= start) &
            (fut_df["date"] <= end)
        ]

        fut_indices = compute_indices(period_df["BIAS_CORRECTED"].values, period_df["date"])

        change = {
            key: 100 * (fut_indices[key] - hist_indices[key]) / hist_indices[key]
            for key in hist_indices
        }

        row = {"Model": model, "Period": period_name}
        row.update(change)
        all_results.append(row)

df_results = pd.DataFrame(all_results)
df_results.to_excel(output_model_file, index=False)

print("Model-wise internal baseline changes saved.")

# =====================================================
# ENSEMBLE MEDIAN
# =====================================================
ensemble = (
    df_results
    .groupby("Period")
    .median(numeric_only=True)
    .reset_index()
)

ensemble.to_excel(output_ensemble_file, index=False)

print("Ensemble median (internal baseline) saved.")
