#!/usr/bin/env sh

# Where GDrive is mounted on James' computer
GDRIVE_DEFAULT_LOC="/Users/jdouglass/Library/CloudStorage/GoogleDrive-jadoug06@stanford.edu/Shared drives/GreenFin/Pilot_Countries/Armenia/GIS_Armenia/NatCap_Armenia_DataSharing/climate_projections/GFDL-ESM4 monthly processed data"

GDRIVE_LOC=${1:-$GDRIVE_DEFAULT_LOC}

GTIFF_PATTERN="GFDL-ESM4_hist_plus*.tif"
CSV_PATTERN="*.csv"

find "$GDRIVE_LOC" -name "$GTIFF_PATTERN" -o -name "$CSV_PATTERN" > files-on-gdrive.txt
find $(pwd) -name "$GTIFF_PATTERN" -o -name "$CSV_PATTERN" > files-on-local.txt

cat files-on-local.txt | while read file
do
    file_basename="$(basename "$file")"
    target_path=$(grep "$file_basename" files-on-gdrive.txt)
    if [ -z "$target_path" ]; then
        new_file_on_gdrive="$GDRIVE_LOC/$file_basename"
    else
        new_file_on_gdrive="$target_path"
    fi

    cp -v "$file" "$new_file_on_gdrive"
done
