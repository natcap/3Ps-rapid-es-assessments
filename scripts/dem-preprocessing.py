"""DEM preprocessing script.  Details TBD."""

import argparse
import logging
import os
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pygeoprocessing
import pygeoprocessing.routing
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
    gdal.BuildVRT(vrt_path, [f'/vsicurl/{source_url}'], options=vrt_options)

    # Warp to the target projection
    LOGGER.info(f"Warping {source_dem_slug} to local projection with "
                f"{resample_method}")
    warped_raster = os.path.join(workspace, f'warped-{source_dem_slug}.tif')
    pygeoprocessing.warp_raster(
        vrt_path, pixel_size, warped_raster, resample_method,
        target_bb=target_bbox, target_projection_wkt=target_srs_wkt)

    LOGGER.info("Filling pits")
    filled_raster = os.path.join(workspace, f'pitfilled-{source_dem_slug}.tif')
    pygeoprocessing.routing.fill_pits((warped_raster, 1), filled_raster)

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
    flow_dir_func((filled_raster, 1), flow_dir_raster)

    LOGGER.info("Calculating flow accumulation")
    flow_accum_raster = os.path.join(
        workspace, f'flowaccum-{routing_method}-{source_dem_slug}.tif')
    flow_accum_func((flow_dir_raster, 1), flow_accum_raster)

    tfa_start, tfa_stop, tfa_step = tfa_slice.split(":")
    for tfa in range(int(tfa_start), int(tfa_stop), int(tfa_step)):
        LOGGER.info(f"Calculating streams with TFA {tfa}")
        tfa_raster_path = os.path.join(
            workspace, f'tfa-{source_dem_slug}-{tfa}.tif')
        if routing_method == 'd8':
            pygeoprocessing.routing.extract_streams_d8(
                (flow_accum_raster, 1), tfa, tfa_raster_path)
        else:
            pygeoprocessing.routing.extract_streams_mfd(
                (flow_accum_raster, 1), (flow_dir_raster, 1), tfa,
                tfa_raster_path)


if __name__ == '__main__':
    PARSED_ARGS = main()
    preprocess_dem(**PARSED_ARGS)
