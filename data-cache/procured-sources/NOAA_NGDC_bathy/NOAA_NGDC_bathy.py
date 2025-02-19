import sys
import xml.etree.ElementTree as ET

## Script derived from J. Douglass' script in this repo: https://github.com/phargogh/2025-02-18-download-modis-land-cover-types/tree/main

URL_PREFIX = "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_bed_elev_gtif/"

def extract_links():
    
    for dataset in datasets_root:
        for suffix in ('dap', 'info', 'rdf', 'html', 'dap.nc4', 'dap.csv'):
            print(f"{URL_PREFIX}{dataset.attrib['ID']}.{suffix}")






if __name__ == '__main__':
    extract_links(sys.argv[1])
