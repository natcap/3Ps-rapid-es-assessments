# R script to rasterize servicesheds:
This script sums overlapping polygons (servicesheds) by a weighted field and then rasterizes them.

Required libraries:
raster https://cran.r-project.org/web/packages/raster/index.html
sf https://cran.r-project.org/web/packages/sf/index.html

Line 4 reads in a biophysical ES supply raster, typically this is an InVEST result, and assigns it to an object named "r". Be sure to replace the placeholder filepath with the appropriate one.
Line 5 reads in a vector containing polygon features representing the servicesheds and assigns it to an object named "sheds". Replace the placeholder filepath with the appropriate one.

Line 7 assigns the values from a field in "sheds" to an object named "flow". This field should contain the values by which to weight ES supply ("r"). Be sure to update the placeholder field named "CAUDAL_CON" to the appropriate fieldname from your vector.

Line 8 rasterizes the servicesheds, assigning values as the sum of overlapping beneficiaries' weights (from the chosen field in the polygon features), and assigns these to an object named "r_sheds". The resulting raster will match the CRS, resolution, dimensions, and extent of "r".

Line 10 writes a 'weighted beneficiaries' raster. Be sure to update the filepath and filename as appropriate.
