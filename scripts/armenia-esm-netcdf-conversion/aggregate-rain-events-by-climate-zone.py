import calendar
import collections
import glob
import logging
import os
import shutil
import sys
import tempfile

import numpy
import pygeoprocessing
from osgeo import gdal
from osgeo import osr

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))
gdal.UseExceptions()

MONTH_NAMES = [calendar.month_name[i][:3].lower() for i in range(1, 13)]


def main(target_csv, climate_zones_raster, monthly_rain_events_rasters,
         temp_workspace=None, remove_workspace=True):
    # create temp workspace in usual place
    if temp_workspace is None:
        temp_workspace = tempfile.mkdtemp(prefix="rain-events-agg-by-cz")
    else:
        if not os.path.exists(temp_workspace):
            os.makedirs(temp_workspace)

    assert len(monthly_rain_events_rasters) == 12, (
        "Must have 12 monthly rain events rasters, not %s. Check the glob." %
        len(monthly_rain_events_rasters))

    aligned_climate_zones_raster = os.path.join(
        temp_workspace, 'aligned_climate_zones.tif')
    aligned_raster_paths = [aligned_climate_zones_raster]
    aligned_rain_events = []
    # because our month numbers are zero-padded, this works as you expect.
    for month_no, raster_path in (
            enumerate(sorted(monthly_rain_events_rasters))):
        aligned_raster_path = os.path.join(
            temp_workspace, f'aligned_{month_no+1}.tif')
        aligned_raster_paths.append(aligned_raster_path)
        aligned_rain_events.append(aligned_raster_path)

    # Assume we're using the climate zones raster pixel size.
    cz_raster_info = pygeoprocessing.get_raster_info(climate_zones_raster)
    target_pixel_size = cz_raster_info['pixel_size']
    target_projection_wkt = cz_raster_info['projection_wkt']
    pygeoprocessing.align_and_resize_raster_stack(
        [climate_zones_raster] + monthly_rain_events_rasters,
        aligned_raster_paths,
        ['near'] + (['bilinear']*len(monthly_rain_events_rasters)),
        target_pixel_size, 'intersection',
        target_projection_wkt=target_projection_wkt,
        working_dir=temp_workspace)

    monthly_rain_events_by_climate_zone = collections.defaultdict(
        lambda: collections.defaultdict(int))
    cz_array = pygeoprocessing.raster_to_numpy_array(
        aligned_climate_zones_raster)
    cz_nodata = pygeoprocessing.get_raster_info(
        aligned_climate_zones_raster)['nodata'][0]
    for month_name, aligned_path in zip(MONTH_NAMES, aligned_rain_events):
        for cz_id in numpy.unique(cz_array):
            cz_mask = (
                (cz_array == cz_id) &
                (~pygeoprocessing.array_equals_nodata(cz_array, cz_nodata)))
            rain_events_array = pygeoprocessing.raster_to_numpy_array(
                aligned_path)
            if rain_events_array[cz_mask].size > 0:
                monthly_rain_events_by_climate_zone[month_name][cz_id] = (
                    rain_events_array[cz_mask].mean())

    with open(target_csv, 'w') as target_file:
        target_file.write(f'cz_id,{",".join(MONTH_NAMES)}\n')
        for cz_id in numpy.unique(cz_array):
            if cz_id == cz_nodata:
                continue
            row_data = [str(cz_id)]
            for month_name in MONTH_NAMES:
                row_data.append(str(monthly_rain_events_by_climate_zone[
                    month_name][cz_id]))
            target_file.write(f'{",".join(row_data)}\n')
    LOGGER.info(f"Wrote climate zones table to {target_csv}")

    if remove_workspace:
        shutil.rmtree(
            temp_workspace,
            onerror=lambda *args: LOGGER.exception("Error during rmtree"))


if __name__ == "__main__":
    GDRIVE_DIR = (
        "/Users/jdouglass/Library/CloudStorage/"
        "GoogleDrive-jadoug06@stanford.edu/Shared drives/GreenFin/"
        "Pilot_Countries/Armenia/GIS_Armenia/1_preprocess")
    #main(
    #    "target.csv", os.path.join(GDRIVE_DIR, "KG_climatezones.tif"),
    #    glob.glob("GFDL-ESM4_hist_plus_ssp585_pr-2040-2040-*-rain-events.tif"),
    #    'workspace', False)
    try:
        workspace = sys.argv[4]
    except IndexError:
        workspace = None

    try:
        main(sys.argv[1], sys.argv[2], glob.glob(sys.argv[3]), workspace)
    except Exception as e:
        print(sys.argv)
        raise
