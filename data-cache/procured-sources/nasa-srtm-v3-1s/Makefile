SHELL := bash
SRTM_URLS_FILE := srtm30m_urls.txt
SRTM_URLS_SOURCE := https://www.opentopodata.org/datasets/$(SRTM_URLS_FILE)
BASE_URL := https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/
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


$(SRTM_URLS_FILE):
	curl $(SRTM_URLS_SOURCE) > $(SRTM_URLS_FILE)

$(TILESDIR):
	mkdir $@

# Sometimes it's useful to use a single HTTP session for this
.PHONY: download-batch
download-batch: $(TILESDIR)
	cat $(ROOT_DIR)/$(SRTM_URLS_FILE) | parallel -j$(N_WORKERS) "wget \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--user=\"$(NASA_EARTHDATA_USERNAME)\" --password=\"$(NASA_EARTHDATA_PASSWORD)\" \
		--directory-prefix=$(TILESDIR) {}"
	python3 $(ROOT_DIR)/clean-srtm-tiles.py $(TILESDIR)

srtm.vrt:
	gdalbuildvrt $@ tiles/*.hgt{,.zip}

srtm-v3-1s.tif: srtm.vrt
	$(SETCACHE) gdal_translate -ot "Int16" $(GTIFF_CREATE_OPTS) $< $@

srtm-v3-1s.tif.ovr: srtm-v3-1s.tif
	$(SETCACHE) GDAL_NUM_THREADS=$(N_WORKERS) gdaladdo \
				  --config COMPRESS_OVERVIEW LZW \
				  --config PREDICTOR_OVERVIEW 2 \
				  -r near -ro srtm-v3-1s.tif

srtm-v3-1s-colorized.tif: srtm-v3-1s.tif
	$(SETCACHE) gdaldem color-relief -alpha $(GTIFF_CREATE_OPTS) srtm-v3-1s.tif $(ROOT_DIR)/colorprofile.txt $@

xyztiles: srtm-v3-1s-colorized.tif
	$(SETCACHE) gdal2tiles.py --xyz -r near --zoom=1-8 --processes=$(N_WORKERS) srtm-v3-1s-colorized.tif $@
