#!/bin/bash
#
#SBATCH --time=5:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal,serc
#SBATCH --job-name="NOAA-bathymetry-processing-bed-reproj"

set -ex

function print_now {
    echo "The time right now is $(date)"
}

module load physics gdal/3.5.2
module load python/3.9.0

TARGET_OAK_DIR=$OAK/global-dataset-cache/Global_ExternalSources/Public/NOAA_NGDC_bathymetry
mkdir -p $TARGET_OAK_DIR || echo "Directory already exists: $TARGET_OAK_DIR"

SCRATCH_DIR=$SCRATCH/NOAA_NGDC_bathymetry_bedrock
SCRATCH_TILES_DIR=$SCRATCH_DIR/tiles
mkdir $SCRATCH_DIR || echo "Dir already exists: $SCRATCH_DIR"
mkdir -p $SCRATCH_TILES_DIR || echo "Dir already exists: $SCRATCH_TILES_DIR"
scratch_make="make N_WORKERS=$SLURM_CPUS_PER_TASK -C $SCRATCH_DIR -f $(pwd)/Makefile"

#$scratch_make download-batch

print_now
$scratch_make noaa-ngdc-bedrock-bathymetry.tif
cp $SCRATCH_DIR/noaa-ngdc-bedrock-bathymetry.tif $TARGET_OAK_DIR &