# CMIP6 Extreme Rainfall Bias Correction — Kovalam Basin

Code accompanying the manuscript: *Projection of Extreme Rainfall Characteristics over the Kovalam Basin (Chennai, India) Using a Hybrid Bias Correction Framework for CMIP6 Models*.

## Overview

This repository contains the analysis and plotting scripts used to:
- Bias-correct historical and future CMIP6 precipitation using a hybrid Empirical Quantile Mapping (EQM) + Generalized Pareto Distribution (GPD) / Quantile Delta Mapping (QDM) framework
- Screen and rank CMIP6 GCMs by extreme rainfall performance
- Assess model reliability using GEV-based return level analysis
- Quantify projected changes in extreme rainfall indices under SSP2-4.5 and SSP5-8.5 scenarios

## Data sources

Raw data are not included in this repository due to licensing and file size. They are publicly available from:
- **IMD gridded rainfall (0.25° x 0.25°):** [IMD Pune data portal](https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html)
- **CMIP6 GCM output:** [Earth System Grid Federation (ESGF)](https://esgf-node.llnl.gov/search/cmip6/)

Place downloaded files under `data/imd/` and `data/raw_gcm_netcdf/` respectively before running the scripts.

## Repository structure

# CMIP6 Extreme Rainfall Bias Correction — Kovalam Basin

Code accompanying the manuscript: *Projection of Extreme Rainfall Characteristics over the Kovalam Basin (Chennai, India) Using a Hybrid Bias Correction Framework for CMIP6 Models*.

## Overview

This repository contains the analysis and plotting scripts used to:
- Bias-correct historical and future CMIP6 precipitation using a hybrid Empirical Quantile Mapping (EQM) + Generalized Pareto Distribution (GPD) / Quantile Delta Mapping (QDM) framework
- Screen and rank CMIP6 GCMs by extreme rainfall performance
- Assess model reliability using GEV-based return level analysis
- Quantify projected changes in extreme rainfall indices under SSP2-4.5 and SSP5-8.5 scenarios

## Data sources

Raw data are not included in this repository due to licensing and file size. They are publicly available from:
- **IMD gridded rainfall (0.25° x 0.25°):** [IMD Pune data portal](https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html)
- **CMIP6 GCM output:** [Earth System Grid Federation (ESGF)](https://esgf-node.llnl.gov/search/cmip6/)

Place downloaded files under `data/imd/` and `data/raw_gcm_netcdf/` respectively before running the scripts.

## Repository structure


Scripts are numbered in the order they should be run within each folder. Several scripts in `4_future_bias_correction` and `5_extreme_value_analysis` are run once per emission scenario (SSP2-4.5, SSP5-8.5) by changing the `scenario` variable at the top of the script.

## Methodology summary

- Historical baseline: 1955-2014 (constrained by IMD data availability); training period 1955-1984, validation 1985-2014
- Bias correction threshold: 95th percentile of observed wet-day rainfall (>= 1 mm), selected via sensitivity analysis (Figs. 4a, 4b)
- Final ensemble: 4 models (BCC-CSM2-MR, CanESM5, GFDL-ESM4, IPSL-CM6A-LR), selected via multi-criteria stability screening on GEV return level diagnostics
- Future periods: near-term (2021-2040), mid-term (2041-2060), long-term (2081-2100)

## Requirements

See `requirements.txt`. Install with:


## Citation

If you use this code, please cite the associated manuscript (details to be added upon publication).

## Contact

Praveenbalaji Bheeman — pb4338@srmist.edu.in
Department of Civil Engineering, SRM Institute of Science and Technology
