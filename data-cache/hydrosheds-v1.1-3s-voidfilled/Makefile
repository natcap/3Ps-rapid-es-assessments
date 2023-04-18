.PHONY: clean download-tiles all verify-tiles

TILESDIR=tiles

dem_files.json:
	# File obtained by grokking the source code of the HTML page at
	# https://www.hydrosheds.org/hydrosheds-core-downloads
	wget https://f000.backblazeb2.com/file/hydrosheds-v1-dem/dem_files.json

tiles-download-urls.txt: dem_files.json
	 cat dem_files.json | jq '.[].a_attr.href' | sed 's|null||g' | sed 's|\"||g' > tiles-download-urls.txt

vsi-tiles.txt: tiles-download-urls.txt
	cat tiles-download-urls.txt | sed '/^\s*$$/d' | sed 's|^|/vsizip//vsicurl/|g' | sed 's/\([a-z0-9]*_dem\).zip/\1.zip\/\1.tif/g' > $@

hydrosheds-v1.1-3s-voidfilled-online.vrt: vsi-tiles.txt
	gdalbuildvrt -input_file_list vsi-tiles.txt $@

download-tiles: tiles-download-urls.txt
	wget --no-clobber --tries=20 --input-file=tiles-download-urls.txt --directory-prefix=$(TILESDIR)/
	unzip -o '$(TILESDIR)/*.zip'

tiles-checksums.sha256:
	sha256sum $(TILESDIR)/*.tif > $@

verify-tiles: tiles-checksums.sha256
	sha256sum --check tiles-checksums.sha256

local-tiles.vrt:
	find $(TILESDIR) -name "*.tif" > local-tiles.txt
	gdalbuildvrt -input_file_list local-tiles.txt $@

hydrosheds-v1.1-3s-voidfilled.tif: local-tiles.vrt
	gdal_translate -of GTiff -co TILED=YES -co COMPRESS=LZW local-tiles.vrt

hydrosheds-v1.1-3s-voidfilled.tif.ovr: hydrosheds-v1.1-3s-voidfilled.tif
	gdaladdo -ro -clean $@

all: download-tiles tiles-checksums.sha256

clean:
	rm -f dem_files.json tiles-download-urls.txt

