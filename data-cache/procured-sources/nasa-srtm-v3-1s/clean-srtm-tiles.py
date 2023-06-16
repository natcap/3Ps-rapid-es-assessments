import logging
import os
import sys
import zipfile

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))

# These tiles are improperly formatted for GDAL: for some reason, the standard
# .hgt.zip format isn't working.  A workaround is to unzip the files and remove
# the original zipfile.
PROBLEMATIC_TILES = set([
    "N37E051",
    "N37E052",
    "N38E050",
    "N38E051",
    "N38E052",
    "N39E050",
    "N39E051",
    "N40E051",
    "N41E050",
    "N41E051",
    "N42E049",
    "N42E050",
    "N43E048",
    "N43E049",
    "N44E048",
    "N44E049",
    "N47W087",  # This additional one was found by trial and error
])

def clean_files(tiles_dir):
    tiles_dir = os.path.abspath(tiles_dir)

    for tilename in PROBLEMATIC_TILES:
        tile_basename = f'{tilename}.SRTMGL1.hgt'
        tile_filename = os.path.join(tiles_dir, f'{tile_basename}.zip')
        if not os.path.exists(tile_filename):
            LOGGER.info(f"Skipping tile; not found: {tile_filename}")
            continue

        with zipfile.ZipFile(tile_filename, 'r') as hgt_zip:
            LOGGER.info(f"Extracting {tile_filename} to {tile_basename}")
            with open(f'{tiles_dir}/{tile_basename}', 'wb') as new_hgt_file:
                new_hgt_file.write(hgt_zip.read(tile_basename))

        LOGGER.info(f"Removing {tile_filename}")
        os.remove(tile_filename)


if __name__ == '__main__':
    clean_files(sys.argv[1])
