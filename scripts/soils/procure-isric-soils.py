import argparse
import csv
import hashlib
import http.client
import logging
import os
import shutil

from bs4 import BeautifulSoup

import numpy
import pygeoprocessing
import requests
import taskgraph
import urllib3.exceptions
from osgeo import gdal

logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'),
)
LOGGER = logging.getLogger('ISRIC-Erodibility')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
URL_BASE = 'https://files.isric.org/soilgrids/latest/data/'
ISRIC_SOILGRIDS_TYPES = {
    'sand': 'sand_0-5cm_mean',
    'clay': 'clay_0-5cm_mean',
    'silt': 'silt_0-5cm_mean',
    #'soc': 'sand_0-5cm_mean',
}

CHECKSUM_KEY = "checksum.sha256.txt"
NODATA_FLOAT32 = numpy.finfo(numpy.float32).min

def _get_remote_raster_urls(soil_type, tile_csv_path):
    LOGGER.info(f"Building CSV for {soil_type} tile urls")

    # Save VRT to file as first line with corresponding checksum
    vrt_url = f"{URL_BASE}{soil_type}/{soil_type}_0-5cm_mean.vrt"
    vrt_checksum_url = f"{URL_BASE}{soil_type}/{CHECKSUM_KEY}"
    LOGGER.info(f"vrt url: {vrt_url}")
    LOGGER.info(f"vrt checksum url: {vrt_checksum_url}")

    with requests.Session() as s:

        vrt_checksum_response = s.get(vrt_checksum_url).text
        with open(tile_csv_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for line in vrt_checksum_response.splitlines():
                checksum_data = line.split()
                if checksum_data[1] == f"{soil_type}_0-5cm_mean.vrt":
                    csv_writer.writerow([vrt_url, checksum_data[0]])

        # Get tile urls from the VRT. This avoids Python URL directory walking.
        page = s.get(vrt_url).text
        soup = BeautifulSoup(page, 'html.parser')
        tile_url_list = []
        checksum_url_list = []

        LOGGER.info(f"Get tile URLs from VRT")
        for node in soup.find_all('sourcefilename'):
            tile_relative_url = "/".join(node.string.split("/")[1:])
            tile_complete_url = f"{URL_BASE}{soil_type}/{tile_relative_url}"
            tile_url_list.append(tile_complete_url)
            checksum_url = os.path.dirname(tile_complete_url) + '/' + CHECKSUM_KEY
            if not checksum_url in checksum_url_list:
                checksum_url_list.append(checksum_url)

        # Create checksum lookup to map tile urls to checksums
        LOGGER.info(f"Create checksum lookup")
        checksum_tile_lookup = {}
        for checksum_file in checksum_url_list:
            checksum_response = s.get(checksum_file).text
            for line in checksum_response.splitlines():
                checksum_data = line.split()
                checksum_tile_lookup[checksum_data[1]] = checksum_data[0]

        # Write out tile urls with corresponding checksums
        LOGGER.info(f"Write out tile urls and checksums to file")
        with open(tile_csv_path, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for url_path in tile_url_list:
                url_key = os.path.basename(url_path)
                checksum = checksum_tile_lookup[url_key]
                csv_writer.writerow([url_path, checksum])

    LOGGER.info(f"Saving tile urls and checksum complete")


def _digest_file(filepath, alg):
    m = hashlib.new(alg)
    with open(filepath, 'rb') as binary_file:
        while True:
            chunk = binary_file.read(2048)
            if not chunk:
                break
            m.update(chunk)
    return m.hexdigest()


def fetch_raster(source_raster_url, dest_raster_path, checksum_alg, checksum):
    r = requests.head(source_raster_url)
    target_file_size_bytes = int(r.headers.get('content-length', 0))
    LOGGER.info(f"Downloading {source_raster_url}, "
                f"{target_file_size_bytes} bytes")
    resume_header = None

    def _filesize(path):
        try:
            return os.path.getsize(path)
        except OSError:
            # If file does not yet exist
            return 0

    bytes_written = 0
    n_retries = 0
    while _filesize(dest_raster_path) < target_file_size_bytes:
        try:
            LOGGER.info(
                f"Downloading {dest_raster_path}, {bytes_written}b so far")
            if n_retries:
                LOGGER.info(f"{n_retries} retries so far")
            with requests.get(source_raster_url,
                              stream=True, headers=resume_header) as r:
                with open(dest_raster_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
        except (http.client.IncompleteRead,
                urllib3.exceptions.ProtocolError) as error:
            n_retries += 1
            bytes_written = _filesize(dest_raster_path)
            LOGGER.exception(error)
            LOGGER.info(f'Download failed, restarting from {bytes_written}')
            resume_header = {'Range': f'bytes={bytes_written}'}

    LOGGER.info(f"Downloaded {source_raster_url}")
    calculated_checksum = _digest_file(dest_raster_path, checksum_alg)
    if calculated_checksum != checksum:
        LOGGER.info(f"calc checksum: {calculated_checksum} vs {checksum}")
        raise RuntimeError(f"Checksums do not match on {dest_raster_path}")


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
    expected_nodata = 255
    nodatas = [
        pygeoprocessing.get_raster_info(path)['nodata'][0] for path in rasters]
    assert nodatas == [expected_nodata]*len(nodatas)

    def _calculate(soil_depth_0cm, soil_depth_5cm, soil_depth_15cm,
                   soil_depth_30cm, soil_depth_60cm, soil_depth_100cm,
                   soil_depth_200cm):
        awc = numpy.full(soil_depth_0cm.shape, NODATA_FLOAT32,
                         dtype=numpy.float32)
        valid_mask = numpy.ones(soil_depth_0cm.shape, dtype=bool)
        for array in [soil_depth_0cm, soil_depth_5cm, soil_depth_15cm,
                      soil_depth_30cm, soil_depth_60cm, soil_depth_100cm,
                      soil_depth_200cm]:
            valid_mask &= (array != 255)

        awc[valid_mask] = ((1/200) * (1/2) * (
            ((5 - 0) * (soil_depth_0cm[valid_mask] + soil_depth_5cm[valid_mask])) +
            ((15 - 5) * (soil_depth_5cm[valid_mask] + soil_depth_15cm[valid_mask])) +
            ((30 - 15) * (soil_depth_15cm[valid_mask] + soil_depth_30cm[valid_mask])) +
            ((60 - 30) * (soil_depth_30cm[valid_mask] + soil_depth_60cm[valid_mask])) +
            ((100 - 60) * (soil_depth_60cm[valid_mask] + soil_depth_100cm[valid_mask])) +
            ((200 - 100) * (soil_depth_100cm[valid_mask] + soil_depth_200cm[valid_mask])))
        ) / 100
        return awc


    # TODO: build overviews as well before upload.
    # TODO: build in some warnings if the values are outside of the expected
    # range of 0-100 (or 0-1 if we've already divided by 100).
    driver_opts = ('GTIFF', (
    'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=LZW',
    'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'PREDICTOR=1', 'NUM_THREADS=4'))
    raster_paths = [(path, 1) for path in rasters]
    pygeoprocessing.geoprocessing.raster_calculator(
        raster_paths, _calculate, target_awc_path,
        gdal.GDT_Float32, float(NODATA_FLOAT32))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache-dir', default='downloads')
    parser.add_argument('--soil-type',
                        choices=('clay', 'sand', 'silt', 'soc', 'all'),
                        default='all')

    parsed_args = parser.parse_args()

    cache_dir = os.path.abspath(parsed_args.cache_dir)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    taskgraph_dir = os.path.join(cache_dir, 'taskgraph_cache')
    if not os.path.exists(taskgraph_dir):
        os.makedirs(taskgraph_dir)

    # TODO check cache-dir to avoid reruns
    #LOGGER.info(f"Looking for existing Erodibility rasters in {cache_dir}")

    # set up taskgraph to spread out workload and not repeat work
    n_workers = 6
    LOGGER.info(f"TaskGraph workers: {n_workers}")
    graph = taskgraph.TaskGraph(taskgraph_dir, n_workers, reporting_interval=60*5)

    ## For sand, clay, silt, or ALL
    LOGGER.info(f'soil type: {parsed_args.soil_type.lower()}')
    soil_type_to_procure = [parsed_args.soil_type.lower()]
    if parsed_args.soil_type.lower() == 'all':
        soil_type_to_procure = list(ISRIC_SOILGRIDS_TYPES.keys())

    # 1. Get list of tile urls and save to csv file with corresponding
    # checksum, so we can skip this step if already done previously.
    soil_tiles_csv_lookup = {}
    for soil_type in soil_type_to_procure:
        soil_dir = os.path.join(cache_dir, soil_type)
        if not os.path.isdir(soil_dir):
            os.mkdir(soil_dir)

        soil_tiles_csv_path = os.path.join(soil_dir, f'{soil_type}-tile-urls.csv')
        soil_tiles_csv_lookup[soil_type] = soil_tiles_csv_path

        _ = graph.add_task(
            _get_remote_raster_urls,
            kwargs={
                'soil_type': soil_type,
                'tile_csv_path': soil_tiles_csv_path,
            },
            target_path_list=[soil_tiles_csv_path],
            task_name='Collect tile and checksum urls to csv file.'
        )

    graph.join()
    LOGGER.info(f"Completed building CSV with urls.")

    # 2. Download the soil rasters and do checksum
    for soil_type, soil_tiles_csv_path in soil_tiles_csv_lookup.items():
        # Save tiles in similar ISRIC directory structure:
        # sand_0-5cm_mean/
        #      sand_0-5cm_mean.vrt
        #      sand_0-5cm_mean/
        #           tile_dir_1/
        #           tile_dir_2/
        #      ...
        soil_dir = os.path.join(cache_dir, soil_type)
        soil_tiles_dir = os.path.join(soil_dir, ISRIC_SOILGRIDS_TYPES[soil_type])
        if not os.path.isdir(soil_tiles_dir):
            os.mkdir(soil_tiles_dir)

        download_task_list = []
        #only_download_n = 10
        with open(soil_tiles_csv_path, 'r') as csv_fp:
            reader = csv.reader(csv_fp)
            for row in reader:
                raster_tile_url = row[0]
                checksum = row[1]

                raster_tile_basename = os.path.basename(raster_tile_url)
                vrt_check = os.path.splitext(raster_tile_basename)[1]
                if  vrt_check == '.vrt':
                    raster_tile_out_path = os.path.join(soil_dir, raster_tile_basename)
                else:
                    raster_tile_dir = os.path.basename(os.path.dirname(raster_tile_url))
                    raster_tile_out_dir = os.path.join(soil_tiles_dir, raster_tile_dir)
                    if not os.path.isdir(raster_tile_out_dir):
                        os.mkdir(raster_tile_out_dir)

                    raster_tile_out_path = os.path.join(
                        raster_tile_out_dir, raster_tile_basename)

                download_task = graph.add_task(
                    fetch_raster,
                    kwargs={
                        'source_raster_url': raster_tile_url,
                        'dest_raster_path': raster_tile_out_path,
                        'checksum_alg': 'sha256',
                        'checksum': checksum,
                    },
                    target_path_list=[raster_tile_out_path],
                    task_name=f'Download raster tile {raster_tile_basename}.'
                )
                download_task_list.append(download_task)

                #if len(download_task_list) >= only_download_n:
                #    break


    graph.close()
    graph.join()

    LOGGER.info(f"Soils download complete for {parsed_args.soil_type}")

    # 3. Download the tiles


#    local_soil_rasters = []
#    for soil_raster_dict in ISRIC_2017_AWCH1_RASTERS.values():
#        local_file = os.path.join(
#            cache_dir, os.path.basename(soil_raster_dict['url']))
#        if not os.path.exists(local_file):
#            LOGGER.info(f"File not found: {local_file}")
#            fetch_raster(soil_raster_dict['url'], local_file, 'md5',
#                         soil_raster_dict['md5'])
#        else:
#            LOGGER.info(f"Verifying checksum on {local_file}")
#            if not _digest_file(local_file, 'md5') == soil_raster_dict['md5']:
#                raise AssertionError(
#                    "MD5sum for {local_file} did not match what's expected. "
#                    "Try deleting the file and re-running the program to "
#                    "re-download the file.")
#        local_soil_rasters.append(local_file)
#
#    LOGGER.info(f"Calculating AWC to {parsed_args.target_awc}")
#    calculate_awc(*local_soil_rasters, parsed_args.target_awc)
#
#    LOGGER.info(f"AWC complete; written to {parsed_args.target_awc}")
#

if __name__ == '__main__':
    main()
