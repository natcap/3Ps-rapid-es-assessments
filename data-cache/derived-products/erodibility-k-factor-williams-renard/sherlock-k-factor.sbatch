#!/bin/bash
#
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="K_Factor_ISRIC_SoilGRIDS"

singularity run docker://ghcr.io/natcap/devstack:2023-06-21 python build_k_factor.py \
    --workspace=$SCRATCH/ddenu/soils \
    --clay=$SCRATCH/ddenu/soils/clay/clay_0-5cm_mean.vrt \
    --sand=$SCRATCH/ddenu/soils/sand/sand_0-5cm_mean.vrt \
    --silt=$SCRATCH/ddenu/soils/silt/silt_0-5cm_mean.vrt \
    --soc=$SCRATCH/ddenu/soils/soc/soc_0-5cm_mean.vrt
