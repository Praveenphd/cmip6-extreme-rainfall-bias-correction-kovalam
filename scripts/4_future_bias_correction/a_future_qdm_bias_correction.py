"""
Future bias correction using hybrid Quantile Delta Mapping (QDM) + GPD
tail adjustment, signal-preserving formulation.

For each GCM with both historical and future (SSP) data available,
trains bulk (EQM-based quantile mapping) and tail (GPD scale-ratio)
correction parameters on the historical period (1955-2014), then
applies the same correction to both historical and future series.
Produces historical and future bias-corrected time series for use in
extreme value analysis (Section 7).

Input : data/imd/ (IMD gridded rainfall CSV)
        data/gcm_csv/historical/<scenario>/ (raw historical GCM CSVs)
        data/gcm_csv/future/<scenario>/ (raw future GCM CSVs)
Output: outputs/future_bias_corrected/<scenario>/<model>_Historical_Corrected.csv
        outputs/future_bias_corrected/<scenario>/<model>_Future_Corrected.csv

Run once per scenario (e.g., ssp245, ssp585) by updating the
`scenario` and folder settings below.
"""

import pandas as pd
import numpy as np
from scipy.stats import genpareto
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================
wet_thr = 1.0
percentile_thr = 95   # Fixed, consistent with historical bias correction

scenario = "ssp245"   # Change to "ssp585" for the other scenario

imd_csv = "data/imd/imd_grid_kovalam.csv"
hist_folder = Path(f"data/gcm_csv/historical/{scenario}")
future_folder = Path(f"data/gcm_csv/future/{scenario}")
output_folder = Path(f"outputs/future_bias_corrected/{scenario}")

output_folder.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD IMD
# =====================================================
imd = pd.read_csv(imd_csv)
imd["date"] = pd.to_datetime(imd["Date"]).dt.floor("D")
imd["Rainfall"] = pd.to_numeric(imd["Rainfall"], errors="coerce")

imd = imd[(imd["date"] >= "1955-01-01") &
          (imd["date"] <= "2014-12-31")]

imd = imd[["date", "Rainfall"]].rename(columns={"Rainfall": "OBS"})

# =====================================================
# LOOP THROUGH HIST FILES
# =====================================================
for hist_file in hist_folder.glob("*.csv"):

    hist_name = hist_file.stem
    print(f"\nProcessing {hist_name}")

    base_model = hist_name.split("_pr_mm_day")[0]

    future_pattern = f"{base_model}_{scenario}_pr_mm_day*.csv"
    future_matches = list(future_folder.glob(future_pattern))

    if not future_matches:
        print("Future file not found. Skipping.")
        continue

    future_file = future_matches[0]

    # -----------------------------------------
    # LOAD HISTORICAL GCM
    # -----------------------------------------
    gcm_hist = pd.read_csv(hist_file)
    gcm_hist["date"] = pd.to_datetime(gcm_hist["time"]).dt.floor("D")
    gcm_hist["gcm_pr_mm_day"] = pd.to_numeric(
        gcm_hist["gcm_pr_mm_day"], errors="coerce"
    )

    gcm_hist = gcm_hist[(gcm_hist["date"] >= "1955-01-01") &
                         (gcm_hist["date"] <= "2014-12-31")]

    gcm_hist = gcm_hist[["date", "gcm_pr_mm_day"]]
    gcm_hist = gcm_hist.rename(columns={"gcm_pr_mm_day": "GCM"})

    df_hist = pd.merge(imd, gcm_hist, on="date", how="inner")

    if len(df_hist) < 20000:
        print("Merge issue. Skipping.")
        continue

    obs = df_hist["OBS"].values
    gcm_hist_vals = df_hist["GCM"].values

    # -----------------------------------------
    # LOAD FUTURE
    # -----------------------------------------
    gcm_future = pd.read_csv(future_file)
    gcm_future["date"] = pd.to_datetime(gcm_future["time"]).dt.floor("D")
    gcm_future["gcm_pr_mm_day"] = pd.to_numeric(
        gcm_future["gcm_pr_mm_day"], errors="coerce"
    )

    gcm_future = gcm_future[gcm_future["date"] >= "2015-01-01"]
    future_vals = gcm_future["gcm_pr_mm_day"].values

    # =================================================
    # TRAIN PARAMETERS (HISTORICAL ONLY)
    # =================================================
    obs_wet = obs[obs >= wet_thr]
    p_thr = np.percentile(obs_wet, percentile_thr)

    gcm_bulk = gcm_hist_vals[gcm_hist_vals < p_thr]
    obs_bulk = obs[obs < p_thr]

    gcm_sorted = np.sort(gcm_bulk)
    obs_sorted = np.sort(obs_bulk)

    q_gcm = np.linspace(0, 1, len(gcm_sorted))
    q_obs = np.linspace(0, 1, len(obs_sorted))

    obs_excess = obs[obs >= p_thr] - p_thr
    gcm_excess = gcm_hist_vals[gcm_hist_vals >= p_thr] - p_thr

    if len(obs_excess) < 50 or len(gcm_excess) < 50:
        print("Low tail sample. Skipping.")
        continue

    shape_o, _, scale_o = genpareto.fit(obs_excess, floc=0)
    shape_g, _, scale_g = genpareto.fit(gcm_excess, floc=0)

    scale_ratio = scale_o / scale_g

    # =================================================
    # HYBRID SIGNAL-PRESERVING FUNCTION
    # =================================================
    def hybrid_signal_preserving(vals):

        corrected = np.zeros_like(vals)

        for i, x in enumerate(vals):

            if x < wet_thr:
                corrected[i] = 0.0

            elif x < p_thr:
                q = np.interp(x, gcm_sorted, q_gcm)
                obs_hist_q = np.interp(q, q_obs, obs_sorted)

                delta = x / np.interp(q, q_gcm, gcm_sorted)
                corrected[i] = obs_hist_q * delta

            else:
                excess = x - p_thr
                corrected[i] = p_thr + excess * scale_ratio

        return corrected

    hist_corrected = hybrid_signal_preserving(gcm_hist_vals)
    future_corrected = hybrid_signal_preserving(future_vals)

    # -----------------------------------------
    # SAVE OUTPUTS
    # -----------------------------------------
    pd.DataFrame({
        "date": df_hist["date"],
        "OBS": obs,
        "RAW_GCM": gcm_hist_vals,
        "BIAS_CORRECTED": hist_corrected
    }).to_csv(output_folder / f"{base_model}_Historical_Corrected.csv", index=False)

    pd.DataFrame({
        "date": gcm_future["date"],
        "RAW_GCM": future_vals,
        "BIAS_CORRECTED": future_corrected
    }).to_csv(output_folder / f"{base_model}_Future_Corrected.csv", index=False)

print("\nAll models processed successfully.")
