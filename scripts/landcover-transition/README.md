# Landcover transition utility
This python utility script runs a transition analyses on two landcover rasters.
Given a transition _from_ raster and a transition _to_ raster the script
creates the following three outputs:

1. **Transition matrix** (CSV)

    a matrix with "From/To" rows and columns
    where the row keys represent the "from" raster classes, the column
    keys represent the "to" raster classes, and the values are the
    counts for how many times the transition occurs. NoData values are
    included in the row, column keys.

2. **Transition raster** (tif)

    a raster of new integer values that represent transitions.

    The transition raster has the following special cases:
    # nodata -> nodata - should output nodata
    # x -> x - unchanged values should output the same new class
    # x -> nodata  - should output a new class value
    # nodata -> y - should output a new class value

3. **Transition raster table** (CSV)

    an accompanying table to the transition raster that has two columns,
    "Transition Class" and "Transition".  "Transition Class" indicates the new
    class given the unique transition which is described in the "Transition"
    column.

## Dependencies and installation
This scripts relies on the following libraries:
  - numpy
  - gdal
  - pygeoprocessing

### Conda setup
To set up a conda environment via the command line:
```
  >> conda create -p ./transition-env -c conda-forge python=3.10
  >> conda activate ./transition-env
  >> conda install pygeoprocessing
```
Once the environment is set up download the script by cloning the repository.

`  >> git clone https://github.com/natcap/gef-rapid-es-assessments.git`

The script will live in `gef-rapid-es-assessments/scripts/landcover-transition/lulc-transition.py`

### Docker setup (coming soon)
Docker integration (coming soon)

## Example
For this example let's assume you are on the command line in the folder
`user/workspace/`. This example assumes you have the repository cloned in
`user/workspace/gef-rapid-es-assessments` and another folder
`user/workspace/transitions/` with the LULC rasters.

To learn about how to run the script you can use the `--help` flag.

```bash
>> python gef-rapid-es-assessments/scripts/landcover-transitions/lulc-transition.py --help
  
usage: lulc-transition.py [-h] [-f FROM] [-t TO] [-o OUTPUT_DIRECTORY]

Given two landcover rasters creates a transition matrix table and transition
raster with accompanying attribute table.

options:
  -h, --help            show this help message and exit
  -f FROM, --from FROM  Path of landcover raster before transitionm.
  -t TO, --to TO        Path of landover after transition.
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Path to a directory to save the outputs of this script.
```

To run the script and output into `user/workspace/transitions`:

`  >> python gef-rapid-es-assessments/scripts/landcover-transitions/lulc-transition.py -f transitions/LULC-before.tif -t transitions/LULC-after.tif -o transitions`

