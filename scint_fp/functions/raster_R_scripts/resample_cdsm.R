library(terra)
#> Warning: package 'terra' was built under R version 4.0.3
#> terra version 1.0.10
library(tools)
outDir <- "D:/Documents/large_rasters/clipped/"


#first file is master file - i.e. the crop for this is used for all
#the left hand side is the new name, the right hand side is the current name
files <- c("height_surface.tif" = "../../../../large_rasters/DSM_GLA_1m_EPSG_32631.tif",
           "veg_attempt.tif" = "../../../../large_rasters/CDSM_GLA_1m_EPSG32631.tif")

#zoom in this number of  at each edge
zoom_m <- 1500
original_raster <- rast(files[1])
crs_out <- crs(original_raster)
new_extent <- terra::ext(original_raster) - rep(zoom_m, 4)


for (i in 2:length(files)) {
  
  dir.create(outDir, showWarnings = FALSE)
  
  r <- rast(files[i])
  r_project <- terra::project(r, crs_out, method = "near")
  r_resample <- terra::resample(r_project, original_raster)
  
  r_agg <- terra::aggregate(r_resample, fact = 4, fun = "mean")
  
  r_crop <- terra::crop(r_agg, new_extent)
  
  terra::writeRaster(r_crop, file.path(outDir, names(files[i])),
                     wopt = list(gdal = c("COMPRESS=LZW")), overwrite = TRUE)
}


