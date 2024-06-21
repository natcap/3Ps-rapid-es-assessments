"""Soil erodibility K Factor from ISRIC soilgrids.

Refactored from Jade Delevaux's R script.

References:

Renard, K., Foster, G., Weesies, G., McCool, D., Yoder, D., 1997.
Predicting Soil Erosion by Water: A Guide to Conservation Planning With the
Revised Universal Soil Loss Equation (RUSLE). U.S. Department of Agriculture,
Agriculture Handbook No. 703.
"""
import argparse
import logging
import os

import numpy
from osgeo import gdal
import pygeoprocessing
import taskgraph

logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'),
)
LOGGER = logging.getLogger('K-Factor-Renard')
NODATA_FLOAT32 = numpy.finfo(numpy.float32).min
gdal.SetCacheMax(2**32)

def calculate_dg(clay_path, sand_path, silt_path, dg_output_path):
    """Calculate Dg for each particle size class (clay, sand, silt).

    Calculate Dg, the geometric mean particle size for each particle size
    class (clay, silt, sand).

    fi is the corresponding particle mass fraction for each particle class in percent

    `mi` is the arithmetic mean of the diameter limits for each particle size
    class (mm) based on the USDA classification:
    The mi values for each soil particle class are:
        for clay 0.0010 mm, for silt 0.0026 mm and for sand 1.025 mm.

    Args:
        clay_path (string): path to the clay soils raster.
        sand_path (string): path to the sand soils raster.
        silt_path (string): path to the silt soils raster.
        dg_output_path (string): path for the output raster.

    Returns:
        Nothing
    """
    mi_clay = 0.0010
    mi_sand = 1.025
    mi_silt = 0.0026

    raster_paths = [clay_path, sand_path, silt_path]
    nodatas = [
        pygeoprocessing.get_raster_info(path)['nodata'][0] for path in raster_paths]

    def _calculate_dg(clay, sand, silt):
        dg = numpy.full(clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
        valid_mask = numpy.ones(clay.shape, dtype=bool)
        for array, nodata in zip([clay, sand, silt], nodatas):
            valid_mask &= (array != nodata)

        dg_clay = (clay[valid_mask] / 10)*numpy.log(mi_clay)
        dg_sand = (sand[valid_mask] / 10)*numpy.log(mi_sand)
        dg_silt = (silt[valid_mask] / 10)*numpy.log(mi_silt)

        # calculate dg
        dg[valid_mask] =  numpy.exp(0.01 * (dg_clay + dg_silt + dg_sand))

        return dg

    driver_opts = ('GTIFF', (
        'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=LZW', 'BLOCKXSIZE=256',
        'BLOCKYSIZE=256', 'PREDICTOR=3', 'NUM_THREADS=4'))
    raster_path_band = [(path, 1) for path in raster_paths]
    pygeoprocessing.geoprocessing.raster_calculator(
        raster_path_band, _calculate_dg, dg_output_path,
        gdal.GDT_Float32, float(NODATA_FLOAT32),
        raster_driver_creation_tuple=driver_opts)


def calculate_renard_k_factor(dg_path, k_factor_output_path):
    """K-factor using Renard et al. (1997).

    Args:
        dg_path (string): path to the dg raster
        k_factor_output_path (string): path for the output raster

    Returns:
        Nothing
    """
    nodata = pygeoprocessing.get_raster_info(dg_path)['nodata'][0]

    def k_factor(dg):
        k_factor = numpy.full(dg.shape, NODATA_FLOAT32, dtype=numpy.float32)
        valid_mask = (dg != nodata)

        # calculate k-factor using Renard et al. (1997)
        k_factor[valid_mask] = (
            7.594 * (0.0034 + (0.0405 * numpy.exp(-0.5 *
                        ((numpy.log(dg[valid_mask]) + 1.659) / 0.7101)**2))))
        # convert from US to metric using 0.1317
        k_factor[valid_mask] = k_factor[valid_mask] * 0.1317
        return k_factor

    driver_opts = ('GTIFF', (
        'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=LZW', 'BLOCKXSIZE=256',
        'BLOCKYSIZE=256', 'PREDICTOR=3', 'NUM_THREADS=4'))
    pygeoprocessing.geoprocessing.raster_calculator(
        [(dg_path, 1)], k_factor, k_factor_output_path,
        gdal.GDT_Float32, float(NODATA_FLOAT32),
        raster_driver_creation_tuple=driver_opts)

    pygeoprocessing.geoprocessing.build_overviews(
        k_factor_output_path, internal=False, resample_method='near',
        overwrite=True, levels='auto')


if __name__ == "__main__":
    LOGGER.info("Starting script to process K Factor from ISRIC soil grids.")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--workspace', default='soils-k-factor',
        help='directory to save outputs')
    parser.add_argument('--clay', help='path to clay raster')
    parser.add_argument('--sand', help='path to sand raster')
    parser.add_argument('--silt', help='path to silt raster')

    parsed_args = parser.parse_args()
    LOGGER.info(f"Parsed args: {parsed_args}")

    workspace_dir = os.path.abspath(parsed_args.workspace)
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
    taskgraph_dir = os.path.join(workspace_dir, 'taskgraph_cache')
    if not os.path.exists(taskgraph_dir):
        os.makedirs(taskgraph_dir)

    # set up taskgraph to spread out workload and not repeat work
    n_workers = -1
    LOGGER.info(f"TaskGraph workers: {n_workers}")
    graph = taskgraph.TaskGraph(
        taskgraph_dir, n_workers, reporting_interval=60*5)

    # import the soil grid data
    clay_raster_path = os.path.abspath(parsed_args.clay)
    sand_raster_path = os.path.abspath(parsed_args.sand)
    silt_raster_path = os.path.abspath(parsed_args.silt)

    ##### A/ Soil erodibility ######
    LOGGER.info("Set up workspace directory")
    output_dir = os.path.join(workspace_dir, 'outputs')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    LOGGER.info("Calculating DG")
    dg_output_path = os.path.join(output_dir, 'dg-result.tif')
    dg_task = graph.add_task(
        calculate_dg,
        kwargs={
            "clay_path": clay_raster_path,
            "sand_path": sand_raster_path,
            "silt_path": silt_raster_path,
            "dg_output_path": dg_output_path,
        },
        target_path_list=[dg_output_path],
        task_name='Calculate DG'
    )

    LOGGER.info("Calculating Renard K")
    renard_k_factor_path =  os.path.join(output_dir, 'renard-k-factor.tif')
    _ = graph.add_task(
        calculate_renard_k_factor,
        kwargs={
            "dg_path": dg_output_path,
            "k_factor_output_path": renard_k_factor_path,
        },
        target_path_list=[dg_output_path],
        dependent_task_list=[dg_task],
        task_name='Calculate Renard K'
    )

    graph.close()
    graph.join()

    LOGGER.info(f"Soils K factor complete.")
