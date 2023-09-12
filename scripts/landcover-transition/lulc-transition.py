import argparse
import csv
import logging
import numpy
import os
import sys
import time

from osgeo import gdal

import pygeoprocessing

logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'),
    stream=sys.stdout)
LOGGER = logging.getLogger(__name__)


_TARGET_NODATA_INT = -1


def array_equals_nodata(array, nodata):
    """Check for the presence of ``nodata`` values in ``array``.

    The comparison supports ``numpy.nan`` and unset (``None``) nodata values.

    Args:
        array (numpy array): the array to mask for nodata values.
        nodata (number): the nodata value to check for. Supports ``numpy.nan``.

    Returns:
        A boolean numpy array with values of 1 where ``array`` is equal to
        ``nodata`` and 0 otherwise.
    """
    # If nodata is undefined, nothing matches nodata.
    if nodata is None:
        return numpy.zeros(array.shape, dtype=bool)

    # comparing an integer array against numpy.nan works correctly and is
    # faster than using numpy.isclose().
    if numpy.issubdtype(array.dtype, numpy.integer):
        return array == nodata
    return numpy.isclose(array, nodata, equal_nan=True)


def lulc_transition_matrix(
        from_raster_path, to_raster_path, transition_raster_path,
        raster_csv_path, out_csv_path):
    """Create a tabular transition matrix, transition raster and raster table.

    This function creates the following three outputs:
        Transition matrix (CSV) - a matrix with "From/To" rows and columns
            where the row keys represent the "from" raster classes, the column
            keys represent the "to" raster classes, and the values are the
            counts for how many times the transition occurs. NoData values are
            included in the row, column keys.

        Transition raster (tif) - a raster of new integer values that
            represent transitions.

            The transition raster has the following special cases:
            # nodata -> nodata - should output nodata
            # x -> x - unchanged values should output the same new class
            # x -> nodata  - should output a new class value
            # nodata -> y - should output a new class value

        Transition raster table (CSV) - an accompanying table to the transition
            raster that has two columns, "Transition Class" and "Transition".
            "Transition Class" indicates the new class given the unique
            transition which is described in the "Transition" column.

    Args:
        from_raster_path (string) - path on disk to the raster to transition
            from.
        to_raster_path (string) -  path on disk to the raster transitioned
            to.
        transition_raster_path (string) - path on disk to write the new
            transition raster.
        raster_csv_path (string) - path on disk to write the raster table that
            maps the transition path.
        out_csv_path (string) - path on disk to write the transition matrix.

    Return:
        None

    """
    from_raster_info = pygeoprocessing.get_raster_info(from_raster_path)
    to_raster_info = pygeoprocessing.get_raster_info(to_raster_path)
    from_nodata = from_raster_info['nodata'][0]
    to_nodata = to_raster_info['nodata'][0]

    # Align rasters
    from_raster_aligned_name = f'{os.path.splitext(os.path.basename(from_raster_path))[0]}_aligned.tif'
    to_raster_aligned_name = f'{os.path.splitext(os.path.basename(to_raster_path))[0]}_aligned.tif'
    aligned_from_raster_path = os.path.join(
            os.path.dirname(from_raster_path), from_raster_aligned_name)
    aligned_to_raster_path = os.path.join(
            os.path.dirname(to_raster_path), to_raster_aligned_name)

    pygeoprocessing.align_and_resize_raster_stack(
        [from_raster_path, to_raster_path],
        [aligned_from_raster_path, aligned_to_raster_path], ['near', 'near'],
        from_raster_info['pixel_size'], 'intersection')

    # Create output transition raster
    pygeoprocessing.new_raster_from_base(
        aligned_from_raster_path, transition_raster_path, gdal.GDT_Int32,
        [_TARGET_NODATA_INT])

    # Open rasters and get band for iterblocks
    from_raster = gdal.OpenEx(aligned_from_raster_path, gdal.OF_RASTER)
    from_raster_band = from_raster.GetRasterBand(1)
    to_raster = gdal.OpenEx(aligned_to_raster_path, gdal.OF_RASTER)
    to_raster_band = to_raster.GetRasterBand(1)
    transition_raster = gdal.OpenEx(transition_raster_path, gdal.OF_RASTER | gdal.GA_Update)
    transition_raster_band = transition_raster.GetRasterBand(1)

    # Set up for tracking transition csv matrix
    transition_map = {}
    from_raster_unique_values = set()
    to_raster_unique_values = set()
    # Set up for tracking transition raster information
    transition_str_dict = {}
    transition_index = 1
    unchanged_value = 0
    transition_class_key = {0: "unchanged"}

    # Info needed for logging progress
    n_cols, n_rows = from_raster_info['raster_size']
    last_log_time = time.time()
    n_pixels_processed = 0
    n_pixels_to_process = n_cols * n_rows

    for block_info, from_raster_matrix in pygeoprocessing.iterblocks((aligned_from_raster_path, 1)):
        to_raster_matrix = to_raster_band.ReadAsArray(**block_info)

        # Get unique values and add to transition count if not present
        from_raster_unique = numpy.unique(from_raster_matrix)
        to_raster_unique = numpy.unique(to_raster_matrix)
        from_raster_unique_values.update(from_raster_unique)
        to_raster_unique_values.update(to_raster_unique)

        # Mask nodata if both from_raster and to_raster are nodata
        nodata_mask = (
                array_equals_nodata( from_raster_matrix, from_nodata) &
                array_equals_nodata( to_raster_matrix, to_nodata))

        # Ensure that the transition map stays up to date with all the possible
        # transitions
        for from_value in from_raster_unique_values:
            if from_value not in transition_map:
                transition_map[from_value] = {lulc_next: 0 for lulc_next in to_raster_unique_values}
            else:
                for to_value in to_raster_unique:
                    if to_value not in transition_map[from_value]:
                        transition_map[from_value][to_value] = 0

        # Need to iterate over each pixel to know the transition
        #TODO: A lot of pixel values remain the same, so getting a mask of
        # only the changed values and iterating over those could provide
        # significant runtime improvement
        win_xsize = block_info['win_xsize']
        win_ysize = block_info['win_ysize']

        transition_array = numpy.empty(
            (win_ysize, win_xsize), dtype=numpy.int32)
        transition_array[:] = 0.0

        for row_index in range(win_ysize):
            for col_index in range(win_xsize):
                # Transition CSV lookup
                # TODO: Make sure to check NoData cases
                from_raster_value = from_raster_matrix[row_index, col_index]
                to_raster_value = to_raster_matrix[row_index, col_index]
                # We took care of adding the transition possibilities above,
                # so we can just increment by 1 here
                transition_map[from_raster_value][to_raster_value] += 1

                # Transition raster and table

                # If transition does not change, use "same" code
                code_to_use = unchanged_value
                if from_raster_value != to_raster_value:
                    code_to_use = transition_index
                    transition_str_key = f'{from_raster_value} to {to_raster_value}'
                    if transition_str_key not in transition_str_dict:
                        transition_str_dict[transition_str_key] = code_to_use
                        transition_index += 1
                    else:
                        code_to_use = transition_str_dict[transition_str_key]

                if code_to_use not in transition_class_key:
                    transition_class_key[code_to_use] = f'{from_raster_value} to {to_raster_value}'
                transition_array[row_index, col_index] = code_to_use

        transition_array[nodata_mask] = _TARGET_NODATA_INT
        transition_raster_band.WriteArray(
            transition_array, block_info['xoff'], block_info['yoff'])

        n_pixels_processed += win_xsize * win_ysize
        if time.time() - last_log_time >= 5.0:
            percent_complete = round(
                n_pixels_processed / n_pixels_to_process, 4)*100
            LOGGER.info(f'Transitions {percent_complete:.2f}% complete')
            last_log_time = time.time()

    LOGGER.info('100.0% complete')


    from_raster_band = None
    from_raster = None
    to_raster_band = None
    to_raster = None
    transition_band = None
    transition_raster = None

    # Write out transitions to CSV
    with open(out_csv_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        sorted_from_values = sorted(from_raster_unique_values)
        sorted_to_values = sorted(to_raster_unique_values)
        print(sorted_to_values)
        header = ["From/To"] + sorted_to_values
        writer.writerow(header)
        for row_key in sorted_from_values:
            row_to_write = [row_key]
            for col_key in sorted_to_values:
                row_to_write += [transition_map[row_key][col_key]]
            writer.writerow(row_to_write)

    # Write out raster table transitions to CSV
    with open(raster_csv_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        header = ["Transition Class", "Transition"]
        writer.writerow(header)
        nodata_row = ["-1 (nodata)", "nodata to nodata"]
        writer.writerow(nodata_row)
        for class_key, transition_op in transition_class_key.items():
            row_to_write = [class_key, transition_op]
            writer.writerow(row_to_write)


if __name__ == "__main__":
    # execute only if run as a script
    transition_matrix_name = 'transition_matrix_csv.csv'
    transition_raster_name = 'transition_raster.tif'
    transition_raster_table_name = 'transition_raster_table.csv'

    parser = argparse.ArgumentParser(
        description="Given two landcover rasters creates a transition matrix"
            " table and transition raster with accompanying attribute table."
            )
    parser.add_argument(
        "-f", "--from", help="Path of landcover raster before transitionm.")
    parser.add_argument(
        "-t", "--to", help="Path of landover after transition.")
    parser.add_argument(
        "-o", "--output-directory",
        help="Path to a directory to save the outputs of this script.")

    args = parser.parse_args()
    args_dict = vars(args)
    LOGGER.info(f"Command line inputs: {args_dict}")

    transition_csv_matrix_path = os.path.join(
        args_dict['output_directory'], transition_matrix_name)
    transition_raster_path = os.path.join(
        args_dict['output_directory'], transition_raster_name)
    transition_raster_table_path = os.path.join(
        args_dict['output_directory'], transition_raster_table_name)

    lulc_transition_matrix(
        args_dict['from'], args_dict['to'], transition_raster_path,
        transition_raster_table_path, transition_csv_matrix_path)

    LOGGER.info("Completed.")
