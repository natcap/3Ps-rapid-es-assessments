#!/bin/bash
#
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="SRTM-processing"

set -ex

module load physics gdal/3.5.2
mpdule load python/3.9.0

TARGET_OAK_DIR=$OAK/global-dataset-cache/srtm-v3-1s

lscratch_make="make N_WORKERS=$SLURM_CPUS_PER_TASK -C $L_SCRATCH -f $(pwd)/Makefile"

# download all the tiles from NASA
$lscratch_make download-batch

$lscratch_make srtm-v3-1s.tif
cp srtm-v3-1s.tif $TARGET_OAK_DIR

# remove the tiles directory now that we don't need it.
# There's too great a chance that we'll exhaust local storage space when
# building overviews.
rm -r $L_SCRATCH/tiles
$lscratch_make srtm-v3-1s.tif.ovr
cp srtm-v3-1s.tif.ovr $TARGET_OAK_DIR
rm srtm-v3-1s.tif.ovr

$lscratch_make xyztiles
cp -r $L_SCRATCH/xyztiles $TARGET_OAK_DIR

echo "Finished building SRTM!"
