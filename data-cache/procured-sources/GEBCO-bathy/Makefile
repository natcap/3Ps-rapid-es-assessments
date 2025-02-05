SHELL := bash
GEBCO_PATH := /oak/stanford/groups/gdaily/global-dataset-cache/Public/GEBCO/raw
N_WORKERS := 8
SETCACHE := GDAL_CACHEMAX=2048

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))


ifeq (, $(shell which cogger))
	$(error "cogger is not available. Please install it from https://github.com/airbusgeo/cogger")
endif

gebco_2024.vrt:
	gdalbuildvrt $@ $(GEBCO_PATH)/*.tif

# follows general instructions from: https://geoexamples.com/other/2019-02-08-cog-tutorial/
gebco_bathymetry_2024_global.tif: gebco_2024.vrt
	$(SETCACHE) gdal_translate -of GTiff -co "TILED=YES" $< gebco_bathymetry_2024_stitch.tif
	$(SETCACHE) gdaladdo gebco_bathymetry_2024_stitch.tif
	$(SETCACHE) gdal_translate -of GTiff -strict -co COPY_SRC_OVERVIEWS=YES -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=LZW" -co "NUM_THREADS=$(N_WORKERS)" gebco_bathymetry_2024_stitch.tif $@
	cogger $@
