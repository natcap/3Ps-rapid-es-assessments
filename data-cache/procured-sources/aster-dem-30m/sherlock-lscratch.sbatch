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

function print_now {
    echo "The time right now is $(date)"
}

module load physics gdal/3.5.2
module load python/3.9.0

TARGET_OAK_DIR=$OAK/global-dataset-cache/srtm-v3-1s
mkdir -p $TARGET_OAK_DIR || echo "Directory already exists: $TARGET_OAK_DIR"

lscratch_make="make N_WORKERS=$SLURM_CPUS_PER_TASK -C $L_SCRATCH -f $(pwd)/Makefile"

# download all the tiles from NASA to a directory on SCRATCH that we can use if
# something fails later on, without having to re-fetch _everything_.
SCRATCH_TILES_DIR=$SCRATCH/srtm-v3-1s/tiles
mkdir -p $SCRATCH_TILES_DIR || echo "Dir already exists: $SCRATCH_TILES_DIR"
$lscratch_make TILESDIR=$SCRATCH_TILES_DIR download-batch

# Copy tiles to L_SCRATCH for easier processing of later steps
cp -r $SCRATCH_TILES_DIR $L_SCRATCH/tiles

print_now
$lscratch_make srtm-v3-1s.tif
cp $L_SCRATCH/srtm-v3-1s.tif $TARGET_OAK_DIR

# remove the tiles directory now that we don't need it.
# There's too great a chance that we'll exhaust local storage space when
# building overviews.
print_now
rm -r $L_SCRATCH/tiles
$lscratch_make srtm-v3-1s.tif.ovr
cp $L_SCRATCH/srtm-v3-1s.tif.ovr $TARGET_OAK_DIR
rm $L_SCRATCH/srtm-v3-1s.tif.ovr

print_now
$lscratch_make xyztiles
print_now
cp -rv $L_SCRATCH/xyztiles $TARGET_OAK_DIR
print_now

echo "Finished building SRTM!"
