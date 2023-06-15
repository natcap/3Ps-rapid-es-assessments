#!/bin/bash
#
#SBATCH --time=5:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="SRTM-processing"

# download all the tiles from NASA
make download-batch

# build all the files we're looking for
make N_WORKERS=$SLURM_SPUS_PER_TASK -j3 xyztiles srtm-v3-1s.tif.ovr
