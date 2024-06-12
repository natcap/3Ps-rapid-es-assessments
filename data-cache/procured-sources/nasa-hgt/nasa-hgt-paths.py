import os
import sys
import zipfile
import glob
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))

def extract_paths(tiles_dir):

    """Create txt file listing all *.hgt paths to feed into gdalbuildvrt.
       gdalbuildvrt had a hard time reading the *.hgt files from the zipfiles
       using glob, this was a solution to that problem.

    Args:
        tiles_dir (path): the path to the directory containing the NASA HGT zipfiles.

    Returns:
        Prints a list of all NASA hgt tiles to standard out.
    """

    tiles_dir = os.path.abspath(tiles_dir)
    files = []
    for zip in glob.glob(os.path.join(tiles_dir, "*.zip"), recursive=True):
        with zipfile.ZipFile(zip, 'r') as zipObj:
            print(zipObj)
            zipObj.testzip()
            #<zipfile.ZipFile filename='/scratch/users/epavia/nasa-hgt-v1-1s/tiles/NASADEM_HGT_n60e080.zip' mode='r'>
            for name in zipObj.infolist():
                if name.filename.endswith(".hgt"):
                    print(name.filename)
                    file = str(name.filename)
                    final_path = f'/vsizip/{zip}/{file}'
                    files.append(final_path)

    print(*files, sep='\n')


if __name__ == '__main__':
    extract_paths(sys.argv[1])