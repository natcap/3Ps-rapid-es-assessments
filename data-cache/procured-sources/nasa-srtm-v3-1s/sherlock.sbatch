#!/bin/bash
#
#SBATCH --time=5:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal
#SBATCH --job-name="SRTM-processing"

set -ex
TARGET_OAK_DIR=$OAK/global-dataset-cache/srtm-v3-1s

# download all the tiles from NASA
make -C $L_SCRATCH download-batch

make N_WORKERS=$SLURM_CPUS_PER_TASK -C $L_SCRATCH srtm-v3-1s.tif
cp srtm-v3-1s.tif $TARGET_OAK_DIR

# remove the tiles directory now that we don't need it.
# There's too great a chance that we'll exhaust local storage space when
# building overviews.
rm -r $L_SCRATCH/tiles
make N_WORKERS=$SLURM_CPUS_PER_TASK -C $L_SCRATCH srtm-v3-1s.tif.ovr
cp srtm-v3-1s.tif.ovr $TARGET_OAK_DIR
rm srtm-v3-1s.tif.ovr

make N_WORKERS=$SLURM_CPUS_PER_TASK -C $L_SCRATCH xyztiles
cp -r $L_SCRATCH/xyztiles $TARGET_OAK_DIR

echo "Finished building SRTM!"
