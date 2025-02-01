#!/bin/bash
#
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal,serc
#SBATCH --job-name="LANDSCAN-processing"

function print_now {
    echo "The time right now is $(date)"
}

module load physics gdal/3.5.2
module load python/3.9.0
module load py-gdal-utils

TARGET_OAK_DIR=$OAK/global-dataset-cache/Public/landscan-pop/landscan-2023
mkdir -p $TARGET_OAK_DIR || echo "Directory already exists: $TARGET_OAK_DIR"

SCRATCH_DIR=$SCRATCH/landscan-pop
mkdir $SCRATCH_DIR || echo "Dir already exists: $SCRATCH_DIR"

VALIDATION=/share/software/user/open/py-gdal-utils/3.4.1_py39/lib/python3.9/site-packages/osgeo_utils/samples/validate_cloud_optimized_geotiff.py

GDAL_CACHEMAX=2048 gdal_translate -of GTiff -strict -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=LZW" -co "NUM_THREADS=8" $< landscan_2023_cog.tif
GDAL_CACHEMAX=2048 gdaladdo $@
cogger $@
GDAL_CACHEMAX=2048 python3 $VALIDATION $SCRATCH_DIR/landscan_2023_cog.tif >> $TARGET_OAK_DIR/validation_check.txt


cp $SCRATCH_DIR/landscan_2023_cog.tif $TARGET_OAK_DIR &

gdalinfo --stats $TARGET_OAK_DIR/landscan_2023_cog.tif


echo "Waiting for backgrounded jobs to complete"
wait $(jobs -p)
echo "Finished building Landscan COG!"
