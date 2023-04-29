.PHONY: download verify
DOWNLOADS := downloads
ISRIC_BASEURL :=  https://files.isric.org/soilgrids/former/2017-03-10/data
CHECKSUM_FILE = $(DOWNLOADS)/checksum.sha256.txt
ALLFILES := $(CHECKSUM_FILE) \
	        $(DOWNLOADS)/AWCh1_M_sl1_250m_ll.tif \
	        $(DOWNLOADS)/AWCh1_M_sl2_250m_ll.tif \
	        $(DOWNLOADS)/AWCh1_M_sl3_250m_ll.tif \
	        $(DOWNLOADS)/AWCh1_M_sl4_250m_ll.tif \
	        $(DOWNLOADS)/AWCh1_M_sl5_250m_ll.tif \
	        $(DOWNLOADS)/AWCh1_M_sl6_250m_ll.tif \
	        $(DOWNLOADS)/AWCh1_M_sl7_250m_ll.tif
CONTAINER := ghcr.io/natcap/devstack
CONTAINER_DIGEST := sha256:961c937a55ac8ff99219afeffe0f8509e4f142061cd3302c8133dfbe94574657

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

$(DOWNLOADS)/%: $(DOWNLOADS)
	wget --tries=20 $(ISRIC_BASEURL)/$(notdir $@) --directory-prefix=$(DOWNLOADS)

download: $(ALLFILES)

verify: $(CHECKSUM_FILE)
	cd $(DOWNLOADS) && sha265sum --check checksum.sha256.txt

awc.tif: $(ALLFILES)
	$(CONTAINER_CMD) python3 build-awc.py --cache-dir=$(DOWNLOADS) $@
