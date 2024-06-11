#!/usr/bin/env sh

set -e  # This should cause things to fail if any command fails, like if a file is missing from GDrive.

# Where GDrive is mounted on James' computer
GDRIVE_DEFAULT_LOC="/Users/jdouglass/Library/CloudStorage/GoogleDrive-jadoug06@stanford.edu/Shared drives/GEF_GreenFin/Pilot_Countries/Armenia/GIS_Armenia/NatCap_Armenia_DataSharing/climate_projections/GFDL-ESM4 monthly processed data"

GDRIVE_LOC=${1:-$GDRIVE_DEFAULT_LOC}

find "$GDRIVE_LOC" -name "GFDL-ESM4_hist_plus*.tif" -o "*.csv"> files-on-gdrive.txt

for file in $(find . -name "$FILE_PATTERN")
do
    # If the file already exists on GDrive, copy it there. Otherwise, copy it to the GDrive root.
    cp -v "$(pwd)/$file" "$(grep $file files-on-gdrive.txt || echo $GRIVE_LOC/$file)"
done
