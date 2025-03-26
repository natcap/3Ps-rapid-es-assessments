## set variables for path, NETCDF, and variable to extract (optional: file suffixes)
path="Z:\global-dataset-cache\Global_ExternalSources\Public\koppen_geiger_climatezones\raw_downloads\climate_data_0p1\1991_2020"
outpath="Z:\global-dataset-cache\Global_ExternalSources\Public\koppen_geiger_climatezones\climate_data"
netcdf="ensemble_mean_0p1.nc"
variable=precipitation
suffix="1991_2020_0p1_precip"
CACHE="GDAL_CACHEMAX=2048"

# turn NETCDF variable into geotiff
gdal_translate -of GTiff NETCDF:$path/$netcdf:$variable $outpath/$suffix.tif

# raster calculations for summing or averaging bands

# extract bands and set as separate geotiffs