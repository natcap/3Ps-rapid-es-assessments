SHELL := bash
ASTER_URLS_FILE := aster30m_urls.txt
ASTER_URLS_SOURCE := https://www.opentopodata.org/datasets/$(ASTER_URLS_FILE)
BASE_URL := https://e4ftl01.cr.usgs.gov/ASTT/ASTGTM.003/2000.03.01/
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


$(ASTER_URLS_FILE):
	curl $(ASTER_URLS_SOURCE) > $(ASTER_URLS_FILE)

$(TILESDIR):
	mkdir $@

# Sometimes it's useful to use a single HTTP session for this
.PHONY: download-batch
download-batch: $(TILESDIR)
	cat $(ROOT_DIR)/$(ASTER_URLS_FILE) | parallel -j$(N_WORKERS) "wget \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--directory-prefix=$(TILESDIR) {}"

aster.vrt:
	gdalbuildvrt $@ tiles/*.hgt{,.zip}

aster-v3-1s.tif: aster.vrt
	$(SETCACHE) gdal_translate -ot "Int16" $(GTIFF_CREATE_OPTS) $< $@

aster-v3-1s.tif.ovr: aster-v3-1s.tif
	$(SETCACHE) GDAL_NUM_THREADS=$(N_WORKERS) gdaladdo \
				  --config COMPRESS_OVERVIEW LZW \
				  --config PREDICTOR_OVERVIEW 2 \
				  -r near -ro aster-v3-1s.tif

aster-v3-1s-colorized.tif: aster-v3-1s.tif
	$(SETCACHE) gdaldem color-relief -alpha $(GTIFF_CREATE_OPTS) aster-v3-1s.tif $(ROOT_DIR)/colorprofile.txt $@

xyztiles: aster-v3-1s-colorized.tif
	$(SETCACHE) gdal2tiles.py --xyz -r near --zoom=1-8 --processes=$(N_WORKERS) aster-v3-1s-colorized.tif $@
