#!/bin/bash
#
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=normal,hns

set -ex

module load physics gdal
make N_WORKERS="$SLURM_SPUS_PER_TASK" OUTPUT_DIR="$1" "$2"
