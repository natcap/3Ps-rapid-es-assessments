import os
import requests
import io
import zipfile
from osgeo import gdal
import sys
import glob
from pathlib import Path
import numpy
import pygeoprocessing
import logging

logging.basicConfig(level=logging.INFO)
file_path = sys.argv[1]
url = r'https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_30s_prec.zip'
NODATA_FLOAT32 = numpy.finfo(numpy.float32).min

directories = {'monthly':'monthly_path','annual':'annual_path'}
for d,p in directories.items():
    path = os.path.join(file_path, d)            
    if not os.path.exists(path):
        os.mkdir(path)
    globals()[str(p)] = path
        
def read_url():
    r = requests.get(url,stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(monthly_path)

def sum_annual_precip():
    base_rasters =[]
    for rasters in glob.glob(os.path.join(monthly_path,'*.tif')):
        base_rasters.append(rasters)
    
    print(base_rasters)

    target_path = os.path.join(path, 'annual')
    if not os.path.exists(target_path):
        os.mkdir(target_path)

    def _avg(*months):
        output = numpy.full(months[0].shape,0,dtype=numpy.float32)
        for month in months:
            output += month
        output /= len(months)
        output[output==0]=-1
        return(output)
    pygeoprocessing.raster_map(_avg, base_rasters, 'annual_precip.tif',target_nodata=-1)
    #pygeoprocessing.geoprocessing.raster_calculator(
     #   raster_paths, _sum, target_path, gdal.GDT_Float32, float(NODATA_FLOAT32))


def main(file_path):

    #read_url()
    sum_annual_precip()


if __name__ == '__main__':
    main(sys.argv[1])
    
