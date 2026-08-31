"""
Figure 3: Daily precipitation climatology, IMD vs. individual CMIP6 GCMs
(1955-2014). Supports Section 5.1.

Input : data/imd/ (IMD gridded rainfall CSV)
        data/gcm_csv/ (raw GCM CSVs from Script 1)
Output: outputs/figures/fig03_climatology.jpg
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================
imd_csv = "data/imd/imd_grid_kovalam.csv"
gcm_folder = Path("data/gcm_csv")
output_folder = Path("outputs/figures")
output_folder.mkdir(parents=True, exist_ok=True)

start_date = "1955-01-01"
end_date = "2014-12-31"
smooth_window = 15  # days, light smoothing only for visual clarity

# =====================================================
# LOAD IMD
# =====================================================
imd = pd.read_csv(imd_csv)
imd["date"] = pd.to_datetime(imd["Date"], format="%m/%d/%Y")
imd = imd[["date", "Rainfall"]].rename(columns={"Rainfall": "IMD"})
imd = imd[(imd["date"] >= start_date) & (imd["date"] <= end_date)]
imd["doy"] = imd["date"].dt.dayofyear
imd = imd[imd["doy"] <= 365]

imd_clim = imd.groupby("doy")["IMD"].mean()
imd_clim_smooth = imd_clim.rolling(smooth_window, center=True, min_periods=1).mean()

# =====================================================
# LOAD ALL GCMs AND COMPUTE CLIMATOLOGY
# =====================================================
gcm_climatologies = {}
for file in gcm_folder.glob("*.csv"):
    model_name = file.stem.split("_pr_mm_day")[0]

    gcm = pd.read_csv(file)
    gcm["date"] = pd.to_datetime(gcm["time"]).dt.floor("D")
    gcm = gcm[["date", "gcm_pr_mm_day"]].rename(columns={"gcm_pr_mm_day": "GCM"})
    gcm = gcm[(gcm["date"] >= start_date) & (gcm["date"] <= end_date)]
    gcm["doy"] = gcm["date"].dt.dayofyear
    gcm = gcm[gcm["doy"] <= 365]

    clim = gcm.groupby("doy")["GCM"].mean()
    clim_smooth = clim.rolling(smooth_window, center=True, min_periods=1).mean()
    gcm_climatologies[model_name] = clim_smooth

gcm_df = pd.DataFrame(gcm_climatologies)

# =====================================================
# PLOT
# =====================================================
plt.figure(figsize=(12, 6))
plt.plot(imd_clim_smooth.index, imd_clim_smooth.values,
         color="black", linewidth=2.5, label="IMD (Observed)", zorder=10)

for model in gcm_df.columns:
    plt.plot(gcm_df.index, gcm_df[model], linewidth=0.8, alpha=0.6, label=model)

plt.xlabel("Day of Year")
plt.ylabel("Mean Daily Precipitation (mm/day)")
plt.title("Daily Precipitation Climatology: IMD vs. Individual CMIP6 GCMs (1955-2014)")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7, ncol=1)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(output_folder / "fig03_climatology.jpg", dpi=300)
plt.show()

print("Figure 3 saved.")
