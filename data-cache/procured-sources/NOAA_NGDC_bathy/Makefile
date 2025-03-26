# this line below will change depending on whether you're downloading bedrock or ice elevation
BASE_URL := https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/
N_WORKERS := 8
GTIFF_CREATE_OPTS := -co "BIGTIFF=YES" \
					 -co "NUM_THREADS=$(N_WORKERS)"
SETCACHE := GDAL_CACHEMAX=2048
# the following line should be changed depending on if we are downloading the bedrock or ice layers
TYPE := bedrock
# https://stackoverflow.com/a/2547973
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
TILESDIR := tiles

$(TILESDIR):
	mkdir $@


# Sometimes it's useful to use a single HTTP session for this
.PHONY: download-batch
download-batch: $(TILESDIR)
	wget -r -l1 -nd -np -A.tif $(BASE_URL) \
		--no-verbose --no-clobber --tries=20 --random-wait --retry-connrefused \
		--user=\"$(NASA_EARTHDATA_USERNAME)\" --password=\"$(NASA_EARTHDATA_PASSWORD)\" \
		--directory-prefix=$(TILESDIR)/$(TYPE)
# change end of previous line from bed to ice, or vice versa, depending on the tiles we are retrieving

noaa-bathy.vrt:
	gdalbuildvrt $@ tiles/$(TYPE)/*.tif

noaa-ngdc-bedrock-bathymetry.tif: noaa-bathy.vrt
	$(SETCACHE) gdal_translate -of GTiff -strict -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=LZW" -co "NUM_THREADS=$(N_WORKERS)" $< noaa-bathy_stitch.tif
	$(SETCACHE) gdaladdo noaa-bathy_stitch.tif
	$(SETCACHE) gdal_translate -a_srs EPSG:4326 -of GTiff -co COPY_SRC_OVERVIEWS=YES -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=LZW" -co "NUM_THREADS=$(N_WORKERS)" noaa-bathy_stitch.tif $@
	cogger $@