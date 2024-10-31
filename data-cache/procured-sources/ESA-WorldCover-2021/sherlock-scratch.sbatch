#!/bin/bash
#
#SBATCH --time=18:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="ESM-processing"

set -ex

function print_now {
    echo "The time right now is $(date)"
}

module load physics gdal/3.5.2
module load python/3.9.0
module load py-gdal-utils

TARGET_OAK_DIR=$OAK/global-dataset-cache/aster-v3-1s
mkdir -p $TARGET_OAK_DIR || echo "Directory already exists: $TARGET_OAK_DIR"

SCRATCH_DIR=$SCRATCH/aster-v3-1s
SCRATCH_TILES_DIR=$SCRATCH_DIR/tiles
mkdir $SCRATCH_DIR || echo "Dir already exists: $SCRATCH_DIR"
mkdir -p $SCRATCH_TILES_DIR || echo "Dir already exists: $SCRATCH_TILES_DIR"
scratch_make="make N_WORKERS=$SLURM_CPUS_PER_TASK -C $SCRATCH_DIR -f $(pwd)/Makefile"

$scratch_make download-batch

$scratch_make create-paths

print_now
$scratch_make aster-v3-1s.tif
cp $SCRATCH_DIR/aster-v3-1s.tif $TARGET_OAK_DIR &

print_now
$scratch_make aster-v3-1s.tif.ovr
cp $SCRATCH_DIR/aster-v3-1s.tif.ovr $TARGET_OAK_DIR &

print_now
$scratch_make xyztiles
print_now
cp -rv $SCRATCH_DIR/xyztiles $TARGET_OAK_DIR
print_now

echo "Waiting for backgrounded jobs to complete"
wait $(jobs -p)
echo "Finished building ASTER!"
