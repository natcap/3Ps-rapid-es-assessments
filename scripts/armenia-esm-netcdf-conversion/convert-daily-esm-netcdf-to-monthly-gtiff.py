"""Read in a NetCDF file with daily data and sum it up to monthly data.

This script was built by request from Nadine to process monthly climate data
from NetCDF files that have daily pixel values starting at Jan 1, 1850.
"""
import calendar
import datetime
import logging
import os
import sys

import numpy
from osgeo import gdal

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


# GDAL by default limits the band count to 32768, but the NetCDF files we're
# using have WAY more bands than that in these NetCDF files.
gdal.SetConfigOption('GDAL_MAX_BAND_COUNT', "100000")


def main(filepath, years, method):
    basename = os.path.basename(os.path.splitext(filepath)[0])
    ds = gdal.Open(f'NETCDF:"{filepath}"', gdal.GA_ReadOnly)

    # The datestamps I'm getting are formatted 1850-1-1, which is not ISO-8601
    malformed_date = ds.GetMetadataItem('time#units').split(' ')[2]
    year, month, day = malformed_date.split('-')
    first_day = datetime.date(int(year), int(month), int(day))
    LOGGER.info(f'First day: {first_day}')

    band_count = ds.RasterCount
    final_day = first_day + datetime.timedelta(days=band_count)
    LOGGER.info(f'Layers available until {final_day}')

    years_label = f'{min(years)}-{max(years)}'
    for month in range(1, 13):
        monthly_sum = numpy.zeros((ds.RasterYSize, ds.RasterXSize), dtype=numpy.float32)

        for year in years:
            # To get something working, I'm assuming that I just need to sum all the
            # bands within a month.
            sum_array = numpy.zeros(
                (ds.RasterYSize, ds.RasterXSize), dtype=numpy.float32)
            for day in range(1, calendar.monthrange(year, month)[1]+1):
                date = datetime.date(year=year, month=month, day=day)
                band_index = (date - first_day).days + 1  # GDAL starts bands at 1
                band = ds.GetRasterBand(band_index)
                nodata = band.GetNoDataValue()
                band_array = ds.GetRasterBand(band_index).ReadAsArray()
                array_mask = ~numpy.isclose(band_array, nodata)
                sum_array[array_mask] += band_array[array_mask]

        monthly_sum += sum_array
        if method == 'mean':
            result = monthly_sum / len(years)
        else:
            result = monthly_sum

        # Write out the calculated array to a new GeoTiff.
        driver = gdal.GetDriverByName('GTiff')
        filename = f'{basename}-{years_label}-{month:02d}.tif'
        LOGGER.info("Writing out %s", filename)
        target_ds = driver.Create(
            filename, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)
        target_ds.SetProjection(ds.GetProjection())
        target_ds.SetGeoTransform(ds.GetGeoTransform())
        target_band = target_ds.GetRasterBand(1)
        target_band.WriteArray(result)


if __name__ == '__main__':
    years_string = sys.argv[2]
    years = [int(year) for year in years_string.split(':')]
    method = sys.argv[3]
    if method not in {'sum', 'mean'}:
        raise ValueError(f'Unknown method: {method}')
    try:
        main(sys.argv[1], list(range(years[0], years[1]+1)), method)
    except IndexError:
        main('/Users/jdouglass/Downloads/GFDL-ESM4_hist_plus_ssp126_pet.nc')
