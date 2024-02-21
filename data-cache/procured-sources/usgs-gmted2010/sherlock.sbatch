#!/bin/bash
#
#SBATCH --time=8:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --job-name=GMTED2010-download-and-stitch
#SBATCH --mail-type=ALL
#SBATCH --partition=normal,hns

set -ex
module load physics gdal

OUTPUT_DIR=$SCRATCH/gmted2010

mkdir $OUTPUT_DIR || echo "$OUTPUT_DIR already exists"
pushd $OUTPUT_DIR
make download-batch

LAYERS=("mea" "std" "med" "min" "dsc" "bln")
RESOLUTIONS=("075" "150" "300")

for layer in "${LAYERS[@]}"; do
    for resolution in "${RESOLUTIONS[@]}"; do
        gdalbuildvrt "gmted2010-${layer}-${resolution}.vrt" "tiles/*_${layer}${resolution}.tif"
        sbatch --job-name="GMTED2010-create-${layer}-${resolution}" sherlock-create-single-gtiff.sbatch
    done
done
