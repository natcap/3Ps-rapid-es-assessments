SHELL := bash
NASAHGT_URLS_FILE := nasahgt_urls.txt
NASAHGT_PATHS := nasa_hgt_paths.txt
NASAHGT_URLS_SOURCE := https://e4ftl01.cr.usgs.gov/MEASURES/NASADEM_HGT.001/2000.02.11/
N_WORKERS := 8
GTIFF_CREATE_OPTS := -co "COMPRESS=LZW" \
					 -co "PREDICTOR=2" \
					 -co "TILED=YES" \
					 -co "SPARSE_OK=False" \
					 -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
SETCACHE := GDAL_CACHEMAX=2048

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
TILESDIR := tiles


$(NASAHGT_URLS_FILE):
	wget $(NASAHGT_URLS_SOURCE) -q -O - | grep -Po '(?<=href=")[^"]*.zip' > $(ROOT_DIR)/$(NASAHGT_URLS_FILE)

$(TILESDIR):
	mkdir $@

# Sometimes it's useful to use a single HTTP session for this
.PHONY: download-batch
download-batch: $(TILESDIR)
	cat $(ROOT_DIR)/$(NASAHGT_URLS_FILE) | parallel -j$(N_WORKERS) "wget \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--user=\"$(NASA_EARTHDATA_USERNAME)\" --password=\"$(NASA_EARTHDATA_PASSWORD)\" \
		--directory-prefix=$(TILESDIR) {}"

$(NASAHGT_PATHS):
	python3 $(ROOT_DIR)/nasa-hgt-paths.py $(TILESDIR) > $(NASAHGT_PATHS)

nasa-hgt-v1-1s.vrt:
	gdalbuildvrt $@ -input_file_list $(ROOT_DIR)/$(NASAHGT_PATHS)

nasa-hgt-v1-1s.tif: nasa-hgt-v1-1s.vrt
	$(SETCACHE) gdal_translate -ot "Int16" $(GTIFF_CREATE_OPTS) $< $@

nasa-hgt-v1-1s.tif.ovr: nasa-hgt-v1-1s.tif
	$(SETCACHE) GDAL_NUM_THREADS=$(N_WORKERS) gdaladdo \
				  --config COMPRESS_OVERVIEW LZW \
				  --config PREDICTOR_OVERVIEW 2 \
				  -r near -ro aster-v3-1s.tif

nasa-hgt-v1-1s-colorized.tif: nasa-hgt-v1-1s.tif
	$(SETCACHE) gdaldem color-relief -alpha $(GTIFF_CREATE_OPTS) nasahgt.tif $(ROOT_DIR)/colorprofile.txt $@

xyztiles: nasa-hgt-v1-1s-colorized.tif
	$(SETCACHE) gdal2tiles.py --xyz -r near --zoom=1-8 --processes=$(N_WORKERS) nasa-hgt-v1-1s-colorized.tif $@
