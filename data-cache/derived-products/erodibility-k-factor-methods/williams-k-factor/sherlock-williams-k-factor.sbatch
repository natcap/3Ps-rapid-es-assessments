#!/bin/bash
#
#SBATCH --time=7:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="Williams_K_Factor"

module load physics gdal/3.5.2
module load python/3.12.1
module load py-gdal-utils

# $OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/
# is expected location for downloaded raw soilgrid data.
singularity run docker://ghcr.io/natcap/devstack:2023-06-21 python3 williams_k_factor.py \
    --workspace=$SCRATCH/erodibility-k-factor/williams \
    --clay=$OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/clay/clay_0-5cm_mean.vrt \
    --sand=$OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/sand/sand_0-5cm_mean.vrt \
    --silt=$OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/silt/silt_0-5cm_mean.vrt \
    --soc=$OAK/global-dataset-cache/Public/erodibility-k-factors/downloads/soc/soc_0-5cm_mean.vrt 
