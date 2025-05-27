library(raster)
library(sf)

r <- raster('C:/Users/jgldstn/Documents/GreenFin/Colombia/SinuWaterAccts/avoided_export_M_MOD_MOD.tif') # UPDATE filepath to read in InVEST ES supply raster output
sheds <- st_read('C:/Users/jgldstn/Documents/GreenFin/Colombia/SinuWaterAccts/beneficiaries/sheds_147.shp') # UPDATE filepath to read in servicesheds vector

flow <- sheds$CAUDAL_CON # UPDATE to define values to weight ES supply by
r_sheds <- rasterize(x = sheds, y = r, field = flow, fun = sum) # Rasterize servicesheds assigning values as sum of overlapping beneficiaries' weights. Raster matches resolution, CRS, dims, extent of InVEST ES supply raster output

writeRaster(r_sheds, filename = paste('C:/Users/jgldstn/Documents/GreenFin/Colombia/SinuWaterAccts/beneficiaries/caudal'), format = 'GTiff', overwrite = T) # UPDATE filepath and filename to write beneficiaries weights raster
