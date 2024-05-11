TILESDIR          := tiles
GMTED_URLS_FILE   := gmted2010-urls.txt
ifdef SLURM_CPUS_PER_TASK
	N_WORKERS := $(SLURM_CPUS_PER_TASK)
else
	N_WORKERS := 1
endif
SETCACHE          := GDAL_CACHEMAX=2048
GTIFF_CREATE_OPTS := -co "COMPRESS=LZW" \
					 -co "PREDICTOR=2" \
					 -co "TILED=YES" \
					 -co "SPARSE_OK=False" \
					 -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
ALLTIFFS          := $(shell echo gmted2010-{mea,std,med,min,dsc,bln,max}{075,150,300}.tif)
ALLVRTS           := $(subst .tif,.vrt,$(ALLTIFFS))
ALLOVERVIEWS      := $(addsuffix .ovr,$(ALLTIFFS))
ALLCOLORIZED      := $(subst .tif,-colorized.tif,$ALLTIFFS)
ALLXYZTILES       := $(subst .tif,.xyztiles,$(ALLTIFFS))
SBATCH_PARAMS     := --output=$(SCRATCH)/slurm-logfiles/slurm-%j.%x.out

# For debugging.  Run `make print-VARIABLE` to see the value of a variable.
print-%:
	@echo "$* = $($*)"

# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

$(TILESDIR):
	mkdir $@

$(GMTED_URLS_FILE):
	python3 $(ROOT_DIR)/build-tile-urls.py > $@

gmted2010-%.vrt: $(GMTED_URLS_FILE)
	$(SETCACHE) gdalbuildvrt $@ $(addprefix /vsicurl/,$(shell grep $(subst gmted2010-,,$(notdir $(subst .vrt,.tif,$@))) $(GMTED_URLS_FILE)))

gmted2010-%.tif: gmted2010-%.vrt
	$(SETCACHE) gdal_translate -ot "Int16" $(GTIFF_CREATE_OPTS) $< $@

gmted2010-%.tif.ovr: gmted2010-%.tif
	$(SETCACHE) gdaladdo -ro --config COMPRESS_OVERVIEW LZW $<

gmted2010-%-colorized.tif: gmted2010-%.tif
	$(SETCACHE) gdaldem color-relief -alpha $(GTIFF_CREATE_OPTS) $@ $(ROOT_DIR)/colorprofile.txt $<

gmted2010-%.xyztiles: gmted2010-%-colorized.tif
	$(SETCACHE) gdal2tiles.py --xyz -r near --zoom=1-8 --processes=$(N_WORKERS) $(subst .xyztiles,-colorized.tif,$@) $@

.PHONY: submit all sherlock-submit
all: $(ALLTIFFS) $(ALLVRTS) $(ALLOVERVIEWS) $(ALLCOLORIZED) $(ALLXYZTILES)

alltiffs: $(ALLTIFFS)

allvrts: $(ALLVRTS)

alloverviews: $(ALLOVERVIEWS)

allcolorized: $(ALLCOLORIZED)

allxyztiles: $(ALLXYZTILES)

submit:
	for mode in mea std med min dsc bln; do \
		sbatch $(SBATCH_PARAMS) --job-name=GMTED2010-$$mode-075 --time=4:00:00 $(ROOT_DIR)/sherlock.sbatch $(shell gmted2010-$${mode}075.tif{,.ovr,.xyztiles}); \
		sleep 1; \
		sbatch $(SBATCH_PARAMS) --job-name=GMTED2010-$$mode-150 --time=2:00:00 $(ROOT_DIR)/sherlock.sbatch $(shell gmted2010-$${mode}150.tif{,.ovr,.xyztiles}); \
		sleep 1; \
		sbatch $(SBATCH_PARAMS) --job-name=GMTED2010-$$mode-300 --time=1:00:00 $(ROOT_DIR)/sherlock.sbatch $(shell gmted2010-$${mode}300.tif{,.ovr,.xyztiles}); \
		sleep 1; \
	done

sherlock-submit:
	mkdir -p $(SCRATCH)/gmted2010 || echo "directory already exists"
	make submit
