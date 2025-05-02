import pygeoprocessing
import sys
import glob
import os
import numpy

def sum_annual_precip(tifs_path, filesuffix, out_path, filename, finalsuffix):
    base_rasters =[]

    tifs_path=f"{tifs_path}_{filesuffix}"
    for rasters in glob.glob(os.path.join(tifs_path,'*.tif')):
        base_rasters.append(rasters)
    
    print(base_rasters)

    target_path = f"{out_path}/{filename}_{finalsuffix}.tif"

    def _sum(*months):
        output = numpy.full(months[0].shape,0,dtype=numpy.float32)
        for month in months:
            output += month
        output /= len(months) # I previously believed we need to take an average. I am keeping this in case we need to at another time
        output[output==0]=-1
        return(output)
    pygeoprocessing.raster_map(_sum, base_rasters, target_path, target_nodata=-1)


if __name__ == '__main__':
    sum_annual_precip(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])