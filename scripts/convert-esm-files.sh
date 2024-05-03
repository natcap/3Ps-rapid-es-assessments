#!/usr/bin/env sh

# The directory containing the netCDF files is $1
DIR="$1"

SUFFIXES=("ssp126" "ssp585")
YEARRANGES=("1961:1990" "2040:2040" "2041:2070" "2071:2100")

for suffix in ${SUFFIXES[@]}
do
    for yearrange in ${YEARRANGES[@]}
    do
        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_pet.nc" "$yearrange" mean

        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_pr.nc" "$yearrange" mean

        python convert-daily-esm-netcdf-to-monthly-gtiff.py \
            "$DIR/GFDL-ESM4_hist_plus_${suffix}_tas.nc" "$yearrange" mean
    done
done



