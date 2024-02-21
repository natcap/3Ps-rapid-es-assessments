DIGEST	          := sha256:54066e72aa135deb8e2f60fda2f42f1856912e36967446659ad754b4b64d7efa
CONTAINER         := ghcr.io/natcap/devstack
OUTPUT_DIR	      := .
TILESDIR          := $(OUTPUT_DIR)/tiles
GMTED_URLS_FILE   := $(OUTPUT_DIR)/gmted2010-urls.txt
N_WORKERS         := 8
SETCACHE          := GDAL_CACHEMAX=2048
GTIFF_CREATE_OPTS := -co "COMPRESS=LZW" \
					 -co "PREDICTOR=2" \
					 -co "TILED=YES" \
					 -co "SPARSE_OK=False" \
					 -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

$(TILESDIR):
	mkdir $@

$(GMTED_URLS_FILE):
	python build-tile-urls.py > $@

.PHONY: download-batch submit
download-batch: $(TILESDIR) $(GMTED_URLS_FILE)
	cat $(ROOT_DIR)/$(GMTED_URLS_FILE) | parallel -j$(N_WORKERS) "wget \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--directory-prefix=$(TILESDIR) {}"

$(OUTPUT_DIR)/gmted2010-%.tif:
	$(SETCACHE) gdal_translate -ot "Int16" $(GTIFF_CREATE_OPTS) $(subst .tif,.vrt,$@) $@

submit:
	sbatch --output=$(SCRATCH)/slurm-logfiles/slurm-%j.%x.out sherlock.sbatch
