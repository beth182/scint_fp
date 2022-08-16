# Title     : TODO
# Objective : TODO
# Created by: beths
# Created on: 03/06/2021

library(terra)
#> Warning: package 'terra' was built under R version 4.0.3
#> terra version 1.0.10
library(tools)
outDir <- "D:/Documents/large_rasters/clipped/"


#first file is master file - i.e. the crop for this is used for all
#the left hand side is the new name, the right hand side is the current name
files <- c("height_surface.tif" = "../../../../large_rasters/DSM_GLA_1m_EPSG_32631.tif",
           "height_veg_2.tif" = "../../../../large_rasters/CDSM_GLA_1m_EPSG32631.tif",)

#zoom in this number of  at each edge
zoom_m <- 1500

for (i in 1:length(files)) {
  
  dir.create(outDir, showWarnings = FALSE)
  
  r <- rast(files[i])
  if (i == 1) {
    new_extent <- terra::ext(r) - rep(zoom_m, 4)
    crs_out <- crs(r)
  }
  
  r <- terra::project(r, crs_out, method = "near") 
  if (i > 1) r <- terra::aggregate(r, fact = 4, fun = "mean")
  r1 <- terra::crop(r, new_extent)
  terra::writeRaster(r1, file.path(outDir, names(files[i])), 
                     wopt = list(gdal = c("COMPRESS=LZW")), overwrite = TRUE)
}

