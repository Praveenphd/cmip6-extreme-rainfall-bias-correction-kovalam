"""
Ensemble return level change factor summary.

Aggregates empirical change factors (future/historical return level
ratios) across stability-screened models to compute the ensemble
median, mean, interquartile range, and standard deviation at each
return period. These are the EM-SSP2-4.5 / EM-SSP5-8.5 values reported
in Section 6.7.

Input : outputs/future_bias_corrected/<scenario>/return_level_results.xlsx
        (from Script 8)
        outputs/future_bias_corrected/<scenario>/model_stability_screening.xlsx
        (from Script 9)
Output: outputs/future_bias_corrected/<scenario>/ensemble_return_level_summary.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================
scenario = "ssp245"   # Change to "ssp585" for the other scenario

rl_file = f"outputs/future_bias_corrected/{scenario}/return_level_results.xlsx"
screen_file = f"outputs/future_bias_corrected/{scenario}/model_stability_screening.xlsx"
output_folder = Path(f"outputs/future_bias_corrected/{scenario}")

# =====================================================
# LOAD DATA
# =====================================================
df_rl = pd.read_excel(rl_file)
df_screen = pd.read_excel(screen_file)

# Select only models scoring 5/5
stable_models = df_screen[df_screen["Stability_Score_0to5"] == 5]["Model"].tolist()
print("Stable Models Used for Ensemble:")
for m in stable_models:
    print(m)

df_rl = df_rl[df_rl["Model"].isin(stable_models)]
df_rl = df_rl[["Model", "ReturnPeriod", "Emp_ChangeFactor"]]

# =====================================================
# ENSEMBLE STATISTICS
# =====================================================
ensemble_stats = []
for T in sorted(df_rl["ReturnPeriod"].unique()):
    df_T = df_rl[df_rl["ReturnPeriod"] == T]
    median_cf = np.median(df_T["Emp_ChangeFactor"])
    mean_cf = np.mean(df_T["Emp_ChangeFactor"])
    q25 = np.percentile(df_T["Emp_ChangeFactor"], 25)
    q75 = np.percentile(df_T["Emp_ChangeFactor"], 75)
    std_cf = np.std(df_T["Emp_ChangeFactor"])

    ensemble_stats.append({
        "ReturnPeriod": T,
        "Median_CF": median_cf,
        "Mean_CF": mean_cf,
        "Q25_CF": q25,
        "Q75_CF": q75,
        "Std_CF": std_cf
    })

ensemble_df = pd.DataFrame(ensemble_stats)
ensemble_df.to_excel(
    output_folder / "ensemble_return_level_summary.xlsx",
    index=False
)

print("\nEnsemble summary table saved.")
