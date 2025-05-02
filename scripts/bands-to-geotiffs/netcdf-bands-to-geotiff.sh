## set variables for path, NETCDF, and variable to extract (optional: file suffixes)
netcdf="Z:\global-dataset-cache\Global_ExternalSources\Public\koppen_geiger_climatezones\raw_downloads\climate_data_0p1\1991_2020\ensemble_mean_0p1.nc"
outpath="Z:\global-dataset-cache\Global_ExternalSources\Public\koppen_geiger_climatezones\climate_data"
variable=air_temperature
suffix="climate_1991_2020_0p1_temp"
CACHE="GDAL_CACHEMAX=2048"

# turn NETCDF variable into geotiff
#gdal_translate -of GTiff NETCDF:$netcdf:$variable $outpath/$suffix.tif

# extract bands and set as separate geotiffs
#python band-to-separate-geotiff.py $outpath/$suffix.tif $outpath/$suffix $suffix 'monthly'

# raster calculations for summing or averaging bands
python raster-sum.py $outpath/$suffix 'monthly' $outpath $suffix 'annual_avg'

# convert resulting geotiffs to COGs using scripts/tiff-to-cog-conversions/tif-to-cog.sbatch.sh