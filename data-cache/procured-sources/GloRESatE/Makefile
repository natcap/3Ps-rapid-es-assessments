SHELL := bash
# the urls on the list below were taken manually from: https://zenodo.org/records/11078865
DOWNLOAD_PATHS=download-paths.txt
OUT_PATH=$(OAK)/global-dataset-cache/Global_ExternalSources/Public/GLORESATE-erosivity
N_WORKERS := 8
GTIFF_CREATE_OPTS := -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
SETCACHE := GDAL_CACHEMAX=2048

RAW_DOWNLOADS := raw_downloads

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

$(RAW_DOWNLOADS):
	mkdir $(OUT_PATH)/$@

# Sometimes it's useful to use a single HTTP session for this
.PHONY: download-batch
download-batch:
	cat $(ROOT_DIR)/$(DOWNLOAD_PATHS) | parallel -j$(N_WORKERS) "wget \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--directory-prefix=$(OUT_PATH)/$(RAW_DOWNLOADS) {}"

