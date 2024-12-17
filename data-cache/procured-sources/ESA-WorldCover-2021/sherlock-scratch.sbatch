#!/bin/bash
#
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="ESA-processing"

function print_now {
    echo "The time right now is $(date)"
}

module load physics gdal/3.5.2
module load python/3.9.0
module load py-gdal-utils

TARGET_OAK_DIR=$OAK/global-dataset-cache/Public/esa2021
mkdir -p $TARGET_OAK_DIR || echo "Directory already exists: $TARGET_OAK_DIR"

SCRATCH_DIR=$SCRATCH/esa2021
SCRATCH_TILES_DIR=$SCRATCH_DIR/tiles
mkdir $SCRATCH_DIR || echo "Dir already exists: $SCRATCH_DIR"
mkdir -p $SCRATCH_TILES_DIR || echo "Dir already exists: $SCRATCH_TILES_DIR"
scratch_make="make N_WORKERS=$SLURM_CPUS_PER_TASK -C $SCRATCH_DIR -f $(pwd)/Makefile"

VALIDATION=/share/software/user/open/py-gdal-utils/3.4.1_py39/lib/python3.9/site-packages/osgeo_utils/samples/validate_cloud_optimized_geotiff.py

#$scratch_make download-batch


$scratch_make esa.vrt
cp $SCRATCH_DIR/esa.vrt $TARGET_OAK_DIR &

$scratch_make esa2021.tif
GDAL_CACHEMAX=2048 python3 $VALIDATION $SCRATCH_DIR/esa2021.tif >> $TARGET_OAK_DIR/validation_check.txt


cp $SCRATCH_DIR/esa2021.tif $TARGET_OAK_DIR &

gdalinfo --stats $TARGET_OAK_DIR/esa2021.tif


echo "Waiting for backgrounded jobs to complete"
wait $(jobs -p)
echo "Finished building ESM!"
