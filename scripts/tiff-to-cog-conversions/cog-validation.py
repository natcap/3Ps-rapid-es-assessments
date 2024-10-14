## This script will serve to validate the COGs created in gdal_translate

from rio_cogeo import cog_validate
from osgeo import gdal
import sys



def validate_cog(cog):

    """This function will check the validity of the newly formulated
        COG from a geoTIFF.

    Args:
        cog (path): the path to the newly generated COG file

    Returns:
        Prints whether COGs are valid per file to standard out.
    """

    is_valid, valid, errors = cog_validate(cog)

    if is_valid:
        print(cog + " " + "is Valid", sep='\n')
    else:
        print(cog + " " + "is Invalid")
        for error in errors:
            print(error, sep='\n')
    


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
    print("COG:" + " " + cog_band.GetNoDataValue())  # NoData value
    print("TIF:" + " " + tif_band.GetNoDataValue())  # NoData value

    print(cog_band.GetStatistics(0, 1)) 
    print(cog_band.GetStatistics(0, 1)) 


if __name__ == '__main__':
    validate_cog(sys.argv[1])
    compare_scale(sys.argv[1],sys.argv[2])