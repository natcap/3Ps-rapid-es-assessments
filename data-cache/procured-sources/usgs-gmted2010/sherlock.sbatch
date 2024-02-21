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

mkdir "$OUTPUT_DIR" || echo "$OUTPUT_DIR already exists"

make -j "$SLURM_CPUS_PER_TASK" OUTPUT_DIR="$OUTPUT_DIR" all
