#!/bin/bash

# Simple script to convert shapefiles to mbtiles.
#
# Usage:
#  * This script assumes your shapefiles are in the directory where the shapefiles are. 
#  * Run the command as `bash build-tiles.sh`
#
# Dependencies:
#  * ogr2ogr (GDAL)
#  * tippecanoe (https://github.com/felt/tippecanoe)
#  * tile-join (included with tippecanoe)

module load physics gdal/3.5.2
module load py-gdal-utils
module load gcc/14.2.0

cd /oak/stanford/groups/gdaily/natcap-data-catalog-cache/footprint-impact-tool-data/natural_capital_footprint_asset_sample_data

GEOJSON_DIR=./geojsons
MBTILES_DIR=./mbtiles

mkdir -p $GEOJSON_DIR
mkdir -p $MBTILES_DIR

# TODO gpkg too?
for i in **/*.shp; do
echo $i
  [ -f "$i" ] && echo ${i%.*}

  # Use gdal to convert to geojson
  mkdir -p $GEOJSON_DIR/$(dirname $i)
  ogr2ogr -t_srs EPSG:4326 -f GeoJSON $GEOJSON_DIR/${i%.*}.geojson $i

  # Use tippecanoe to convert to mbtiles
  mkdir -p $MBTILES_DIR/$(dirname $i)
  tippecanoe --force -zg -o $MBTILES_DIR/${i%.*}.mbtiles --drop-densest-as-needed $GEOJSON_DIR/${i%.*}.geojson
done

# Use tile-join to merge mbtiles
#
# --overzoom is significant here since it gets the separate tiles to work on the
# same zooms
tile-join --force --overzoom -o ${PWD##*/}.mbtiles $MBTILES_DIR/**/*.mbtiles

# .mbtiles need a server to open them and serve the tiles within them.
# Alternatively, we could output to a directory of vector tiles like this:
#
#tile-join --force --overzoom -output-to-directory=./vector-tiles $MBTILES_DIR/**/*.mbtiles