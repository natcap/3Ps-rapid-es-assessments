CHECKSUM_FILE = checksum.sha256.txt
ISRIC_BASEURL :=  https://files.isric.org/soilgrids/former/2017-03-10/data
WGET_ARGS := --tries=20 --random-wait --retry-connrefused --random-wait

SHELL := bash
TARGET_PREFIX := ISRIC-SoilGrids-2017-250m-
ALLFILES := $(CHECKSUM_FILE) \
			$(shell echo $(TARGET_PREFIX)AWCh1_M_sl1_250m_ll.tif{,.xml})

.PHONY: download
download: $(ALLFILES)

$(CHECKSUM_FILE):
	wget $(WGET_ARGS) -O $@ $(ISRIC_BASEURL)/$@

# If the raster isn't already present and verifiable, grab it.
%: $(CHECKSUM_FILE)
	(grep $(subst $(TARGET_PREFIX),,$@)$$ $(CHECKSUM_FILE) | sha256sum --check --status) \
	   	|| wget $(WGET_ARGS) -O $@ $(ISRIC_BASEURL)/$(subst $(TARGET_PREFIX),,$@)

.PHONY: clean
clean:
	rm -rf $(DOWNLOADS)
