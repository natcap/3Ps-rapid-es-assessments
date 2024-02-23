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

mkdir -p "$SCRATCH/gmted2010" || echo "Directory already exists"

make -j "$SLURM_CPUS_PER_TASK" -f "$SLURM_SUBMIT_DIR/Makefile" -C "$SCRATCH/gmted2010" "$1"
