## This script will serve to validate the COGs created in gdal_translate
from osgeo import gdal
import sys


def compare_scale(cog, tif):
    """This function will check whether the statistics are the same
        between the geoTIFF and COG file.

    Args:
        cog (path): the path to the newly generated COG file
        tif (path): the path to the original TIFF file 

    Returns:
        Prints the file statistics to standard out.
    """

    cog_file = gdal.Open(cog)
    tif_file = gdal.Open(tif)

    cog_band = cog_file.GetRasterBand(1)
    tif_band = tif_file.GetRasterBand(1)

    assert cog_band.GetNoDataValue() == tif_band.GetNoDataValue(), "NoData does not match for {cog}"

    assert cog_band.GetStatistics(0, 1) == cog_band.GetStatistics(0, 1), "Scales do not match for {cog}"

if __name__ == '__main__':
    compare_scale(sys.argv[1], sys.argv[2])