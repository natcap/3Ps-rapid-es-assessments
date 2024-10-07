## MAKEFILE for TIFF to COG
SHELL := bash
TIF_PATHS := tif_paths.txt
DIRECTORY := $(OAK)/global-dataset-cache/Public/erodibility-k-factors/
N_WORKERS := 8
GTIFF_CREATE_OPTS := -of cog
                     -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
SETCACHE := GDAL_CACHEMAX=2048

$(TIF_PATHS):
	python3 $(ROOT_DIR)/list-geotiffs.py $(DIRECTORY) > $(TIF_PATHS)

cog.tif: $(TIF_PATHS)
	$(SETCACHE) gdal_translate -input_file_list $(TIF_PATHS) $(TIF_PATHS) $(GTIFF_CREATE_OPTS) 