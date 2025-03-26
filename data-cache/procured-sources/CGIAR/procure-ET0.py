""" Read CGIAR Evapotranspiration Data (ET0). This script downloads the zipfiles
    and extracts the monthly datasets to the downloads and monthly folder. The
    annual data is extracted to the annual folder.

    Information on this dataset can be found here:
    https://csidotinfo.wordpress.com/2019/01/24/global-aridity-index-and-potential-evapotranspiration-climate-database-v3/
"""
import os
import requests
import io
import zipfile
import sys


path = sys.argv[1]
url = r'https://figshare.com/ndownloader/articles/7504448/versions/6'

directories = {'downloads': 'downloads_path', 'monthly': 'monthly_path', 'annual': 'annual_path'}
for d,p in directories.items():
    path = os.path.join(path, d)
    if not os.path.exists(path):
        os.mkdir(path)
    globals()[str(p)] = path


def download_all():
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(downloads_path) # type: ignore


def extract_monthly():
    files = []
    for zip in os.listdir(os.path.join(downloads_path)): # type: ignore
        files.append(zip)

    # parse out the zip folder with monthly data
    for i in files:
        if "monthly" in i:
            monthly = os.path.join(downloads_path, i) # type: ignore
    print(monthly)

    # extract only the ET0 monthly files
    with zipfile.ZipFile(monthly) as z:
        print(z.namelist())
        for names in z.namelist():
            if names.endswith('.tif') | names.endswith('.pdf'):  #select files we want, including readme for reference
                z.extract(names, monthly_path) # type: ignore


def extract_annual():
    files = []
    for zip in os.listdir(os.path.join(downloads_path)): # type: ignore
        files.append(zip)

    # parse out the zip folder with annual data
    for i in files:
        if "annual" in i:
            annual = os.path.join(downloads_path, i) # type: ignore

    # extract only the ET0 files
    with zipfile.ZipFile(annual) as z:
        for names in z.namelist():
            if "et0_v3_yr.tif" | "Readme" in names:  # select files we want, including readme for reference
                z.extract(names, annual_path)  # type: ignore # write only the ET0 annual files to annual folder(not including std files)


def main(path):
    """Run all downloads and zipfile data extractions.

    Args:
        path (str): The path to the folder the zipfiles are extracted to.
        Originally, the data was downloaded to the Oak global data cache.
    """

    download_all()
    extract_monthly()
    extract_annual()


if __name__ == '__main__':
    main(sys.argv[1])
