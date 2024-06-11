#!/usr/bin/env sh
#
# To use this script, call with the directory containing the netCDF files as the first argument.

set -e

# The directory containing the netCDF files is $1
DIR="$1"
if [ -z "$DIR" ]; then
    echo "Please provide the directory containing the netCDF files as the first argument."
    exit 1
fi

SUFFIXES=("ssp126" "ssp585")
YEARRANGES=("1961:1990" "2040:2040" "2041:2070" "2071:2100")

for suffix in ${SUFFIXES[@]}
do
    for yearrange in ${YEARRANGES[@]}
    do
        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_pet.nc" "$yearrange" "pet"

        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_pr.nc" "$yearrange" "precip"

        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_tas.nc" "$yearrange" "tas"
    done
done



