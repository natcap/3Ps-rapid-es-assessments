#!python3

# Build a list of URLs for downloading GMTED2010 tiles from USGS.
# GMTED2010 is available at 3 resolutions (7.5, 15 and 30 arcseconds)
# and has a variety of different layers available depending on the statistic
# desired (mean, median, standard deviation, etc.).
#
# This script generates a list of all of these tiles that can be downloaded in
# bulk by wget.  This list is written to stdout.


PREFIX = 'https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/topo/downloads/GMTED/Global_tiles_GMTED'
for lyr in ("mea",  # mean
            "std",  # standard deviation
            "med",  # median
            "min",  # minimum
            "dsc",  # systematic subsample
            "bln"):  # breakline emphasis
    for res in ("075",   # 7.5 arcseconds
                "150",   # 15 arcseconds
                "300"):  # 30 arcseconds
        for lat in range(-70, 71, 20):
            if lat < 0:
                lat_direction = 'S'
            else:
                lat_direction = 'N'
            lat = abs(lat)

            for lon in range(-180, 151, 30):
                if lon < 0:
                    lon_direction = 'W'
                else:
                    lon_direction = 'E'
                lon = abs(lon)

                directory = f'{res}darcsec/{lyr}/{lon_direction}{lon:03}'
                filename = f'{lat}{lat_direction}{lon:03}{lon_direction}_20101117_gmted_{lyr}{res}.tif'
                print(f'{PREFIX}/{directory}/{filename}')
