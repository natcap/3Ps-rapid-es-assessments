"""Convert Link et al (2020) data to GeoTiffs.

The data from Link et al (2020) uses custom .npy files to associate source grid
cells' evapotranspiration with precipitation elsewhere on the globe.  This
results in a dense data distribution format, but requires conversion to some
other format in order to use.  This script takes in the custom basin or grid
cell format used by the datasets and writes out a geotiff.

Usage example:

    python link-et-al-2020-to-gtiff.py --dataset=./data --target=central-australia.tif --mode=grid 16653

See link-et-al-2020-to-gtiff.py --help for more information about parameters.

Paper is available at: https://essd.copernicus.org/articles/12/1897/2020/essd-12-1897-2020.pdf

The full dataset (including monthly layers, 69GB in size) can be downloaded from:
    https://hs.pangaea.de/model/WAM-2layers/Link-etal_2019/Dataset.zip
"""
import argparse
import calendar
import logging
import os

import numpy
import pygeoprocessing
from osgeo import gdal
from osgeo import osr

logging.basicConfig(level=logging.DEBUG)
gdal.DontUseExceptions()

LOGGER = logging.getLogger(os.path.basename(__file__))
TARGET_NODATA = float(numpy.finfo(numpy.float32).min)


def run(ids, et0_array_path, target_raster_path):
    """Write pixel values of evapotranspiration for the given basins or cells.

    For each ID provided, this function reads the et0 array and writes
    the et0 values to the appropriate pixels, adding to any existing values.

    Note:
        If ``ids`` represents basins, these must be internal basins and the
        ``et0_array_path`` should be the array file called
        "Basin_to_Grid_2001_2018_yr(Era_Int).npy".

        If ``ids`` represents gridcells, these must be the IDs of the
        individual grid cells, and the ``et0_array_path`` should be the array
        file called "Era_Int_2001_2018_matrix_yr.npy".


    Args:
        ids (iterable): An iterable of internal basin IDs or gridcell IDs.
        et0_array_path (str): The location of the et0 array file.
        target_raster_path (str): The path to a raster that already exists on
            disk.

    Returns:
        None.
    """
    raster = gdal.Open(target_raster_path, gdal.GA_Update)
    band = raster.GetRasterBand(1)
    target_array = numpy.full((raster.RasterYSize, raster.RasterXSize),
                              TARGET_NODATA, dtype=numpy.float32)
    _, n_cols = target_array.shape
    source_evaporation_data = numpy.load(et0_array_path)
    for source_id in ids:
        for target_pixel_id in range(source_evaporation_data.shape[0]):
            water_vol = source_evaporation_data[target_pixel_id][source_id]
            if water_vol <= 0:
                continue
            target_row = target_pixel_id // n_cols
            target_col = target_pixel_id % n_cols
            existing_value = target_array[target_row][target_col]
            if numpy.isclose(existing_value, TARGET_NODATA):
                existing_value = 0
            target_array[target_row][target_col] = existing_value + water_vol
    band.WriteArray(target_array)
    band = None
    raster = None


def convert_vector_basin_ids_to_internal(array_location, basin_ids):
    """Convert basin IDs to table IDs

    Args:
        array_location (str): The location to where the vector ID array is
            located.  This should be called "Basin IDs.npy".
        basin_ids (iterable): An iterable of string or int basin IDs, as they
            are presented in the WaterGAP vector in the "ID_final" attribute.

    Returns:
        An iterable of int internal basin IDs.
    """
    basin_ids_array = numpy.load(array_location)
    basin_ids = set(int(basin_id) for basin_id in basin_ids)
    out_set = set()
    for n, array_value in enumerate(basin_ids_array):
        array_value = int(array_value)
        if array_value in basin_ids:
            out_set.add(n)
    return out_set


def convert_cell_index_to_internal(array_location, cell_indexes):
    """Convert cell indices to table IDs.

    Args:
        array_location (str): The location to where the index ID array is
            located.  This should be called "considered_cells.npy".
        basin_ids (iterable): An iterable of string or int basin IDs, as they
            are presented in the WaterGAP vector in the "ID_final" attribute.

    Returns:
        An iterable of int internal basin IDs.
    """
    valid_gridcells_array = numpy.load(array_location)
    cell_indexes = set(cell_indexes)
    converted_indexes = set()
    for index, (row, col) in enumerate(zip(*valid_gridcells_array)):
        current_index = row*240 + col
        if current_index in cell_indexes:
            converted_indexes.add(index)
    return converted_indexes


def _convert_aoi_to_cell_index(aoi_path, sample_raster_path):
    """Convert an AOI to cell indices.

    Args:
        aoi_path (str): The path to an AOI vector.  The 1st layer of this
            vector will be rasterized and used to determine whether a pixel
            intersects the aoi.
        sample_raster_path (str): The path to the sample raster, distributed
            with the Link et al dataset.

    Returns:
        A set of flat cell indices.
    """
    source_raster_info = pygeoprocessing.get_raster_info(sample_raster_path)
    cols, rows = source_raster_info['raster_size']

    # Our sample raster is small, so OK to do everything in memory here.
    driver = gdal.GetDriverByName('MEM')
    new_raster = driver.Create('', cols, rows, 1, gdal.GDT_Byte)
    new_raster.SetProjection(source_raster_info['projection_wkt'])
    new_raster.SetGeoTransform(source_raster_info['geotransform'])

    aoi_vector = gdal.OpenEx(aoi_path)
    aoi_layer = aoi_vector.GetLayer()
    gdal.RasterizeLayer(new_raster, [1], aoi_layer, burn_values=[1])

    new_band = new_raster.GetRasterBand(1)
    raster_array = new_band.ReadAsArray()
    ids = set()
    for col in range(cols):
        for row in range(rows):
            if raster_array[row, col] == 1:
                flat_index = (row * cols) + col
                ids.add(flat_index)

    aoi_layer = None
    aoi_vector = None
    new_band = None
    new_raster = None
    return ids


def main():
    parser = argparse.ArgumentParser(
        os.path.basename(__file__), description=(
            "Extract a raster of values from Link et al (2020) based on a "
            "source of water."))
    parser.add_argument(
        '--dataset', default=os.getcwd(), help=(
            'The path to where the Link et al (2020) dataset lives on disk.'))
    parser.add_argument(
        '--target', default="where-water-lands.tif", help=(
            "The name of the file to write out, ending in '.tif'"))
    parser.add_argument(
        '--mode', default="basin", help=(
            "One of 'basin', 'grid', 'yearly-YYYY' or 'monthly-YYYY-MM'. "
            "If 'basin', the IDs provided must be basin IDs. "
            "Otherwise, the IDs provided must be grid cell IDs. "
            "If 'yearly-YYYY' or 'monthly-YYYY-MM', replace YYYY with the "
            "year of interest, and MM with the month of interest.  For "
            "Example: 'yearly-2014' or 'monthly-2014-05'."))
    parser.add_argument('ID', nargs='+', help=(
        "The ID of the basin or grid cell (depending on your mode option) "
        "of the source area, or an AOI vector."))
    parsed_args = parser.parse_args()

    # TODO: function to translate AOI to grid/basin IDs
    # TODO: should I keep the basin AND the grid IDs?


    # Create the target raster and set the SRS to WGS84.  The ASCII sample
    # raster doesn't have a spatial reference.
    sample_raster_path = os.path.join(
        parsed_args.dataset, 'Further Data', 'grid_info_for_arcmap.asc')
    pygeoprocessing.new_raster_from_base(
        sample_raster_path, parsed_args.target, gdal.GDT_Float32,
        [TARGET_NODATA])
    wgs84_srs = osr.SpatialReference()
    wgs84_srs.ImportFromEPSG(4326)
    raster = gdal.Open(parsed_args.target, gdal.GA_Update)
    raster.SetProjection(wgs84_srs.ExportToWkt())
    raster = None

    if len(parsed_args.ID) == 1:
        if os.path.exists(parsed_args.ID):
            if parsed_args.mode == 'basin':
                parser.error(
                    "The basin mode cannot be used with an AOI. "
                    "You must provide a basin ID instead.")
            raw_ids = _convert_aoi_to_cell_index(
                parsed_args.ID, sample_raster_path)
        else:
            raw_ids = int(parsed_args.ID)
    else:
        raw_ids = [int(i) for i in parsed_args.ID]

    considered_cells_array_path = os.path.join(
        parsed_args.dataset, 'Further Data', 'considered_cells.npy')
    if parsed_args.mode == 'basin':
        basin_ids_array_path = os.path.join(
            parsed_args.dataset, 'Further Data', 'Basin_IDs.npy')
        source_ids = convert_vector_basin_ids_to_internal(
            basin_ids_array_path, raw_ids)
        et0_array_path = os.path.join(
            parsed_args.dataset, 'Matrices',
            'Basin_to_grid(Era_Int_2001_2018)',
            'Basin_to_Grid_2001_2018_yr(Era_Int).npy')
    elif parsed_args.mode == 'grid':
        source_ids = convert_cell_index_to_internal(
            considered_cells_array_path, raw_ids)
        et0_array_path = os.path.join(
            parsed_args.dataset, 'Matrices',
            'Land_cell_to_grid(Era_Int_2001_2018)',
            'Era_Int_2001_2018_matrix_yr.npy')
    elif parsed_args.mode.startswith('yearly'):
        year = int(parsed_args.mode.replace('yearly-'))
        source_ids = convert_cell_index_to_internal(
            considered_cells_array_path, raw_ids)
        et0_array_path = os.path.join(
            parsed_args.dataset, 'Years', year, '.npy')
    elif parsed_args.mode.startswith('monthly'):
        source_ids = convert_cell_index_to_internal(
            considered_cells_array_path, raw_ids)
        year_month = parsed_args.mode.replace('monthly-')
        year, month = year_month.split('-')
        year = int(year)
        month_name = calendar.month_name[int(month)]
        et0_array_path = os.path.join(
            parsed_args._dataset, 'Years', year, f'{month_name}.npy')
    else:
        parser.exit(f'Could not recognize mode {parsed_args.mode}', 1)

    LOGGER.info(f"Extracting values from {parsed_args.mode}(s) "
                f"{', '.join(str(id_) for id_ in source_ids)} "
                f"to {parsed_args.target}")
    LOGGER.debug(f"Using et0 array {et0_array_path}")
    run(source_ids, et0_array_path, parsed_args.target)
    LOGGER.info(f"Complete!  Output written to {parsed_args.target}")


if __name__ == '__main__':
    main()
