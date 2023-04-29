#!/bin/bash
#
#SBATCH --time=5:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jdouglass@stanford.edu
#SBATCH --partition=hns,normal
#SBATCH --job-name="Build-AWC-ISRIC_SoilGRIDS"
#SBATCH --output=/scratch/users/jadoug06/slurm-logfiles/slurm-%j.%x.out

# The ISRIC webserver is pretty unreliable, so it makes sense to try
# downloading all the files at once.
make -j 8 download
make verify
make awc.tif
