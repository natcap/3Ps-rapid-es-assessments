#!/bin/bash

##Stitch together multiple rasters layers into one layer.
# Usage:
#  * This script assumes your rasters are in the same directory as the output directory. 
#  * Run the command as `bash build-tiles.sh`

module load physics gdal/3.5.2
module load py-gdal-utils

cd /oak/stanford/groups/gdaily/global-dataset-cache/Global_ExternalSources/Public/NLCD/

ls -1 *_tcc_*.tif > tiff_list.txt

gdal_merge -o nlcd_tcc_US_2021_v2021-4.tif --optfile tiff_list.txt
