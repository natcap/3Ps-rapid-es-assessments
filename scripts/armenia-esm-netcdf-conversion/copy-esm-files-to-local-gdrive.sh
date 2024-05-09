#!/usr/bin/env sh

set -e  # This should cause things to fail if any command fails, like if a file is missing from GDrive.

# Where GDrive is mounted on James' computer
GDRIVE_DEFAULT_LOC="/Users/jdouglass/Library/CloudStorage/GoogleDrive-jadoug06@stanford.edu/Shared drives/GEF_GreenFin/Pilot_Countries/Armenia/GIS_Armenia/NatCap_Armenia_DataSharing/climate_projections/GFDL-ESM4 monthly processed data"

GDRIVE_LOC=${1:-$GDRIVE_DEFAULT_LOC}
FILE_PATTERN="GFDL-ESM4_hist_plus*.tif"

# This assumes that all files already exist on gdrive.
find "$GDRIVE_LOC" -name "$FILE_PATTERN" > files-on-gdrive.txt

for file in $(find . -name "$FILE_PATTERN")
do
    cp -v "$(pwd)/$file" "$(grep $file files-on-gdrive.txt)"
done
