#!/bin/bash
#
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="K_Factor_renard_style_tile"

# $OAK/global-dataset-cache/Public/erodibility-k-factors/williams/
# is expected location for Williams K factor rasters.
singularity run docker://ghcr.io/natcap/devstack@sha256:0a678f8da0f174129adbfdc8c804bcf4a47310eda23799b1432bdb9e90d92ea2 \
	python3 ../style_and_tile.py \
    $OAK/global-dataset-cache/Public/erodibility-k-factors/williams/williams-k-factor.tif \
    williams-k-factor-colors.txt $SCRATCH/k-factor-williams 
