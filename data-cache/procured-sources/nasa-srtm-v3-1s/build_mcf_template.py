import datetime
import json
import sys
import textwrap
import uuid

import pygeoprocessing
from osgeo import osr


def main(raster_file, mcf_file):
    raster_info = pygeoprocessing.get_raster_info(raster_file)

    srs = osr.SpatialReference()
    srs.ImportFromWkt(raster_info['projection_wkt'])
    srs.AutoIdentifyEPSG()  # in case there isn't an EPSG code
    epsg_code = int(srs.GetAttrValue('AUTHORITY', 1))

    metadata = {
        'mcf': {'version': 1.0},
        'metadata': {
            'identifier': str(uuid.uuid4()),
            'language': 'en',
            'charset': 'utf8',
            'hierarchylevel': 'dataset',
            'datestamp': '$date',  # pygeometa replaces at runtime
            #'dataseturi': I'm not sure ... this is optional, leaving out
        },
        'spatial': {
            'datatype': 'grid',  # because it's a raster
            'geomtype': 'point',  # because it's a raster
        },
        'identification': {
            'language': 'en',
            'doi': 'https://doi.org/10.5067/MEASURES/SRTM/SRTMGL1.003',
            'language': 'inappliccable',
            'title': 'NASA Shuttle Radar Topography Mission Global 1 arc second',
            'edition': 'v3',
            'abstract': textwrap.dedent("""\
                The Shuttle Radar Topography Mission (SRTM) is a joint effort between NASA, the National
                Geospatial-Intelligence Agency (NGA), the German Aerospace Center, and the Italian Space
                Agency. Data derived from SRTM are based on interferometric observations from C-band and
                X-band synthetic aperture radar (SAR) antennas aboard space shuttle Endeavour. The mission
                flew February 11–21, 2000, imaging the Earth’s surface between 60°N and 56°S; this accounts
                for 80% of the Earth’s landmass. The spectral coverage for SAR operates at a much longer
                wavelength than optical sensors. C-band operates at 5.6 cm wavelength while X-band operates at
                3.1 cm. Because radar operates at a longer wavelength, smaller particles such as cloud droplets
                are transmitted and not reflected. Additionally, C-band was used to provide mapping coverage
                as mandated by the mission, while X-band with higher signal-to-noise ratio was used to validate
                C radar processing and quality control."""),
            'topiccategory': ['geoscientificInformation'],
            'fees': 'None',
            'accessconstraints': 'otherRestrictions',  # public
            'rights': 'Copyright NASA LP DAAC',
            'url': 'https://storage.googleapis.com/gef-ckan-public-data/nasa-srtm-v3-1s/srtm-v3-1s.tif',
            'status': 'completed',
            'maintenancefrequency': 'unknown',
            'dates': {
                'publication': '2013-09-04T09:21:05.226Z',
                'revision': '2015-09-02T10:31:05.569Z'
            },
            'extents': {
                'spatial': [{
                    'bbox': raster_info['bounding_box'],
                    'crs': epsg_code,
                    'description': 'The Earth’s surface between 60°N and 56°S',
                }],
                'temporal': [{
                    'begin': '2000-02-11T00:00:00Z',
                    'end': '2000-02-21T23:59:59Z',
                }],
            },
            'keywords': {
                'default': {
                    'keywords': {
                        'en': [],
                    },
                    'keywords_type': 'theme',
                    'vocabulary': {
                        'name': 'My vocabulary name',
                        'url': 'https://example.org/my-vocab',
                    }
                },
            },
            'license': {
                'name': 'Public Domain',
                #'url': '',  # for public domain this does not apply
            },
        },
        'content_info': {
            'type': 'image',
            'attributes': [{
                'name': 'elevation',
                'units': 'm',  # user-defined
                'type': 'integer',  # derived from pixel dtype
            }],
            'dimensions': [{
                'name': 'B1',
                'units': 'm',
                'min': -32767,
                'max': 32767,
            }],
        },
        'contact': {
            'pointOfContact': {
                'organization': 'NASA',
                'url': '',
                'individualname': '',
                'positionname': '',
                'phone': '',
                'fax': '',
                'address': '',
                'city': '',
                'administrativearea': '',
                'postalcode': '',
                'country': '',
                'email': '',
            },
            'distributor': {
                'organization': 'The Natural Capital Project',
                'url': 'https://naturalcapitalproject.stanford.edu',
                'individualname': 'James Douglass',
                'positionname': 'Software Architect',
                'phone': 'None - use email',
                'fax': 'None - use email',
                'address': '327 Campus Drive, Bass Biology Building 123',
                'city': 'Stanford',
                'administrativearea': 'California',
                'postalcode': '94305',
                'country': 'United States of America',
                'email': 'naturalcapitalproject@stanford.edu',
            }
        },
        'distribution': {
            'gcs': {
                'url': 'https://storage.googleapis.com/gef-ckan-public-data/nasa-srtm-v3-1s/srtm-v3-1s.tif',
                'type': 'download',
                'name': 'Direct download',
                'description': 'File download hosted by Google Cloud Storage',
                'function': 'download',
            },
            # Maybe we don't want to provide Oak info in public metadata?
            #'oak': {
            #    'url':
            #    'file:///oak/stanford/groups/gdaily/global-dataset-cache/srtm-v3-1s/srtm-v3-1s.tif'
            #    'type': 'FILE:RASTER',
            #    'name': 'On-campus file access',
            #    'description': 'Direct access to the raster and overviews.',
            #    'function': 'download',
            #},
        },
    }
    with open(mcf_file, 'w') as mcf_json:
        json.dump(metadata, mcf_json)



if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
