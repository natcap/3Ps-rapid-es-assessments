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
ALLTIFFS          := $(shell echo $(TILESDIR)/gmted2010-{mea,std,med,min,dsc,bln}{075,150,300}.tif)
ALLTILES          := $(TILESDIR)/$(shell echo {70S,50S,30S,10S,10N,30N,50N,70N}{180W,150W,120W,090W,060W,030W,000E,030E,060E,090E,120E,150E,180E}_20101117_gmted_{mea,std,med,min,dsc,bln}{075,150,300}.tif)

# For debugging.  Run `make print-VARIABLE` to see the value of a variable.
print-%:
	@echo "$* = $($*)"

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

$(TILESDIR):
	mkdir $@

$(GMTED_URLS_FILE):
	python $(ROOT_DIR)/build-tile-urls.py > $@

$(ALLTILES): $(TILESDIR) $(GMTED_URLS_FILE)
	wget --no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--directory-prefix=$(TILESDIR) \
		$(shell grep $(shell basename $@) $(GMTED_URLS_FILE))

$(ALLTIFFS):
	$(SETCACHE) gdalbuildvrt $@ \
		$(shell find $(TILESDIR) -name "*$(subst gmted2010-,,$(notdir $@))")
	$(SETCACHE) gdal_translate -ot "Int16" $(GTIFF_CREATE_OPTS) $(subst .tif,.vrt,$@) $@

.PHONY: submit
submit:
	sbatch --output=$(SCRATCH)/slurm-logfiles/slurm-%j.%x.out sherlock.sbatch
