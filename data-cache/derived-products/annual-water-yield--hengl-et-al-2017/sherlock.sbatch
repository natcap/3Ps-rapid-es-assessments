#!/bin/bash
#
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="Build-AWC-ISRIC_SoilGRIDS"

# The ISRIC webserver is pretty unreliable, so it makes sense to try
# downloading all the files at once.
make -j 8 download

# Force the use of singularity
make USE_SINGULARITY=1 annual-water-yield--hengl-et-al-2017.tif
