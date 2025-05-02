from osgeo import gdal
import os
import sys

def separate_bands(input_path, out_path, filename, filesuffix):
    """
    Separates bands from a multi-band GeoTIFF into individual files.

    Args:
        input_path (str): Path to the input GeoTIFF file.
        out_path (str): Path to the output directories.
        filename (str): Pattern for the prefix of the output file names as well as the name of the output directory.
    """
    dataset = gdal.Open(input_path)

    out_path = f"{out_path}_{filesuffix}"

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    num_bands = dataset.RasterCount

    for i in range(1, num_bands + 1):
        band = dataset.GetRasterBand(i)
        no_data_value = band.GetNoDataValue()
        driver = gdal.GetDriverByName('GTiff')
        output_path = f"{out_path}/{filename}_{i}.tif"
        output_dataset = driver.Create(output_path, dataset.RasterXSize, dataset.RasterYSize, 1, band.DataType)

        output_dataset.SetGeoTransform(dataset.GetGeoTransform())
        output_dataset.SetProjection(dataset.GetProjection())
        output_band = output_dataset.GetRasterBand(1)
        output_band.WriteArray(band.ReadAsArray())
        output_band.SetNoDataValue(no_data_value)

        output_band.FlushCache()
        output_dataset = None
        print(f"Band {i} saved to {output_path}")

    dataset = None  # Close the input dataset


if __name__ == '__main__':
    separate_bands(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])