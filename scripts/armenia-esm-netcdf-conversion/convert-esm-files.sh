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
WORKSPACE=${2:-$(pwd)}

for suffix in ${SUFFIXES[@]}
do
    for yearrange in ${YEARRANGES[@]}
    do
        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_pet.nc" "$yearrange" "pet" "$WORKSPACE"

        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_pr.nc" "$yearrange" "precip" "$WORKSPACE"
        python aggregate-rain-events-by-climate-zone.py \
            "$WORKSPACE/GFDL-ESM4_hist_plus_${suffix}_rain-events-by-cz.csv" \
            "$DIR/KG_climatezones.tif" \
            "$WORKSPACE/GFDL-ESM4_hist_plus_${suffix}_pr-$(echo $yearrange | tr : -)-*-rain-events.tif" \

        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_tas.nc" "$yearrange" "tas" "$WORKSPACE"
    done
done



