import argparse
import logging
import os

import numpy
import pygeoprocessing
from osgeo import gdal

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))
gdal.SetCacheMax(2**32)
NODATA_FLOAT32 = numpy.finfo(numpy.float32).min
ISRIC_2017_AWCH1_RASTERS = {
    '0cm':   'AWCh1_M_sl1_250m_ll.tif',
    '5cm':   'AWCh1_M_sl2_250m_ll.tif',
    '15cm':  'AWCh1_M_sl3_250m_ll.tif',
    '30cm':  'AWCh1_M_sl4_250m_ll.tif',
    '60cm':  'AWCh1_M_sl5_250m_ll.tif',
    '100cm': 'AWCh1_M_sl6_250m_ll.tif',
    '200cm': 'AWCh1_M_sl7_250m_ll.tif',
}


def calculate_awc(
        soil_depth_0cm_path,
        soil_depth_5cm_path,
        soil_depth_15cm_path,
        soil_depth_30cm_path,
        soil_depth_60cm_path,
        soil_depth_100cm_path,
        soil_depth_200cm_path,
        target_awc_path):
    rasters = [
        soil_depth_0cm_path,
        soil_depth_5cm_path,
        soil_depth_15cm_path,
        soil_depth_30cm_path,
        soil_depth_60cm_path,
        soil_depth_100cm_path,
        soil_depth_200cm_path,
    ]
    soils_nodata = 255
    nodatas = [
        pygeoprocessing.get_raster_info(path)['nodata'][0] for path in rasters]
    assert nodatas == [soils_nodata]*len(nodatas)

    def _calculate(soil_depth_0cm, soil_depth_5cm, soil_depth_15cm,
                   soil_depth_30cm, soil_depth_60cm, soil_depth_100cm,
                   soil_depth_200cm):
        awc = numpy.full(soil_depth_0cm.shape, NODATA_FLOAT32,
                         dtype=numpy.float32)
        valid_mask = numpy.ones(soil_depth_0cm.shape, dtype=bool)
        for array in [soil_depth_0cm, soil_depth_5cm, soil_depth_15cm,
                      soil_depth_30cm, soil_depth_60cm, soil_depth_100cm,
                      soil_depth_200cm]:
            valid_mask &= (array != soils_nodata)

        awc[valid_mask] = ((1/200) * (1/2) * (
            ((5 - 0) * (soil_depth_0cm[valid_mask] + soil_depth_5cm[valid_mask])) +
            ((15 - 5) * (soil_depth_5cm[valid_mask] + soil_depth_15cm[valid_mask])) +
            ((30 - 15) * (soil_depth_15cm[valid_mask] + soil_depth_30cm[valid_mask])) +
            ((60 - 30) * (soil_depth_30cm[valid_mask] + soil_depth_60cm[valid_mask])) +
            ((100 - 60) * (soil_depth_60cm[valid_mask] + soil_depth_100cm[valid_mask])) +
            ((200 - 100) * (soil_depth_100cm[valid_mask] + soil_depth_200cm[valid_mask])))
        ) / 100
        return awc

    # TODO: build in some warnings if the values are outside of the expected
    # range of 0-100 (or 0-1 if we've already divided by 100).
    driver_opts = ('GTIFF', (
        'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=LZW',
        'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'PREDICTOR=1', 'NUM_THREADS=4'))
    raster_paths = [(path, 1) for path in rasters]
    pygeoprocessing.geoprocessing.raster_calculator(
        raster_paths, _calculate, target_awc_path,
        gdal.GDT_Float32, float(NODATA_FLOAT32),
        raster_drive_creation_tuple=driver_opts)

    pygeoprocessing.geoprocessing.build_overviews(
        target_awc_path, internal=False, resample_method='near',
        overwrite=True, levels='auto')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache-dir', default='downloads')
    parser.add_argument('target_awc')

    parsed_args = parser.parse_args()

    cache_dir = os.path.abspath(parsed_args.cache_dir)
    if not os.path.exists(cache_dir):
        os.mkdirs(cache_dir)

    LOGGER.info(f"Looking for existing AWC rasters in {cache_dir}")

    files_not_found = []
    local_soil_rasters = []
    for soil_depth, soil_rastername in ISRIC_2017_AWCH1_RASTERS.values():
        local_file = os.path.join(cache_dir, soil_rastername)
        if not os.path.exists(local_file):
            LOGGER.warning(
                f"Soil depth {soil_depth} file not found: {local_file}")
            files_not_found.append(local_file)
        else:
            LOGGER.info(f"Using {soil_depth} file {local_file}")
            local_soil_rasters.append(local_file)

    if files_not_found:
        missing_files = "\n".join(files_not_found)
        raise AssertionError(
            "Some files were not found. "
            "Run `make download` and `make verify`.\n"
            f"Missing files:\n{missing_files}")

    LOGGER.info(f"Calculating AWC to {parsed_args.target_awc}")
    calculate_awc(*local_soil_rasters, parsed_args.target_awc)

    LOGGER.info(f"AWC complete; written to {parsed_args.target_awc}")


if __name__ == '__main__':
    main()
