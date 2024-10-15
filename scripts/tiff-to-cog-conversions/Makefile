SHELL := bash
TIF_PATHS := tif_paths.txt
DIRECTORY := $(shell echo $1)
N_WORKERS := 8
GTIFF_CREATE_OPTS := -of cog \
                     -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
SETCACHE := GDAL_CACHEMAX=2048
FILES := $(shell cat ${TIF_PATHS})
COG_VALIDATION := cog_validation.txt
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

$(TIF_PATHS):
	python3 $(ROOT_DIR)/list-geotiffs.py $(DIRECTORY) > $(TIF_PATHS)

cog-translate: $(FILES)
	@for t in $(FILES); do \
		j=`echo $$t | cut -d . -f 1`; \
        j=$$j"_cog.tif"; \
        echo $$t $$j; \
		$(SETCACHE) gdal_translate $${t} $${j} $(GTIFF_CREATE_OPTS); \
		python3 cog-validation.py $$j $$t >> $(DIRECTORY)/cog_validation.txt; \
	done