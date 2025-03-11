SHELL := bash
# script to get file below found here: https://github.com/phargogh/2025-02-18-download-modis-land-cover-types/tree/main
MODIS_PATHS := MCD12Q1.061-files.txt
NCF_PATHS := MCD12Q1.061-files-subset.txt
MCD_PATH := https://e4ftl01.cr.usgs.gov/MOTA/MCD12Q1.061/2023.01.01/
N_WORKERS := 8
GTIFF_CREATE_OPTS := -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
SETCACHE := GDAL_CACHEMAX=2048

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
TILESDIR := tiles
NC4DIR := directory

$(TILESDIR):
	mkdir $@

$(NC4DIR):
	mkdir $@

# use grep here to select the types of files we want to download
select-paths:
	cat $(ROOT_DIR)/$(MODIS_PATHS) | grep -e "nc4"  >> $(ROOT_DIR)/$(NCF_PATHS)

# Sometimes it's useful to use a single HTTP session for this
.PHONY: download-batch
download-batch: $(NC4DIR)
	cat $(ROOT_DIR)/$(NCF_PATHS) | parallel -j$(N_WORKERS) "wget \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--http-user=\"$(NASA_EARTHDATA_USERNAME)\" --http-password=\"$(NASA_EARTHDATA_PASSWORD)\" \
		--directory-prefix=$(NC4DIR) {}"