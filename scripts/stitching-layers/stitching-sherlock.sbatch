#!/bin/bash
#
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal,serc
#SBATCH --job-name="stitch-shapefile"

module load python/3.9.0

SHP_PATH=/oak/stanford/groups/gdaily/global-dataset-cache/Global_ExternalSources/Public/NOAA_shorelines/raw_downloads/
OUT_PATH=/oak/stanford/groups/gdaily/global-dataset-cache/Global_ExternalSources/Public/NOAA_shorelines

python3 stitch-shapefiles.py $SHP_PATH $OUT_PATH