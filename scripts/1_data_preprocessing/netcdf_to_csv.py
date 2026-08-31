"""
Convert raw CMIP6 NetCDF precipitation files to CSV format.

Converts precipitation units from kg/m^2/s to mm/day, corrects longitude
convention (0-360 to -180-180), and extracts the nearest grid point to
each specified target coordinate (IMD grid locations).

Input : NetCDF (.nc) files in data/raw_gcm_netcdf/
Output: CSV files in data/gcm_csv/, one per model-scenario-location
"""

import xarray as xr
from pathlib import Path

# ---------------- USER INPUT ----------------
nc_folder = Path("data/raw_gcm_netcdf")   # Folder containing CMIP6 .nc files
output_folder = Path("data/gcm_csv")
output_folder.mkdir(parents=True, exist_ok=True)

# Target coordinates: IMD grid points surrounding the Kovalam Basin
targets = [
    (12.50, 80.00),
    (12.75, 80.00),
    (13.00, 80.00)
]
# --------------------------------------------

# Loop through all NetCDF files
for nc_path in nc_folder.glob("*.nc"):
    print(f"\n==============================")
    print(f"Processing file: {nc_path.name}")
    print(f"==============================")

    # Extract model + scenario automatically from filename
    file_parts = nc_path.stem.split("_")
    model_name = file_parts[2]
    scenario = file_parts[3]
    out_prefix = f"{model_name}_{scenario}_pr_mm_day"

    # Open dataset
    ds = xr.open_dataset(nc_path, engine="netcdf4")

    # Grid resolution
    dlat = float(ds.lat.diff("lat").median())
    dlon = float(ds.lon.diff("lon").median())
    print(f"Grid resolution -> dlat = {dlat} deg, dlon = {dlon} deg")

    # Fix longitude (0-360 -> -180-180)
    ds = ds.assign_coords(
        lon=((ds.lon + 180) % 360) - 180
    ).sortby("lon")

    # Convert rainfall to mm/day
    ds["pr_mm_day"] = ds["pr"] * 86400
    ds["pr_mm_day"].attrs["units"] = "mm/day"

    # Extract each target grid
    for i, (lat, lon) in enumerate(targets, start=1):
        da = ds["pr_mm_day"].sel(
            lat=lat,
            lon=lon,
            method="nearest"
        )
        used_lat = float(da.lat.values)
        used_lon = float(da.lon.values)

        print(f"\nTarget {i}")
        print(f"Requested coordinate : ({lat}, {lon})")
        print(f"Selected GCM grid    : ({used_lat}, {used_lon})")

        df = da.to_dataframe(name="gcm_pr_mm_day").reset_index()
        out_csv = f"{out_prefix}_lat{used_lat:.2f}_lon{used_lon:.2f}.csv"
        df.to_csv(output_folder / out_csv, index=False)
        print(f"CSV written -> {out_csv}")

    ds.close()

print("\nAll files processed. Units = mm/day. Ready for bias correction.")
