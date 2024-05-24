import os
import sys
import zipfile
import glob


def extract_paths(tiles_dir):

    """Create txt file listing all *_dem.tif paths to feed into gdalbuildvrt.
       gdalbuildvrt had a hard time reading the *_dem.tif files from the zipfiles
       using glob, this was a solution to that problem.

    Args:
        tiles_dir (path): the path to the directory containing the ASTER zipfiles.

    Returns:
        A txt file listing all ASTER geotiff tiles.
    """

    tiles_dir = os.path.abspath(tiles_dir)
    tiffiles = []
    for zip in glob.glob(os.path.join(tiles_dir, "*.zip"), recursive=True):
        with zipfile.ZipFile(zip, 'r') as zipObj:
            for name in zipObj.infolist():
                if name.filename.endswith("_dem.tif"):
                    file = str(name.filename)
                    final_path = f'/vsizip/{zip}/{file}'
                    tiffiles.append(final_path)

    print(*tiffiles, sep='\n')


if __name__ == '__main__':
    extract_paths(sys.argv[1])
