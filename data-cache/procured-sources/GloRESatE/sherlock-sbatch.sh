#!/bin/bash
#
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="gloresate-processing"

set -ex

function print_now {
    echo "The time right now is $(date)"
}

## This script is used to download GloRESatE (Global Rainfall Erosivity from Reanalysis and Satellite Estimates) data.
## The data is from the following paper: https://www.nature.com/articles/s41597-024-03756-5#Ack1
## The data download page is: https://zenodo.org/records/11078865
## Data was downloaded and unzipped in our gdaily/groups Oak space for internal use at "global-dataset-cache\Global_ExternalSources\Internal_Private\GLORESATE-erosivity"


## Path to download all of the data: 
download_path=https://zenodo.org/api/records/11078865/files-archive

TARGET_OAK_DIR="$OAK/global-dataset-cache/Global_ExternalSources/Public/GLORESATE-erosivity"
scratch_make="make N_WORKERS=$SLURM_CPUS_PER_TASK -C $TARGET_OAK_DIR -f $(pwd)/Makefile"

$scratch_make download-batch

# after this section, the datasets were converted to COGs in a batch using:
# https://github.com/natcap/gef-rapid-es-assessments/blob/main/scripts/tiff-to-cog-conversions/tif-to-cog.sbatch.sh
# the outputs were placed in global-dataset-cache\Global_ExternalSources\Internal_Private\GLORESATE-erosivity\COGs

$scratch_make split-bands
