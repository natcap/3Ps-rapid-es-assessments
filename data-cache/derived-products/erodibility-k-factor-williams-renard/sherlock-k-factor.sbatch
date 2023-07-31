#!/bin/bash
#
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="K_Factor_ISRIC_SoilGRIDS"

# $SCRATCH/soils is expected location for downloaded raw soilgrid data
# $SCRATCH/soils is the default location in sherlock-download.sbatch
singularity run docker://ghcr.io/natcap/devstack:2023-06-21 python build_k_factor.py \
    --workspace=$SCRATCH/soils \
    --clay=$SCRATCH/soils/clay/clay_0-5cm_mean.vrt \
    --sand=$SCRATCH/soils/sand/sand_0-5cm_mean.vrt \
    --silt=$SCRATCH/soils/silt/silt_0-5cm_mean.vrt \
    --soc=$SCRATCH/soils/soc/soc_0-5cm_mean.vrt
