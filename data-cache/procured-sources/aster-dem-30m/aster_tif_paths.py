import os
import sys
import zipfile
import glob
import pathlib


def extract_paths(tiles_dir):
    tiles_dir = os.path.abspath(tiles_dir)
    tiffiles = []
    for zip in glob.glob(os.path.join(tiles_dir, "*.zip"), recursive=True):
        path = zipfile.Path(zip)
        with zipfile.ZipFile(zip, 'r') as zipObj:
            for name in zipObj.infolist():
                if name.filename.endswith("_dem.tif"):
                    file=str(name.filename)
                    final_path = f'/vsizip/{zip}/{file}'
                    tiffiles.append(final_path)

    print(*tiffiles, sep='\n')

if __name__ == '__main__':
    extract_paths(sys.argv[1])