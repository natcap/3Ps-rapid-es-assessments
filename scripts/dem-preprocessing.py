"""DEM preprocessing script.  Details TBD."""

import argparse
import logging
import multiprocessing
import os
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pygeoprocessing
import pygeoprocessing.routing
import taskgraph
from osgeo import gdal
from osgeo import osr

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))
URL_BASE = 'https://storage.googleapis.com/gef-ckan-public-data'

# Keys are known aliases, values are the path to the layer relative to URL_BASE
# above.
KNOWN_DEMS = {
    'SRTM': f'{URL_BASE}/srtm-v3-1s/srtm-v3-1s.tif',
}

WGS84_SRS = osr.SpatialReference()
WGS84_SRS.ImportFromEPSG(4326)
WGS84_SRS_WKT = WGS84_SRS.ExportToWkt()


def main(args=None) -> Dict[str, str]:
    # parse args
    return {
        'source_dem_slug': 'SRTM',
        'source_aoi_path': sys.argv[1],
        'tfa_slice': '1000:10000:200',
        'workspace': 'bay_area_workspace',
        'pixel_size': [30, 30],
        'resample_method': 'bilinear',
    }


# TODO: add typehint-sensitive docstring
# TODO: add taskgraph
def preprocess_dem(
        source_dem_slug: str,
        source_aoi_path: str,
        tfa_slice: str,
        workspace: str,
        pixel_size: List[float],
        routing_method: str = 'D8',
        resample_method: Optional[str] = 'near',
        target_epsg: Optional[Union[str, int]] = None
        ) -> None:
    """"""
    workspace = os.path.normcase(os.path.normpath(workspace))
    if not os.path.exists(workspace):
        os.makedirs(workspace)

    graph = taskgraph.TaskGraph(
        os.path.join(workspace, '.taskgraph'),
        n_workers=multiprocessing.cpu_count())
    LOGGER.info(f"Writing output files to {workspace}")

    vector_info = pygeoprocessing.get_vector_info(source_aoi_path)

    target_srs = osr.SpatialReference()
    if target_epsg is not None:
        LOGGER.info(f"Output will use user-defined EPSG code {target_epsg}")
        target_srs.ImportFromEPSG(int(target_epsg))
        target_srs_wkt = target_srs.ExportToWkt()
    else:
        target_srs_wkt = vector_info['projection_wkt']
        target_srs.ImportFromWkt(target_srs_wkt)
        target_epsg = target_srs.GetAttrValue('AUTHORITY', 1)
        LOGGER.info(
            "Output will use the AOI vector's projection, "
            f"EPSG: {target_epsg}")

    # Get the target bounding box in WGS84 coordinates for the VRT.
    LOGGER.info("Transforming the AOI bbox to WGS84")
    wgs84_bbox = pygeoprocessing.transform_bounding_box(
        vector_info['bounding_box'], vector_info['projection_wkt'],
        WGS84_SRS_WKT)

    LOGGER.info("Transforming the WGS84 bbox to the target EPSG")
    target_bbox = pygeoprocessing.transform_bounding_box(
        wgs84_bbox, WGS84_SRS_WKT, target_srs_wkt)

    # Build a VRT for use in pygeoprocessing's warp_raster.  A VRT isn't
    # strictly required, but it's easier to use pygeoprocessing's warp_raster
    # (which requires a local file) than calling gdal.Warp with options.
    LOGGER.info("Building a VRT for the clipped bounds")
    source_url = KNOWN_DEMS[source_dem_slug]
    vrt_options = gdal.BuildVRTOptions(outputBounds=wgs84_bbox)
    vrt_path = os.path.join(workspace, f'wgs84-{source_dem_slug}.vrt')
    vrt_task = graph.add_task(
        gdal.BuildVRT,
        args=[vrt_path, [f'/vsicurl/{source_url}']],
        kwargs={'options': vrt_options},
        task_name='Build VRT',
        target_path_list=[vrt_path],
        dependent_task_list=[]
    )

    # Warp to the target projection
    LOGGER.info(f"Warping {source_dem_slug} to local projection with "
                f"{resample_method}")
    warped_raster = os.path.join(workspace, f'warped-{source_dem_slug}.tif')
    warped_task = graph.add_task(
        pygeoprocessing.warp_raster,
        kwargs={
            'base_raster_path': vrt_path,
            'target_pixel_size': pixel_size,
            'target_raster_path': warped_raster,
            'resample_method': resample_method,
            'target_bb': target_bbox,
            'target_projection_wkt': target_srs_wkt,
        },
        task_name='Fetch and warp DEM',
        target_path_list=[warped_raster],
        dependent_task_list=[vrt_task]
    )

    LOGGER.info("Filling pits")
    filled_raster = os.path.join(workspace, f'pitfilled-{source_dem_slug}.tif')
    pitfilling_task = graph.add_task(
        pygeoprocessing.routing.fill_pits,
        args=[(warped_raster, 1), filled_raster],
        task_name='Fill pits',
        target_path_list=[filled_raster],
        dependent_task_list=[warped_task]
    )

    LOGGER.info(f"Calculating {routing_method} flow direction")
    routing_method = routing_method.lower()
    if routing_method == 'd8':
        flow_dir_func = pygeoprocessing.routing.flow_dir_d8
        flow_accum_func = pygeoprocessing.routing.flow_accumulation_d8
    elif routing_method == 'mfd':
        flow_dir_func = pygeoprocessing.routing.flow_dir_mfd
        flow_accum_func = pygeoprocessing.routing.flow_accumulation_mfd
    else:
        raise ValueError(
            f"routing method must be either D8 or MFD, not {routing_method}")

    LOGGER.info("Calculating flow direction")
    flow_dir_raster = os.path.join(
        workspace, f'flowdir-{routing_method}-{source_dem_slug}.tif')
    flow_dir_task = graph.add_task(
        flow_dir_func,
        args=[(filled_raster, 1), flow_dir_raster],
        task_name='Flow direction',
        target_path_list=[flow_dir_raster],
        dependent_task_list=[pitfilling_task]
    )

    LOGGER.info("Calculating flow accumulation")
    flow_accum_raster = os.path.join(
        workspace, f'flowaccum-{routing_method}-{source_dem_slug}.tif')
    flow_accum_task = graph.add_task(
        flow_accum_func,
        args=[(flow_dir_raster, 1), flow_accum_raster],
        task_name='Flow direction',
        target_path_list=[flow_accum_raster],
        dependent_task_list=[flow_dir_task]
    )

    tfa_start, tfa_stop, tfa_step = tfa_slice.split(":")
    for tfa in range(int(tfa_start), int(tfa_stop), int(tfa_step)):
        LOGGER.info(f"Calculating streams with TFA {tfa}")
        tfa_raster_path = os.path.join(
            workspace, f'tfa-{source_dem_slug}-{tfa}.tif')
        if routing_method == 'd8':
            _ = graph.add_task(
                pygeoprocessing.routing.extract_streams_d8,
                args=[(flow_accum_raster, 1), tfa, tfa_raster_path],
                task_name='D8 stream extraction',
                target_path_list=[tfa_raster_path],
                dependent_task_list=[flow_accum_task],
            )
        else:
            _ = graph.add_task(
                pygeoprocessing.routing.extract_streams_mfd,
                args=[(flow_accum_raster, 1), (flow_dir_raster, 1), tfa,
                      tfa_raster_path],
                task_name='MFD stream extraction',
                target_path_list=[tfa_raster_path],
                dependent_task_list=[flow_accum_task],
            )

    graph.close()
    graph.join()


if __name__ == '__main__':
    PARSED_ARGS = main()
    preprocess_dem(**PARSED_ARGS)
