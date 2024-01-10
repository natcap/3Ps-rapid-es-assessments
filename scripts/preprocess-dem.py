"""DEM preprocessing script.  Details TBD."""

import logging
import math
import multiprocessing
import os
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import click
import pygeoprocessing
import pygeoprocessing.geoprocessing
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
    return {
        'source_dem_slug': 'SRTM',
        'source_aoi_path': sys.argv[1],
        'tfa_slice': '1000:10000:200',
        'workspace': 'bay_area_workspace',
        'pixel_size': [30, 30],
        'resample_method': 'bilinear',
    }


# TODO: add typehint-sensitive docstring
@click.command()
@click.option('--dem', default="SRTM", help="The name of the DEM to use.")
@click.argument('aoi')
@click.option('--tfa', help=(
    'The threshold flow accumulation, in the format start:stop:step. For '
    'example, "1000:5000:150"'))
@click.option('--workspace', default='preprocess-dem-workspace')
@click.option('--routing_method', default='d8')
@click.option('--resample_method', default='near')
@click.option('--target_epsg', default=None)
@click.option('--pixel_size', default=None)
def preprocess_dem(
        dem: str,
        aoi: str,
        tfa: str,
        workspace: str,
        pixel_size: List[float] = None,
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

    vector_info = pygeoprocessing.get_vector_info(aoi)

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
    source_url = KNOWN_DEMS[dem]
    vrt_path = os.path.join(workspace, f'wgs84-{dem}.vrt')
    gdal.BuildVRT(vrt_path, [f'/vsicurl/{source_url}'],
                  outputBounds=wgs84_bbox)

    if isinstance(pixel_size, str):
        pixel_size = [int(s) for s in pixel_size.split(',')]

    if not pixel_size:
        target_srs_units = target_srs.GetAttrValue('UNIT')
        if target_srs_units not in ('m', 'meter', 'metre'):
            raise ValueError(
                f"Target EPSG units are not in meters ({target_srs_units}), "
                "so you must define the pixel size at the CLI. "
                "Example: --pixel_size=[30,30]")

        source_raster_info = pygeoprocessing.get_raster_info(vrt_path)
        pixel_size_on_a_side = math.sqrt(
            pygeoprocessing.geoprocessing._m2_area_of_wg84_pixel(
                source_raster_info['pixel_size'][0],
                (wgs84_bbox[1] - wgs84_bbox[0]) / 2))
        pixel_size = [pixel_size_on_a_side, -pixel_size_on_a_side]

    # Warp to the target projection
    LOGGER.info(f"Warping {dem} to local projection with "
                f"{resample_method}")
    warped_raster = os.path.join(workspace, f'warped-{dem}.tif')
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
        dependent_task_list=[]
    )

    LOGGER.info("Filling pits")
    filled_raster = os.path.join(workspace, f'pitfilled-{dem}.tif')
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
        workspace, f'flowdir-{routing_method}-{dem}.tif')
    flow_dir_task = graph.add_task(
        flow_dir_func,
        args=[(filled_raster, 1), flow_dir_raster],
        task_name='Flow direction',
        target_path_list=[flow_dir_raster],
        dependent_task_list=[pitfilling_task]
    )

    LOGGER.info("Calculating flow accumulation")
    flow_accum_raster = os.path.join(
        workspace, f'flowaccum-{routing_method}-{dem}.tif')
    flow_accum_task = graph.add_task(
        flow_accum_func,
        args=[(flow_dir_raster, 1), flow_accum_raster],
        task_name='Flow direction',
        target_path_list=[flow_accum_raster],
        dependent_task_list=[flow_dir_task]
    )

    if not tfa:
        graph.close()
        graph.join()
        return

    tfa_start, tfa_stop, tfa_step = tfa.split(":")
    for tfa in range(int(tfa_start), int(tfa_stop), int(tfa_step)):
        LOGGER.info(f"Calculating streams with TFA {tfa}")
        tfa_raster_path = os.path.join(
            workspace, f'tfa-{dem}-{tfa}.tif')
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
    LOGGER.info("Complete!")


if __name__ == '__main__':
    #PARSED_ARGS = main()
    #preprocess_dem(**PARSED_ARGS)
    preprocess_dem()
