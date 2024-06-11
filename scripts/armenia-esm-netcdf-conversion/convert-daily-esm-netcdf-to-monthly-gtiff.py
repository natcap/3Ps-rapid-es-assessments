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
    Arg 3: The mode of data processing to use.  This can be one of the
        following:
        - "pet": Potential evapotranspiration.  Given the range of years being
           processed, the mean monthly pixel value is written to a new raster,
           one per month.
        - "precip": Precipitation.  One output is created for each month, where
           the monthly raster represents the monthly precipitation, averaged
           over the range of years.  A second output is created representing
           the mean number of monthly rain events.  A third output is created
           that represents the mean number of rain events per pixel in that
           month.
        - "tas": Temperature.  Processing is identical to "pet".
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
gdal.UseExceptions()


# GDAL by default limits the band count to 32768, but the NetCDF files we're
# using have WAY more bands than that.
gdal.SetConfigOption('GDAL_MAX_BAND_COUNT', "100000")

# NetCDFs generally don't provide a spatial reference, so we'll assume WGS84.
SRS = osr.SpatialReference()
SRS.ImportFromEPSG(4326)
SRS_WKT = SRS.ExportToWkt()
del SRS


def read_first_last_days(ds):
    """Read the dates of the first and last dates in the dataset.

    Args:
        ds (gdal.Dataset): The dataset to read from.

    Returns:
        tuple (datetime.DateTime): The first and last dates in the dataset."""
    try:
        # The datestamps I'm getting are formatted 1850-1-1, which is not ISO-8601
        malformed_date = ds.GetMetadataItem('time#units').split(' ')[2]
        year, month, day = malformed_date.split('-')
        first_day = datetime.date(int(year), int(month), int(day))

        band_count = ds.RasterCount
        final_day = first_day + datetime.timedelta(days=band_count)
        return first_day, final_day
    finally:
        ds = None


def write_raster(ds, target_filepath, array):
    """Write out a raster to disk.

    Args:
        ds (gdal.Dataset): A dataset to copy the geotransform and projection
            from.
        target_filepath (str): The path to write the raster to.
        array (numpy.ndarray): The array to write to disk.

    Returns:
        None
    """
    driver = gdal.GetDriverByName('GTiff')
    target_ds = driver.Create(
        target_filepath, array.shape[1], array.shape[0], 1, gdal.GDT_Float32)
    source_projection = ds.GetProjection()
    if not source_projection:
        source_projection = SRS_WKT
    target_ds.SetProjection(source_projection)
    target_ds.SetGeoTransform(ds.GetGeoTransform())
    target_band = target_ds.GetRasterBand(1)
    target_band.WriteArray(array)
    LOGGER.info("Wrote out %s", target_filepath)


def _get_filepath(netcdf_filepath, years, month, suffix=None, workspace=None):
    """Generate a filename for the output raster.

    Args:
        netcdf_filepath (str): The path to the NetCDF file being processed.
        years (list): A list of years being processed.
        month (int): The month being processed.
        suffix (str): An optional suffix to add to the filename.
        workspace (str): An optional workspace to write the file to.
            If not provided, the current working directory is implied.

    Returns:
        str: The filename to write the output raster to.
    """
    basename = os.path.basename(os.path.splitext(netcdf_filepath)[0])
    years_label = f'{min(years)}-{max(years)}'
    if suffix:
        suffix = f'-{suffix}'
    else:
        suffix = ''

    filename = f'{basename}-{years_label}-{month:02d}{suffix}.tif'
    if workspace:
        filename = os.path.join(workspace, filename)
    return filename


def potential_evapotranspiration(netcdf_filepath, years, workspace):
    """Write out mean monthly potential evapotranspiration.

    Args:
        netcdf_filepath (str): The path to the NetCDF file to process.
            Pixel values represent evapotranspiration per day.
        years (list): A list of integer years to process.
        workspace (str): The directory to write the output rasters to.

    Returns:
        None
    """
    ds = gdal.Open(f'NETCDF:"{netcdf_filepath}"', gdal.GA_ReadOnly)
    first_day, last_day = read_first_last_days(ds)
    n_years = len(years)
    for monthly_array, month_index, days_in_month in (
            _get_sum_of_monthly_pixel_values_from_netcdf(
                ds, years)):
        # PET values should be the mean daily value for the month, averaged
        # across all of the years.
        monthly_array /= (n_years * days_in_month)

        target_filename = _get_filepath(netcdf_filepath, years, month_index,
                                        workspace=workspace)
        write_raster(ds, target_filename, monthly_array)


def temperature(netcdf_filepath, years, workspace):
    """Write out mean monthly temperature.

    Args:
        netcdf_filepath (str): The path to the NetCDF file to process.
        years (list): A list of integer years to process.
        workspace (str): The directory to write the output rasters to.

    Returns:
        None
    """
    # The actual calculations for temp are the same as for PET, so just use
    # that.  The netcdf file is named differently, so the outputs should be
    # distinct files.
    potential_evapotranspiration(netcdf_filepath, years, workspace)


def precipitation(netcdf_filepath, years, workspace):
    """Write out mean monthly precipitation and rain events.

    Args:
        netcdf_filepath (str): The path to the NetCDF file to process.
        years (list): A list of integer years to process.
        workspace (str): The directory to write the output rasters to.

    Returns:
        None
    """
    ds = gdal.Open(f'NETCDF:"{netcdf_filepath}"', gdal.GA_ReadOnly)
    first_day, last_day = read_first_last_days(ds)

    # Units are required to be in mm/day, so assert that.
    precip_units = ds.GetMetadataItem('pre#units')
    assert precip_units == 'mm d-1', (
        f'Unexpected precipitation units: {precip_units}. "mm d-1" '
        'required.')

    # map of {month: {year: rain_events}}
    monthly_rain_events_anywhere = collections.defaultdict(collections.Counter)
    n_years = len(years)
    for monthly_array, month_index, days_in_month in (
            _get_sum_of_monthly_pixel_values_from_netcdf(ds, years)):
        # Precip values should be the sum of daily values for the month,
        # averaged across all of the years.
        monthly_array /= n_years
        monthly_rain_events_per_pixel = numpy.zeros(
            monthly_array.shape, dtype=numpy.float32)

        target_filename = _get_filepath(netcdf_filepath, years, month_index,
                                        workspace=workspace)
        write_raster(ds, target_filename, monthly_array)

        for year in years:
            for daily_array, daily_mask in (
                    _get_daily_pixel_values_from_netcdf(
                        ds, first_day, year, month_index)):

                # Count up the rain events
                rain_events_mask = daily_array > 0.1
                if daily_array[rain_events_mask & daily_mask].size > 0:
                    monthly_rain_events_anywhere[month_index][year] += 1

                # Aggregate the number of rain events per pixel.
                monthly_rain_events_per_pixel[rain_events_mask] += 1

        # We want these pixel values to be mean rain events in a month,
        # averaged over the range of years.
        monthly_rain_events_per_pixel /= n_years
        target_filename = _get_filepath(netcdf_filepath, years, month_index,
                                        suffix='rain-events',
                                        workspace=workspace)
        write_raster(ds, target_filename, monthly_rain_events_per_pixel)

    basename = os.path.basename(os.path.splitext(netcdf_filepath)[0])
    years_label = f'{min(years)}-{max(years)}'
    rain_events_filepath = os.path.join(
        workspace, f'{basename}-monthly-rain-events-{years_label}.csv')
    LOGGER.info(f"Writing rain events table to {rain_events_filepath}")
    with open(rain_events_filepath, 'w') as rain_events:
        rain_events.write('month,events\n')
        for month_index in range(1, 13):
            n_rain_events = sum(monthly_rain_events_anywhere[
                month_index].values())
            mean_rain_events = n_rain_events / len(years)
            rain_events.write(f'{month_index},{mean_rain_events}\n')


def _get_daily_pixel_values_from_netcdf(ds, first_day, year, month):
    """Generate daily pixel values from a NetCDF file.

    Args:
        ds (gdal.Dataset): The dataset to read from.
        first_day (datetime.date): The first day of the dataset.
        year (int): The year to read from.
        month (int): The month to read from.

    Yields:
        tuple: A tuple containing the daily pixel values and a mask of valid
            pixels.
    """
    for day in range(1, calendar.monthrange(year, month)[1]+1):
        date = datetime.date(year=year, month=month, day=day)

        # GDAL bands start at 1
        band_index = (date - first_day).days + 1

        band = ds.GetRasterBand(band_index)
        nodata = band.GetNoDataValue()
        band_array = ds.GetRasterBand(band_index).ReadAsArray()
        array_mask = ~numpy.isclose(band_array, nodata)

        yield band_array, array_mask


def _get_sum_of_monthly_pixel_values_from_netcdf(ds, years):
    """Generate the sum of monthly pixel values from a NetCDF file.

    Args:
        ds (gdal.Dataset): The dataset to read from.
        years (list): A list of integer years to process.

    Yields:
        tuple: A tuple containing the sum of monthly pixel values, the month
            index, and the number of days in the month.
    """
    first_day, final_day = read_first_last_days(ds)
    LOGGER.info(f'First day: {first_day}')
    LOGGER.info(f'Layers available until {final_day}')

    # generator: yield monthly pixel values sum, days in the month
    for month in range(1, 13):
        for year in years:
            sum_of_daily_pixel_values = numpy.zeros(
                (ds.RasterYSize, ds.RasterXSize), dtype=numpy.float32)
            for band_array, array_mask in (
                        _get_daily_pixel_values_from_netcdf(
                            ds, first_day, year, month)):
                sum_of_daily_pixel_values[array_mask] += band_array[array_mask]

        yield (sum_of_daily_pixel_values,
               month, calendar.monthrange(year, month)[1])


if __name__ == '__main__':
    year_min, year_max = [int(year) for year in sys.argv[2].split(':')]
    years = list(range(year_min, year_max+1))

    mode_string = sys.argv[3].lower()
    if mode_string == 'pet':
        mode = potential_evapotranspiration
    elif mode_string == 'precip':
        mode = precipitation
    elif mode_string == 'tas':
        mode = temperature
    else:
        raise ValueError(f'Unknown mode: {mode_string}')

    try:
        workspace = sys.argv[4]
    except IndexError:
        workspace = os.getcwd()

    if not os.path.exists(workspace):
        os.makedirs(workspace)

    mode(sys.argv[1], years, workspace)
