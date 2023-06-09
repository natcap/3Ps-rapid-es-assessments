#!/bin/bash
#
#SBATCH --time=8:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="Procure-ISRIC_SoilGRIDS"

singularity run docker://ghcr.io/natcap/devstack:latest python procure-isric-soils.py --cache-dir=$SCRATCH/ddenu/soils --soil-type=sand
