#!/bin/bash
#
#SBATCH --time=5:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal,serc
#SBATCH --job-name="footprint-TIF-TO-COG"

module load physics gdal/3.5.2
module load python/3.9.0
module load py-gdal-utils

# update this path to reflect folders to search through to locate .tif files
WORKDIR=$OAK/natcap-data-catalog-cache/footprint-impact-tool-data/
N_WORKERS=8
VALIDATION=/share/software/user/open/py-gdal-utils/3.4.1_py39/lib/python3.9/site-packages/osgeo_utils/samples/validate_cloud_optimized_geotiff.py

# create list of geotiffs
python3 list-geotiffs.py $WORKDIR > tif_paths.txt

for t in $(cat tif_paths.txt); 
    do
		j=`echo $t | cut -d . -f 1`; \
        j=$j"_cog.tif"; \
        echo $t; \
        GDAL_CACHEMAX=2048 gdalinfo -stats $t; \
		GDAL_CACHEMAX=2048 gdal_translate ${t} ${j} -of cog -strict -co "BIGTIFF=YES" -co "NUM_THREADS=$N_WORKERS"; \
        GDAL_CACHEMAX=2048 python3 $VALIDATION $j >> $WORKDIR/validation_check.txt; \
		python3 scale-check.py $j $t >> $WORKDIR/scale-check.txt; \
	done