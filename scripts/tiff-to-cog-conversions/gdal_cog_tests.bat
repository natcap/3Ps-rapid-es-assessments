module load physics gdal/3.5.2

## gdal translate test from: https://github.com/cogeotiff/cog-spec/blob/master/spec.md
## based on info from here: https://www.earthdata.nasa.gov/engage/cloud-optimized-geotiffs
## note: layers like the LULC need stying changes - need to see how to do that programatically
gdal_translate plant_available_water_fraction_gura.tif plant_available_water_fraction_gura_nasa_cog.tif -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW

#https://github.com/OSGeo/gdal/blob/master/swig/python/gdal-utils/osgeo_utils/samples/validate_cloud_optimized_geotiff.py

## example on sherlock
# NASA
GDAL_CACHEMAX=2048 gdal_translate nitrogen_retention_for_downstream_populations.tif nitrogen_retention_for_downstream_populations_nasa_cog.tif -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW -co BIGTIFF=YES
GDAL_CACHEMAX=2048 gdal_translate coastal_risk_reduction_for_coastal_populations_thresholded.tif coastal_risk_reduction_for_coastal_populations_thresholded_nasa_cog.tif -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW

#GDAL
GDAL_CACHEMAX=2048 gdal_translate nitrogen_retention_for_downstream_populations.tif nitrogen_retention_for_downstream_populations_gdal_cog.tif -of cog -co BIGTIFF=YES
GDAL_CACHEMAX=2048 gdal_translate coastal_risk_reduction_for_coastal_populations_thresholded.tif coastal_risk_reduction_for_coastal_populations_thresholded_gdal_cog.tif -of cog
GDAL_CACHEMAX=2048 gdal_translate nitrogen_retention_for_downstream_populations.tif nitrogen_retention_for_downstream_populations_gdal_cog2.tif -of cog -co BIGTIFF=YES -co STATISTICS=YES

GDAL_CACHEMAX=2048 gdal_translate awc.tif awc_gdal_cog.tif -of cog -co BIGTIFF=YES
