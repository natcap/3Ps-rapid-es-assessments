# This script will serve to search through the catalog folders on Oak and
# create a list of geoTIFFS for conversion to COGS
import os
import glob
import sys


def extract_paths(tif_dir):

    """Create txt file listing all *.tif paths to feed into gdal_translate.
       This will serve as a way to search the Oak catalog cache to find the
       paths for geoTIFFS to convert them to COGs.

    Args:
        tiles_dir (path): the path to the Oak catalog cache directories.

    Returns:
        Prints a list of all catalog geotiff files to standard out.
    """

    tif_dir = os.path.abspath(tif_dir)
    tiffiles = []
    for tif in glob.glob(os.path.join(tif_dir, "**\\*.tif")):
        tiffiles.append(tif)

    print(*tiffiles, sep='\n')


if __name__ == '__main__':
    extract_paths(sys.argv[1])
