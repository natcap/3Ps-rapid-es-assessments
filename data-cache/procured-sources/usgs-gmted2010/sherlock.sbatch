#!/bin/bash
#
#SBATCH --time=11:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --job-name=GMTED2010-download-and-stitch
#SBATCH --mail-type=ALL
#SBATCH --partition=normal,hns

set -ex
module load physics gdal
module load python/3.9.0
module load py-gdal-utils

mkdir -p "$SCRATCH/gmted2010" || echo "Directory already exists"

# if file does not exist, create it
# This should hopefully get around possible situation where we have multiple Makefiles overwriting this file.
if [ ! -f "$SCRATCH/gmted2010/gmted2010-urls.txt" ]; then
    make -f "$SLURM_SUBMIT_DIR/Makefile" -C "$SCRATCH/gmted2010" gmted2010-urls.txt
fi

# Quotes around $@ work as you'd hope - each parameter is quoted individually.  See https://stackoverflow.com/a/4824637/299084
# NOTE: if we want to run with "all", then specify `sbatch sherlock.sbatch all`
make -j 1 -f "$SLURM_SUBMIT_DIR/Makefile" -C "$SCRATCH/gmted2010" "$@"
