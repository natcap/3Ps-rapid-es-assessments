#!/bin/bash
#
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="WorldClim-processing"

function print_now {
    echo "The time right now is $(date)"
}

TARGET_OAK_DIR=$OAK/global-dataset-cache/Internal_Private/world-clim

module load physics gdal/3.5.2
module load python/3.9.0

python3 procure-precip-data.py "$OAK/global-dataset-cache/Internal_Private/world-clim"