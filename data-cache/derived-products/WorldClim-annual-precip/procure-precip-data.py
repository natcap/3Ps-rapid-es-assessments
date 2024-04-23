import os
import requests
import io
import zipfile
from osgeo import gdal

import numpy
import pygeoprocessing

path = 'Z:/global-dataset-cache/world-clim'
url = r'https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_30s_prec.zip'
NODATA_FLOAT32 = numpy.finfo(numpy.float32).min
download = os.path.join(path, 'downloads')
monthly = os.path.join(path, 'monthly')
if not os.path.exists(monthly):
        os.mkdir(monthly)
        
def read_url():
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(download)
    z.extractall(monthly)

def sum_annual_precip():
    base_rasters =[]
    for rasters in os.listdir(os.path.join(path, monthly)):
        if rasters.endswith(".tif"):
            rasters=os.path.join(path,monthly,rasters)
            base_rasters.append(rasters)
    
    print(base_rasters)

    nodatas = [
        pygeoprocessing.get_raster_info(path)['nodata'][0] for path in base_rasters]

    print(nodatas)

    target_path = os.path.join(path, 'annual')
    if not os.path.exists(target_path):
        os.mkdir(target_path)

    raster_paths = [(path, 1) for path in base_rasters]
    #pygeoprocessing.geoprocessing.raster_calculator(
     #   raster_paths, _sum, target_path, gdal.GDT_Float32, float(NODATA_FLOAT32))


def main():
    #read_url()
    sum_annual_precip()


if __name__ == '__main__':
    main()
    
