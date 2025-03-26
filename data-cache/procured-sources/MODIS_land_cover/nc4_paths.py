import os
import sys
import zipfile
import glob


def extract_paths(dir, type):

    """Create txt file listing all *_dem.tif paths to feed into gdalbuildvrt.
       gdalbuildvrt had a hard time reading the *_dem.tif files from the zipfiles
       using glob, this was a solution to that problem.

    Args:
        tiles_dir (path): the path to the directory containing the ASTER zipfiles.

    Returns:
        Prints a list of all ASTER geotiff tiles to standard out.
    """

    dir = os.path.abspath(dir)
    files = []
    for file in glob.glob(os.path.join(dir, "*.nc4"), recursive=True):
        files.append(file)
    print(*files, sep='\n')


if __name__ == '__main__':
    extract_paths(sys.argv[1], sys.argv[2])
