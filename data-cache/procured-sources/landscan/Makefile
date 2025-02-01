SHELL := bash
GEOTIFF := landscan-global-2023-assets/landscan-global-2023.tif
N_WORKERS := 8
SETCACHE := GDAL_CACHEMAX=2048

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

ifeq (, $(shell which cogger))
	$(error "cogger is not available. Please install it from https://github.com/airbusgeo/cogger")
endif

# data was downloaded from the following url: https://landscan.ornl.gov/
# data was unzipped and added to oak (global-dataset-cache/Public/landscan-pop)

landscan_2023_cog.tif:
	$(SETCACHE) gdal_translate -of GTiff -strict -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=LZW" -co "NUM_THREADS=$(N_WORKERS)" $</$(GEOTIFF) $@
	$(SETCACHE) gdaladdo $@
	cogger $@
