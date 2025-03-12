"""Stitch together multiple shapefile layers into one shapefile.

This preprocessing script indexes and merges shapefiles into one layer:

    1. Get list of shapefiles to merge.
    2. Ensure all shapefiles have the same crs
    3. Ensure all shapefiles have a spatial index.
    4. Merge shapefile.
"""

import os
import geopandas
import glob
import pandas as pd

#test path
path="Z:/global-dataset-cache/Global_ExternalSources/Public/NOAA_shorelines/raw_downloads"

def merge_shapefiles(path, out_path):
    """Write a merged shapefile from a list of shapefiles.

    Args:
        path: the path to locate shapefiles for merging
        out_path: the path to where the final shapefile will be written

    Returns:
        ``None``
    """
    path = os.path.abspath(path)
    shp_list = []
    for shp in glob.glob(os.path.join(path, "*.shp")):
        shp_list.append(shp)
    print(shp_list)
    merged=[]
    for l in shp_list:
        s = geopandas.read_file(l)
        s.set_crs('4326')
        s.sindex()
        merged = pd.concat([merged,s])
    out_path = out_path + '/' + 'merged.shp'
    merged.to_file(out_path)

