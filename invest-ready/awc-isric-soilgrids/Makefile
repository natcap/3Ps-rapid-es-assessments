.PHONY: download verify
DOWNLOADS := downloads
CHECKSUM_FILE = $(DOWNLOADS)/checksum.sha256.txt
ISRIC_BASEURL :=  https://files.isric.org/soilgrids/former/2017-03-10/data
CONTAINER := ghcr.io/natcap/devstack
CONTAINER_DIGEST := sha256:961c937a55ac8ff99219afeffe0f8509e4f142061cd3302c8133dfbe94574657
WGET_ARGS := --tries=20 --random-wait --retry-connrefused --random-wait

# Use bash brace expansion here to list out all 7 layers we need from ISRIC
# Force shell to use bash to enable brace expansion.
SHELL := bash
ALLFILES := $(CHECKSUM_FILE) \
	        $(shell echo $(DOWNLOADS)/AWCh1_M_sl{1..7}_250m_ll.tif)

# To force make to use singularity: make USE_SINGULARITY=1 awc.tif
USE_SINGULARITY=0
ifeq ($(USE_SINGULARITY), 1)
	CONTAINER_CMD := singularity run docker://$(CONTAINER)@$(CONTAINER_DIGEST)
endif

ifeq ($(USE_SINGULARITY), 0)
	CONTAINER_CMD := docker run -ti -v $(shell pwd):/natcap -w /natcap $(CONTAINER)@$(CONTAINER_DIGEST)
endif

$(DOWNLOADS):
	mkdir $@

$(CHECKSUM_FILE):
	wget $(WGET_ARGS) --directory-prefix=$(DOWNLOADS) $(ISRIC_BASEURL)/$(notdir $@)

# If the raster isn't already present and verifiable, grab it.
$(DOWNLOADS)/%: $(DOWNLOADS) $(CHECKSUM_FILE)
	cd $(DOWNLOADS) \
		&& grep $(notdir $@)$$ $(notdir $(CHECKSUM_FILE)) | sha256sum --check --status \
		|| rm -f $(notdir $@); wget $(WGET_ARGS) $(ISRIC_BASEURL)/$(notdir $@)

download: $(ALLFILES)

awc.tif: $(ALLFILES)
	$(CONTAINER_CMD) python3 build-awc.py --cache-dir=$(DOWNLOADS) $@
