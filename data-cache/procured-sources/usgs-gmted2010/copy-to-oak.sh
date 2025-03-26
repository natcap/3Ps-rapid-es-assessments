#!/usr/bin/env bash

TARGET_DIR="$OAK/global-dataset-cache/usgs-gmted2010"
mkdir -p "$TARGET_DIR" || echo "$TARGET_DIR already exists"

#cp -rv $SCRATCH/gmted2010/*.{tif,ovr,xyztiles} "$TARGET_DIR"
cp -rv $SCRATCH/gmted2010/*.xyztiles "$TARGET_DIR"