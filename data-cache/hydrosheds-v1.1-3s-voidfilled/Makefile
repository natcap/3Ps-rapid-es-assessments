.PHONY: clean download-tiles all

TILESDIR=tiles

dem_files.json:
	# File obtained by grokking the source code of the HTML page at
	# https://www.hydrosheds.org/hydrosheds-core-downloads
	wget https://f000.backblazeb2.com/file/hydrosheds-v1-dem/dem_files.json

tiles-download-urls.txt: dem_files.json
	 cat dem_files.json | jq '.[].a_attr.href' | sed 's|null||g' | sed 's|\"||g' > tiles-download-urls.txt

download-tiles: tiles-download-urls.txt
	wget --no-clobber --tries=20 --input-file=tiles-download-urls.txt --directory-prefix=$(TILESDIR)/
	unzip -o $(TILESDIR)/*.zip

tiles-checksums.sha256:
	sha256sum $(TILESDIR)/*.tif > tiles-checksums.sha256

verify-tiles: tiles-checksums.sha256
	sha256sum --check tiles-checksums.sha256

tiles.vrt:
	gdalbuildvrt $(TILESDIR)/*.tif

all: download-tiles tiles-checksums.sha256

clean:
	rm -f dem_files.json tiles-download-urls.txt

