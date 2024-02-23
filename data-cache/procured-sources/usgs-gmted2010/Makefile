TILESDIR          := tiles
GMTED_URLS_FILE   := gmted2010-urls.txt
N_WORKERS         := 8
SETCACHE          := GDAL_CACHEMAX=2048
GTIFF_CREATE_OPTS := -co "COMPRESS=LZW" \
					 -co "PREDICTOR=2" \
					 -co "TILED=YES" \
					 -co "SPARSE_OK=False" \
					 -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
ALLTIFFS          := $(shell echo gmted2010-{mea,std,med,min,dsc,bln}{075,150,300}.tif)
SBATCH_PARAMS     := --output=$(SCRATCH)/slurm-logfiles/slurm-%j.%x.out

# For debugging.  Run `make print-VARIABLE` to see the value of a variable.
print-%:
	@echo "$* = $($*)"

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

$(TILESDIR):
	mkdir $@

$(GMTED_URLS_FILE):
	python $(ROOT_DIR)/build-tile-urls.py > $@

$(ALLTIFFS): $(GMTED_URLS_FILE)
	$(SETCACHE) gdalbuildvrt $(subst .tif,.vrt,$@) $(addprefix /vsicurl/,$(shell grep $(subst gmted2010-,,$(notdir $@)) $(GMTED_URLS_FILE)))
	$(SETCACHE) gdal_translate -ot "Int16" $(GTIFF_CREATE_OPTS) $(subst .tif,.vrt,$@) $@
	$(SETCACHE) gdaladdo -ro --config COMPRESS_OVERVIEW LZW $@

.PHONY: submit all sherlock-submit
all: $(ALLTIFFS)

submit:
	for mode in mea std med min dsc bln; do \
		sbatch $(SBATCH_PARAMS) --job-name=GMTED2010-$$mode-075 --time=4:00:00 sherlock.sbatch gmted2010-$${mode}075.tif; \
		sbatch $(SBATCH_PARAMS) --job-name=GMTED2010-$$mode-150 --time=2:00:00 sherlock.sbatch gmted2010-$${mode}150.tif; \
		sbatch $(SBATCH_PARAMS) --job-name=GMTED2010-$$mode-300 --time=1:00:00 sherlock.sbatch gmted2010-$${mode}300.tif; \
	done

sherlock-submit:
	mkdir -p $(SCRATCH)/gmted2010 || echo "directory already exists"
	make -C $(SCRATCH)/gmted2010 -f $(ROOT_DIR)/Makefile submit
