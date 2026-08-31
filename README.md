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
