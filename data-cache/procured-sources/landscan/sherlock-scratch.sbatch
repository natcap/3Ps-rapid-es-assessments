#!/bin/bash
#
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal,serc
#SBATCH --job-name="LANDSCAN-processing"

set -ex

function print_now {
    echo "The time right now is $(date)"
}

run_in_container="singularity run --env GDAL_CACHEMAX=2048 ghcr.io/natcap/devstack@sha256:c011d3a6aea3f9602b986a5a2ae046e8629f098af94494dc3a3ee64649b019bb"

module load physics gdal/3.5.2
module load python/3.9.0
module load py-gdal-utils

#source data was downloaded from the following site: https://landscan.ornl.gov/
#the zip file's unzipped data was placed in the following Oak directory (in groups/gdaily)
TARGET_OAK_DIR="$OAK/global-dataset-cache/Global_ExternalSources/Public/landscan-pop/landscan-2023/"
mkdir -p "$TARGET_OAK_DIR" || echo "Directory already exists: $TARGET_OAK_DIR"

VALIDATION=/share/software/user/open/py-gdal-utils/3.4.1_py39/lib/python3.9/site-packages/osgeo_utils/samples/validate_cloud_optimized_geotiff.py

# the landscan data is already in COG format, we just need to make sure it has all the correct overview, etc
# taking examples from: https://geoexamples.com/other/2019-02-08-cog-tutorial/
$run_in_container gdal_translate -co BIGTIFF=YES -co COMPRESS=LZW -co TILED=YES "$TARGET_OAK_DIR/landscan-global-2023-assets/landscan-global-2023.tif" "$TARGET_OAK_DIR/landscan_2023_new.tif"
$run_in_container gdaladdo "$TARGET_OAK_DIR/landscan_2023_new.tif"
cogger "$TARGET_OAK_DIR/landscan_2023_new.tif"
cp "$TARGET_OAK_DIR/landscan_2023_new.tif" "$TARGET_OAK_DIR/landscan_2023.tif"

#validate COG
python3 "$VALIDATION" "$TARGET_OAK_DIR/landscan_2023.tif" >> "$TARGET_OAK_DIR/validation_check.txt"

gdalinfo "$TARGET_OAK_DIR/landscan_2023.tif"

echo "Finished building Landscan COG!"
