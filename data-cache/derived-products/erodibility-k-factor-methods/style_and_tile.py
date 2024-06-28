import argparse
import logging
import os
import subprocess
import sys

from osgeo import gdal

logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'),
)
LOGGER = logging.getLogger('style-and-tile')
gdal.SetCacheMax(2**32)

N_WORKERS = 8
GTIFF_CREATE_OPTS = (
    '-co "COMPRESS=LZW" '
    '-co "PREDICTOR=2" '
    '-co "TILED=YES" '
    '-co "SPARSE_OK=False" '
    '-co "BIGTIFF=YES" '
    f'-co "NUM_THREADS={N_WORKERS}" ')


def style_tile_raster(raster_path, working_dir, color_relief_path):
    """Calls ``gdaldem color-relief`` and ``gdal2tiles --xyz`` given a raster.

    Args:
        raster_path (string): path to input raster to style and tile.
        working_dir (sring): directory path to save outputs.
        color_relief_path (string): path to a color profile for styling.
        
    Returns:
        Nothing
    """
    # Set up directory and paths for outputs
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    rgb_raster_path = os.path.join(working_dir, f'{base_name}_rgb.tif')
    tile_dir = os.path.join(working_dir, f'{base_name}_tiles')

    if not os.path.isdir(tile_dir):
        os.mkdir(tile_dir)

    cache_cmd = "export GDAL_CACHEMAX=2048"
    gdaldem_cmd = f'{cache_cmd}; gdaldem color-relief {GTIFF_CREATE_OPTS} {raster_path} {color_relief_path} -alpha {rgb_raster_path}'
    LOGGER.info(f'Calling {gdaldem_cmd}')
    subprocess.call(gdaldem_cmd, shell=True)
    tile_cmd = f'{cache_cmd}; gdal2tiles.py --xyz -r near --zoom=1-8 --process={N_WORKERS} {rgb_raster_path} {tile_dir}'
    print(tile_cmd)
    LOGGER.info(f'Calling {tile_cmd}')
    subprocess.call(tile_cmd, shell=True)

if __name__ == "__main__":
    LOGGER.info("Styling and tiling rasters.")
    parser = argparse.ArgumentParser()
    parser.add_argument('input_raster', help='path to raster')
    parser.add_argument(
        'color_relief_file', help='path to a text file for the styling')
    parser.add_argument(
        'workspace', help='directory to save outputs')

    parsed_args = parser.parse_args()
    LOGGER.info(f"Parsed args: {parsed_args}")

    workspace_dir = os.path.abspath(parsed_args.workspace)
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)

    style_tile_raster(parsed_args.input_raster, workspace_dir, parsed_args.color_relief_file)
