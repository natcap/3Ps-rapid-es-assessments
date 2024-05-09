"""Read in a NetCDF file with daily data and sum it up to monthly data.

This script was built by request from Nadine to process monthly climate data
from NetCDF files that have daily pixel values starting at Jan 1, 1850.

To use this script, call with the following arguments:
    Arg 1: The absolute path to the netCDF file to process.  This file must
        have a metadata item labeled "time#units" that contains the first date
        of the of the dataset in the format "days since YYYY-MM-DD".
        Band indexes must be sequential, with the band index being days since
        the start date.
    Arg 2: The range of years to process, in the format "YYYY:YYYY".
    Arg 3: The method to use to aggregate the daily data to monthly data, in
        the format "month_method:year_method".  The method can be either "sum"
        or "mean".  The month method indicates how to to aggregate the daily
        layers to a single monthly layer.  The year method indicates how to
        aggregate the monthly layer across all the years in the range.
"""
import calendar
import collections
import datetime
import logging
import os
import sys

import numpy
from osgeo import gdal
from osgeo import osr

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


# GDAL by default limits the band count to 32768, but the NetCDF files we're
# using have WAY more bands than that in these NetCDF files.
gdal.SetConfigOption('GDAL_MAX_BAND_COUNT', "100000")

# NetCDFs generally don't provide a spatial reference, so we'll assume WGS84.
SRS = osr.SpatialReference()
SRS.ImportFromEPSG(4326)
SRS_WKT = SRS.ExportToWkt()
del SRS

# TODO: function to extract monthly data
# TODO: function to write raster

def read_first_last_days(netcdf_filepath):
    try:
        ds = gdal.Open(f'NETCDF:"{netcdf_filepath}"', gdal.GA_ReadOnly)
        # The datestamps I'm getting are formatted 1850-1-1, which is not ISO-8601
        malformed_date = ds.GetMetadataItem('time#units').split(' ')[2]
        year, month, day = malformed_date.split('-')
        first_day = datetime.date(int(year), int(month), int(day))

        band_count = ds.RasterCount
        final_day = first_day + datetime.timedelta(days=band_count)
        return first_day, final_day
    finally:
        ds = None


def main(filepath, years, month_method, year_method,
         write_rain_events_table=False):
    basename = os.path.basename(os.path.splitext(filepath)[0])
    ds = gdal.Open(f'NETCDF:"{filepath}"', gdal.GA_ReadOnly)

    # Units are required to be in mm/day, so assert that.
    if write_rain_events_table:
        precip_units = ds.GetMetadataItem('pre#units')
        assert precip_units == 'mm d-1', (
            f'Unexpected precipitation units: {precip_units}. "mm d-1" '
            'required.')

    first_day, final_day = read_first_last_days(filepath)
    LOGGER.info(f'First day: {first_day}')
    LOGGER.info(f'Layers available until {final_day}')

    # map of {month: {year: rain_events}}
    monthly_rain_events = collections.defaultdict(collections.Counter)
    years_label = f'{min(years)}-{max(years)}'
    for month in range(1, 13):
        sum_of_this_month = numpy.zeros((ds.RasterYSize, ds.RasterXSize), dtype=numpy.float32)

        for year in years:
            daily_sum_array = numpy.zeros(
                (ds.RasterYSize, ds.RasterXSize), dtype=numpy.float32)
            for day in range(1, calendar.monthrange(year, month)[1]+1):
                date = datetime.date(year=year, month=month, day=day)
                band_index = (date - first_day).days + 1  # GDAL starts bands at 1
                band = ds.GetRasterBand(band_index)
                nodata = band.GetNoDataValue()
                band_array = ds.GetRasterBand(band_index).ReadAsArray()
                array_mask = ~numpy.isclose(band_array, nodata)
                daily_sum_array[array_mask] += band_array[array_mask]

                # SWY requires that rain events only count if daily
                # precipitation exceeds 0.1mm.
                if write_rain_events_table:
                    if band_array[(band_array > 0.1) & array_mask].size > 0:
                        monthly_rain_events[month][year] += 1

            if month_method == 'mean':
                daily_sum_array /= calendar.monthrange(year, month)[1]

            sum_of_this_month += daily_sum_array
        if year_method == 'mean':
            result = sum_of_this_month / len(years)
        else:
            result = sum_of_this_month

        # Write out the calculated array to a new GeoTiff.
        driver = gdal.GetDriverByName('GTiff')
        filename = f'{basename}-{years_label}-{month:02d}.tif'
        array_min = numpy.min(result[result >= 0])
        array_max = numpy.max(result[result >= 0])
        array_mean = numpy.average(result[result >= 0])
        LOGGER.info(f"Writing out {filename} min={array_min:>14.10f}  "
                    f"max={array_max:>14.10f}  mean={array_mean:>14.10f}")
        target_ds = driver.Create(
            filename, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)
        source_projection = ds.GetProjection()
        if not source_projection:
            source_projection = SRS_WKT
        target_ds.SetProjection(source_projection)
        target_ds.SetGeoTransform(ds.GetGeoTransform())
        target_band = target_ds.GetRasterBand(1)
        target_band.WriteArray(result)

    if write_rain_events_table:
        rain_events_filepath = f'{basename}-monthly-rain-events-{years_label}.csv'
        LOGGER.info(f"Writing rain events table to {rain_events_filepath}")
        with open(rain_events_filepath, 'w') as rain_events:
            rain_events.write('month,events\n')
            for month_index in range(1, 13):
                n_rain_events = sum(monthly_rain_events[month_index].values())
                mean_rain_events = n_rain_events / len(years)
                rain_events.write(f'{month_index},{mean_rain_events}\n')


if __name__ == '__main__':
    print(sys.argv)
    years_string = sys.argv[2]
    years = [int(year) for year in years_string.split(':')]
    month_method, year_method = sys.argv[3].split(":")
    try:
        write_rain_events_table = bool(sys.argv[4])
    except IndexError:
        write_rain_events_table = False

    for method in [month_method, year_method]:
        if method not in {'sum', 'mean'}:
            raise ValueError(f'Unknown method: {method}')
    print("Month aggregation method:", month_method)
    print("Year aggregation method:", year_method)
    main(sys.argv[1], list(range(years[0], years[1]+1)), month_method,
         year_method, write_rain_events_table=write_rain_events_table)
