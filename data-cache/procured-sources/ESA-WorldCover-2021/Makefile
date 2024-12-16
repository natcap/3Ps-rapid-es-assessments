SHELL := bash
ESA_URLS_FILE := esa2021_urls.txt
ESA_PATHS := esa_tif_paths.txt
N_WORKERS := 8
SETCACHE := GDAL_CACHEMAX=2048

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
TILESDIR := tiles


$(TILESDIR):
	mkdir $@

# Sometimes it's useful to use a single HTTP session for this
.PHONY: download-batch
download-batch: $(TILESDIR)
	cat $(ROOT_DIR)/$(ESA_URLS_FILE) | parallel -j$(N_WORKERS) "wget \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--directory-prefix=$(TILESDIR) {}"

$(ESA_PATHS):
	python3 $(ROOT_DIR)/esa_tif_paths.py $(TILESDIR) > $(ROOT_DIR)/$(ESA_PATHS)

esa.vrt: $(ESA_PATHS)
	gdalbuildvrt $@ -input_file_list $(ROOT_DIR)/$(ESA_PATHS)

esa2021.tif: esa.vrt
	$(SETCACHE) gdal_translate -of cog -strict -co "BIGTIFF=YES" -co "NUM_THREADS=$N_WORKERS" $< $@
