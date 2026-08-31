"""
Climate signal preservation diagnostics.

Compares change factors (future/historical ratios) for mean rainfall,
RX1, and P99 between raw and bias-corrected GCM output, for models
retained after stability screening. Quantifies the extent to which
bias correction distorts the projected climate change signal
(Section 6.8).

Input : outputs/future_bias_corrected/<scenario>/ (bias-corrected CSVs
        from Script 7)
        data/gcm_csv/historical/<scenario>/ and data/gcm_csv/future/<scenario>/
        (raw GCM CSVs)
        outputs/future_bias_corrected/<scenario>/model_stability_screening.xlsx
        (from Script 9)
Output: outputs/future_bias_corrected/<scenario>/climate_signal_preservation.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================
scenario = "ssp245"   # Change to "ssp585" for the other scenario

data_folder = Path(f"outputs/future_bias_corrected/{scenario}")
raw_hist_folder = Path(f"data/gcm_csv/historical/{scenario}")
raw_future_folder = Path(f"data/gcm_csv/future/{scenario}")

screen_file = data_folder / "model_stability_screening.xlsx"
output_file = data_folder / "climate_signal_preservation.xlsx"

wet_thr = 1.0

# =====================================================
# LOAD STABLE MODELS
# =====================================================
df_screen = pd.read_excel(screen_file)
stable_models = df_screen[df_screen["Stability_Score_0to5"] == 5]["Model"].tolist()

print("Stable Models:")
for m in stable_models:
    print(m)

results = []

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def compute_metrics(series, dates):

    df = pd.DataFrame({"date": dates, "rain": series})
    df["year"] = df["date"].dt.year

    annual_max = df.groupby("year")["rain"].max()

    mean_val = np.mean(series)
    RX1 = annual_max.mean()
    P99 = np.percentile(series, 99)

    return mean_val, RX1, P99

# =====================================================
# LOOP MODELS
# =====================================================
for model in stable_models:

    print(f"\nProcessing {model}")

    hist_corr = pd.read_csv(data_folder / f"{model}_Historical_Corrected.csv")
    fut_corr = pd.read_csv(data_folder / f"{model}_Future_Corrected.csv")

    hist_corr["date"] = pd.to_datetime(hist_corr["date"])
    fut_corr["date"] = pd.to_datetime(fut_corr["date"])

    hist_raw_file = list(raw_hist_folder.glob(f"{model}*.csv"))[0]
    fut_raw_file = list(raw_future_folder.glob(f"{model}*.csv"))[0]

    hist_raw = pd.read_csv(hist_raw_file)
    fut_raw = pd.read_csv(fut_raw_file)

    hist_raw["date"] = pd.to_datetime(hist_raw["time"]).dt.floor("D")
    fut_raw["date"] = pd.to_datetime(fut_raw["time"]).dt.floor("D")

    hist_raw = hist_raw[(hist_raw["date"] >= "1955-01-01") &
                         (hist_raw["date"] <= "2014-12-31")]

    fut_raw = fut_raw[fut_raw["date"] >= "2015-01-01"]

    mean_raw_hist, rx1_raw_hist, p99_raw_hist = compute_metrics(
        hist_raw["gcm_pr_mm_day"].values, hist_raw["date"]
    )
    mean_raw_fut, rx1_raw_fut, p99_raw_fut = compute_metrics(
        fut_raw["gcm_pr_mm_day"].values, fut_raw["date"]
    )
    mean_cor_hist, rx1_cor_hist, p99_cor_hist = compute_metrics(
        hist_corr["BIAS_CORRECTED"].values, hist_corr["date"]
    )
    mean_cor_fut, rx1_cor_fut, p99_cor_fut = compute_metrics(
        fut_corr["BIAS_CORRECTED"].values, fut_corr["date"]
    )

    cf_mean_raw = mean_raw_fut / mean_raw_hist
    cf_rx1_raw = rx1_raw_fut / rx1_raw_hist
    cf_p99_raw = p99_raw_fut / p99_raw_hist

    cf_mean_cor = mean_cor_fut / mean_cor_hist
    cf_rx1_cor = rx1_cor_fut / rx1_cor_hist
    cf_p99_cor = p99_cor_fut / p99_cor_hist

    dist_mean = 100 * (cf_mean_cor - cf_mean_raw) / cf_mean_raw
    dist_rx1 = 100 * (cf_rx1_cor - cf_rx1_raw) / cf_rx1_raw
    dist_p99 = 100 * (cf_p99_cor - cf_p99_raw) / cf_p99_raw

    results.append({
        "Model": model,
        "CF_Mean_Raw": cf_mean_raw,
        "CF_Mean_Corrected": cf_mean_cor,
        "Distortion_Mean_%": dist_mean,
        "CF_RX1_Raw": cf_rx1_raw,
        "CF_RX1_Corrected": cf_rx1_cor,
        "Distortion_RX1_%": dist_rx1,
        "CF_P99_Raw": cf_p99_raw,
        "CF_P99_Corrected": cf_p99_cor,
        "Distortion_P99_%": dist_p99
    })

df_out = pd.DataFrame(results)
df_out.to_excel(output_file, index=False)

print("\nClimate signal preservation diagnostics completed.")
