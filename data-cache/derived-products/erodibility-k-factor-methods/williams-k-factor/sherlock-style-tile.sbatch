#!/bin/bash
#
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="K_Factor_renard_style_tile"

# $OAK/global-dataset-cache/Public/erodibility-k-factors/outputs/
# is expected location for K factor rasters.
# $SCRATCH/soils is the default location in sherlock-download.sbatch
singularity run docker://ghcr.io/natcap/devstack:2023-06-21 python style_and_tile.py \
    $OAK/global-dataset-cache/Public/erodibility-k-factors/outputs/renard-k-factor.tif \
    renard-k-factor-colors.txt \
    $SCRATCH/k-factor-renard 
