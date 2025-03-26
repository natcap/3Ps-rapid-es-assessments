""" Read WorldClim monthly historical Precipication Data (ET0).
    Calculate the annual precipitation by summing the monthly precipication rasters

    Information on these datasets can be found here:
    https://www.worldclim.org/data/worldclim21.html
"""

import os
import requests
import io
import zipfile
import sys
import glob
import numpy
import pygeoprocessing
import logging

logging.basicConfig(level=logging.INFO)
file_path = sys.argv[1]
url = r'https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_30s_prec.zip'

directories = {'monthly': 'monthly_path', 'annual': 'annual_path'}
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

    target_path = os.path.join(annual_path, 'wc2.1_30s_annual_precip.tif')

    def _sum(*months):
        output = numpy.full(months[0].shape,0,dtype=numpy.float32)
        for month in months:
            output += month
        # output /= len(months) # I previously believed we need to take an average. I am keeping this in case we need to at another time
        output[output==0]=-1
        return(output)
    pygeoprocessing.raster_map(_sum, base_rasters, target_path, target_nodata=-1)

def main(file_path):
    """Download data and calculate annual precipitation.

    Args:
        path (str): The path to the folder the zipfiles are extracted to.
        Originally, the data was downloaded to the Oak global data cache.
    """
    read_url()
    sum_annual_precip()


if __name__ == '__main__':
    main(sys.argv[1])
    
