import os
import requests
import io
import zipfile
from osgeo import gdal

import numpy
import pygeoprocessing


path = 'Z:/global-dataset-cache/CGIAR-ET0'
url = r'https://figshare.com/ndownloader/articles/7504448/versions/6'

download = os.path.join(path, 'downloads')
if not os.path.exists(download):
    os.mkdir(download)

monthly_path = os.path.join(path, 'monthly')
if not os.path.exists(monthly_path):
    os.mkdir(monthly_path)

annual_path = os.path.join(path, 'annual')
if not os.path.exists(annual_path):
    os.mkdir(annual_path)
        
def download_all():
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(download)

def extract_monthly():
    files = []
    for zip in os.listdir(os.path.join(download)):
        files.append(zip)


    # parse out the zip folder with monthly data
    for i in files:
        if "monthly" in i:
            monthly = os.path.join(download,i)
    print(monthly)

    # extract only the ET0 monthly files
    with zipfile.ZipFile(monthly) as z:
        print(z.namelist())
        for names in z.namelist():
            if names.endswith('.tif') | names.endswith('.pdf'): #select files we want, including readme for reference
                z.extract(names, monthly_path)

        

    

def extract_annual():
    files = []
    for zip in os.listdir(os.path.join(download)):
        files.append(zip)

    # parse out the zip folder with annual data
    for i in files:
        if "annual" in i:
            annual = os.path.join(download,i)

    # extract only the ET0 files
    with zipfile.ZipFile(annual) as z:
        for names in z.namelist():
            if "et0_v3_yr.tif" | "Readme" in names: #select files we want, including readme for reference
                z.extract(names, annual_path) #write only the ET0 annual files to annual folder(not including std files)



def main():
    #download_all()
    extract_monthly()
    #extract_annual()


if __name__ == '__main__':
    main()