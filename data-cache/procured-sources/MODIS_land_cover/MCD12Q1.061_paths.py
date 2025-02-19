import sys
import xml.etree.ElementTree as ET

##SCRIPT COPIED FROM JAMES DOUGLASS' Scripts in this repo: https://github.com/phargogh/2025-02-18-download-modis-land-cover-types/tree/main

URL_PREFIX = "https://opendap.cr.usgs.gov"


def extract_links(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    for child in root:
        if child.tag.endswith('dataset'):
            datasets_root = child
            break

    for dataset in datasets_root:
        for suffix in ('dap', 'info', 'rdf', 'html', 'dap.nc4', 'dap.csv'):
            print(f"{URL_PREFIX}{dataset.attrib['ID']}.{suffix}")






if __name__ == '__main__':
    extract_links(sys.argv[1])
