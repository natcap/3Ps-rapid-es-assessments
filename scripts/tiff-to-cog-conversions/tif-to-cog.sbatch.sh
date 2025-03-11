#!/bin/bash
#
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --mail-type=ALL
#SBATCH --partition=hns,normal,serc
#SBATCH --job-name="globalcache-TIF-TO-COG"

module load physics gdal/3.5.2
module load python/3.9.0
module load py-gdal-utils

# update this path to reflect folders to search through to locate .tif files
WORKDIR=$OAK/global-dataset-cache/Global_External/Public/CIESIN_NASA_GGRDI_v1/raw_downloads
N_WORKERS=8
VALIDATION=/share/software/user/open/py-gdal-utils/3.4.1_py39/lib/python3.9/site-packages/osgeo_utils/samples/validate_cloud_optimized_geotiff.py

# create list of geotiffs
#python3 list-geotiffs.py $WORKDIR >> tif_paths.txt

for t in $(cat tif_paths.txt); 
    do
		i=`echo ${t%.*}`; \
        i=$i"_translate.tif"; \
        j=`echo ${t%.*}`; \
        j=$j"_cog.tif"; \
        echo $t; \
        echo $i; \
        echo $j; \
        if [ -f $j ]; then 
            echo "$j Already Exists"
        else
            GDAL_CACHEMAX=2048 gdal_translate -of GTiff -co "TILED=YES" -co "BIGTIFF=YES" $t $i; \
            GDAL_CACHEMAX=2048 gdaladdo $i; \
            echo "Translating $t"
		    GDAL_CACHEMAX=2048 gdal_translate ${i} ${j} -of GTiff -strict -co COPY_SRC_OVERVIEWS=YES -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=LZW" -co "NUM_THREADS=$N_WORKERS"; \
            cogger ${j}; \
            echo "Checking validity of $j"
            GDAL_CACHEMAX=2048 python3 $VALIDATION $j >> $WORKDIR/validation_check.txt; \
		    python3 scale-check.py $j $t >> $WORKDIR/scale-check.txt
        fi
	done