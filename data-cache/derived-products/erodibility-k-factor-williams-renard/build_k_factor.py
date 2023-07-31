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
LOGGER = logging.getLogger('K-Factor')
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

    1/ K-factor was derived using Renard et al. (1997) Equation #####

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
        'BLOCKYSIZE=256', 'PREDICTOR=1', 'NUM_THREADS=4'))
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
        return k_factor

    driver_opts = ('GTIFF', (
        'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=LZW', 'BLOCKXSIZE=256',
        'BLOCKYSIZE=256', 'PREDICTOR=1', 'NUM_THREADS=4'))
    pygeoprocessing.geoprocessing.raster_calculator(
        [(dg_path, 1)], k_factor, k_factor_output_path,
        gdal.GDT_Float32, float(NODATA_FLOAT32),
        raster_driver_creation_tuple=driver_opts)

    pygeoprocessing.geoprocessing.build_overviews(
        k_factor_output_path, internal=False, resample_method='near',
        overwrite=True, levels='auto')

def calculate_williams_k_factor(
        clay_path, sand_path, silt_path, soc_path, target_path):
    """K-factor derived using Williams (1995) Equation.

    Args:
        clay_path (string): path to the clay soils raster.
        sand_path (string): path to the sand soils raster.
        silt_path (string): path to the silt soils raster.
        soc_path (string): path to the soils organic carbon raster.
        target_path (string): path for the output raster.

    Returns:
        Nothing
    """

    raster_paths = [clay_path, sand_path, silt_path, soc_path]
    nodatas = [
        pygeoprocessing.get_raster_info(path)['nodata'][0] for path in raster_paths]

    def _calculate_k_williams(clay, sand, silt, soc):
        k_factor_result = numpy.full(
            clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
        soil_keys = {'clay': clay, 'sand': sand, 'silt': silt}

        valid_mask = numpy.ones(clay.shape, dtype=bool)
        for array, nodata in zip([clay, sand, silt, soc], nodatas):
            valid_mask &= (array != nodata)

        # calculate_percent_weight
        msoils = {}
        # convert into % weight:
        # result = % soil_type content
        for key, array in soil_keys.items():
            array_result = numpy.full(
                clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
            array_result[valid_mask] = array[valid_mask] / 10
            msoils[key] = array_result

        # calculate_percent_soc
        orgc = numpy.full(clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
        # orgC = % organic carbon
        # convert soc into % organic carbon - if 10dg = 1g
        orgc[valid_mask] = (soc[valid_mask] / 0.1) / 10

        # First we calculate the input factors of k_factor
        # fcsa is a factor that gives low soil erodibility factors for soils
        # w/ high coarse-sand contents and high values for soils w/ little sand
        fclsa = numpy.full(clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
        fclsa[valid_mask] = (
            0.2 + (0.3 * numpy.exp((-0.256) * msoils['sand'][valid_mask] *
                                   (1 - (msoils['silt'][valid_mask] / 100)))))

        # fclsi is a factor that gives low soil erodibility factors for soils
        # with high clay to silt ratios
        fclsi = numpy.full(clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
        fclsi[valid_mask] = (
            msoils['silt'][valid_mask] / (msoils['clay'][valid_mask] +
            msoils['silt'][valid_mask]) * 0.3)

        # forgc is a factor that reduce soil erodibility for soils with high
        # organic carbon content
        forgc = numpy.full(clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
        forgc[valid_mask] = (
            1 - (0.0256 * orgc[valid_mask] / (
                    orgc[valid_mask] + numpy.exp(3.72 - 2.95 * orgc[valid_mask]))))

        # fhisand is a factor that reduces soil erodibility for soils with
        # extremely high sand contents
        fsand = numpy.full(clay.shape, NODATA_FLOAT32, dtype=numpy.float32)
        fsand[valid_mask] = (
            1 - (0.7 * (1 - msoils['sand'][valid_mask] / 100)) /
                ((1 - msoils['sand'][valid_mask] / 100) +
                numpy.exp(-5.51 + 22.9 * (1 - msoils['sand'][valid_mask] / 100))))

        # k_factor equation:
        k_factor_result[valid_mask] = (
            fclsa[valid_mask] * fclsi[valid_mask] * forgc[valid_mask] *
            fsand[valid_mask])
        return k_factor_result

    raster_path_band = [(path, 1) for path in raster_paths]
    driver_opts = ('GTIFF', (
        'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=LZW', 'BLOCKXSIZE=256',
        'BLOCKYSIZE=256', 'PREDICTOR=1', 'NUM_THREADS=4'))
    pygeoprocessing.geoprocessing.raster_calculator(
        raster_path_band, _calculate_k_williams, target_path,
        gdal.GDT_Float32, float(NODATA_FLOAT32),
        raster_driver_creation_tuple=driver_opts)

    pygeoprocessing.geoprocessing.build_overviews(
        target_path, internal=False, resample_method='near',
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
    parser.add_argument('--soc', help='path to soc raster')

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
    soc_raster_path = os.path.abspath(parsed_args.soc)

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

    # Align and resize datasets as it appears SOC is of different dimensions.
    # {(159243, 58034), (159246, 58034)}
    LOGGER.info("Align and resize soil data.")
    base_list = [clay_raster_path, sand_raster_path, silt_raster_path,
            soc_raster_path]
    for raster_path in base_list:
        raster_info = pygeoprocessing.get_raster_info(raster_path)
        LOGGER.info(f"{os.path.basename(raster_path)}:")
        LOGGER.info(f"Pixel size: {raster_info['pixel_size']}")
        LOGGER.info(f"Raster size: {raster_info['raster_size']}")

    raster_info = pygeoprocessing.get_raster_info(raster_path)
    target_pixel_size = raster_info['pixel_size']
    aligned_list = [f"{os.path.splitext(x)[0]}_aligned.tif" for x in base_list]
    # Taking 'union' since SOC is just missing a few rows.
    align_task = graph.add_task(
        func=pygeoprocessing.align_and_resize_raster_stack,
        args=(
            base_list, aligned_list, ['bilinear']*len(aligned_list),
            target_pixel_size, 'union'),
        kwargs={
            'raster_align_index': 0,
        },
        target_path_list=aligned_list,
        task_name='Align soil input rasters'
    )

    LOGGER.info("Calculating Williams K")
    williams_k_factor_path =  os.path.join(output_dir, 'williams-k-factor.tif')
    _ = graph.add_task(
        calculate_williams_k_factor,
        kwargs={
            "clay_path": aligned_list[0],
            "sand_path": aligned_list[1],
            "silt_path": aligned_list[2],
            "soc_path": aligned_list[3],
            "target_path": williams_k_factor_path,
        },
        target_path_list=[dg_output_path],
        dependent_task_list=[align_task],
        task_name='Calculate Williams K'
    )

    graph.close()
    graph.join()

    LOGGER.info(f"Soils K factor complete.")
