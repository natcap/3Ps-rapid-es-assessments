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
import sys

path="C:\\Users\\epavia\\Downloads\\gla-canopy\\gla-canopy"
out_path="C:\\Users\\epavia\\Desktop\\natcap\\Urban_Projects\\London_InVEST\\gla-curio-canopy"
out_name="curio-gla-canopy-2km-25cm-2016"

def merge_shapefiles(path, out_path, out_name):
    """Write a merged shapefile from a list of shapefiles.

    Args:
        path: the path to locate shapefiles for merging
        out_path: the path to where the final shapefile will be written

    Returns:
        ``None``
    """
    path = os.path.abspath(path)
    shp_list = []
    for shp in glob.glob(os.path.join(path, "*.kml")):
        shp_list.append(shp)
    merged=geopandas.GeoDataFrame()
    for l in shp_list:
        print(l)
        s = geopandas.read_file(l, driver='KML')
        s.sindex
        c = s.to_crs('EPSG:4326')
        merged = pd.concat([merged,c])
    merge_final = merged.to_crs('EPSG:4326')
    out_path = out_path + '/' +  out_name + '.shp'
    merge_final.to_file(out_path)


if __name__ == '__main__':
    merge_shapefiles(sys.argv[1], sys.argv[2], sys.argv[3])