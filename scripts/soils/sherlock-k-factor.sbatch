#!/bin/bash
#
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="K_Factor_ISRIC_SoilGRIDS"

singularity run docker://ghcr.io/natcap/devstack:latest python sdr_k_factor_methods.py \
    --workspace=$SCRATCH/ddenu/soils \
    --clay=$SRATCH/ddenu/soils/clay/clay_0-5cm_mean.vrt \
    --sand=$SRATCH/ddenu/soils/sand/sand_0-5cm_mean.vrt \
    --silt=$SRATCH/ddenu/soils/silt/silt_0-5cm_mean.vrt \
    --soc=$SRATCH/ddenu/soils/soc/soc_0-5cm_mean.vrt
