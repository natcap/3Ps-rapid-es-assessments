"""Convert Link et al (2020) data to GeoTiffs.

The data from Link et al (2020) uses custom .npy files to associate source grid
cells' evapotranspiration with precipitation elsewhere on the globe.  This
results in a dense data distribution format, but requires conversion to some
other format in order to use.  This script takes in the custom basin or grid
cell format used by the datasets and writes out a geotiff.

Usage example:

    python link-et-al-2020-to-gtiff.py --dataset=./data --target=central-australia.tif --mode=grid 16653

See link-et-al-2020-to-gtiff.py --help for more information about parameters.
"""
import argparse
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
    target_array = numpy.full((raster.RasterYSize, raster.RasterXSize), TARGET_NODATA,
                              dtype=numpy.float32)
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
            "Either 'basin' or 'grid'.  Whether the source area is a basin or "
            "a grid cell."))
    parser.add_argument('ID', nargs='+', help=(
        "The ID of the basin or grid cell (depending on your mode option) "
        "of the source area."), type=int)
    parsed_args = parser.parse_args()

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
        raw_ids = parsed_args.ID
    else:
        raw_ids = list(parsed_args.ID)

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
        considered_cells_array_path = os.path.join(
            parsed_args.dataset, 'Further Data', 'considered_cells.npy')
        source_ids = convert_cell_index_to_internal(
            considered_cells_array_path, raw_ids)
        et0_array_path = os.path.join(
            parsed_args.dataset, 'Matrices',
            'Land_cell_to_grid(Era_Int_2001_2018)',
            'Era_Int_2001_2018_matrix_yr.npy')
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
