import os
import requests
import io
import zipfile
from osgeo import gdal
import sys
import numpy
import pygeoprocessing
import argparse


path = sys.argv[1]
url = r'https://figshare.com/ndownloader/articles/7504448/versions/6'
        

directories = {'downloads':'downloads_path','monthly':'monthly_path','annual':'annual_path'}
for d,p in directories.items():
    path = os.path.join(file_path, d)            
    if not os.path.exists(path):
        os.mkdir(path)
    globals()[str(p)] = path

def download_all():
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(downloads_path)

def extract_monthly():
    files = []
    for zip in os.listdir(os.path.join(downloads_path)):
        files.append(zip)


    # parse out the zip folder with monthly data
    for i in files:
        if "monthly" in i:
            monthly = os.path.join(downloads_path,i)
    print(monthly)

    # extract only the ET0 monthly files
    with zipfile.ZipFile(monthly) as z:
        print(z.namelist())
        for names in z.namelist():
            if names.endswith('.tif') | names.endswith('.pdf'): #select files we want, including readme for reference
                z.extract(names, monthly_path)

        

    

def extract_annual():
    files = []
    for zip in os.listdir(os.path.join(downloads_path)):
        files.append(zip)

    # parse out the zip folder with annual data
    for i in files:
        if "annual" in i:
            annual = os.path.join(downloads_path,i)

    # extract only the ET0 files
    with zipfile.ZipFile(annual) as z:
        for names in z.namelist():
            if "et0_v3_yr.tif" | "Readme" in names: #select files we want, including readme for reference
                z.extract(names, annual_path) #write only the ET0 annual files to annual folder(not including std files)



def main(path):
    download_all()
    extract_monthly()
    extract_annual()


if __name__ == '__main__':
    main(sys.argv[1])