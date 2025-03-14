#!/bin/bash
#
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal,serc
#SBATCH --job-name="merge rasters"
##Stitch together multiple rasters layers into one layer.
# Usage:
#  * This script assumes your rasters are in the same directory as the output directory. 
#  * Run the command as `bash build-tiles.sh`

module load physics gdal/3.5.2
module load py-gdal-utils

DIR=/oak/stanford/groups/gdaily/global-dataset-cache/Global_ExternalSources/Public/NLCD

ls -1 $DIR/*_tcc_*.tif > tiff_list.txt

GDAL_CACHEMAX=2048 gdalbuildvrt merge-vrt.vrt -input_file_list $DIR/tiff_list.txt