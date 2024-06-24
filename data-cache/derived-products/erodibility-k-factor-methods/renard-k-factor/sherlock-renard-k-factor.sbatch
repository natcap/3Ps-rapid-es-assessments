#!/bin/bash
#
#SBATCH --time=5:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="Renard_K_Factor"

# $OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/
# is expected location for downloaded raw soilgrid data.
singularity run docker://ghcr.io/natcap/devstack@sha256:0a678f8da0f174129adbfdc8c804bcf4a47310eda23799b1432bdb9e90d92ea2 \
	python3 renard_k_factor.py \
    --workspace=$SCRATCH/erodibility-k-factor/renard \
    --clay=$OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/clay/clay_0-5cm_mean.vrt \
    --sand=$OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/sand/sand_0-5cm_mean.vrt \
    --silt=$OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/silt/silt_0-5cm_mean.vrt 
