library(terra)


out_dir = "D:/Documents/large_rasters/clipped/"
# original_raster_path = "D:/Documents/large_rasters/clipped/height_surface.tif"
original_raster_path = "../../../../large_rasters/clipped/height_veg.tif"
# original_raster_path = "D:/Documents/large_rasters/clipped/height_terrain.tif"

original_raster <- lapply(original_raster_path, rast)[[1]]

fact <- 2.5

r_change_res <- rast(res = res(original_raster) * fact,
                  nrows = nrow(original_raster) * fact,
                  ncols = ncol(original_raster) * fact,
                  crs = crs(original_raster),
                  extent = ext(original_raster))


r_resample <- terra::resample(original_raster, r_change_res)

oFilename <- paste0(out_dir, "resample.tif")
writeRaster(r_resample, oFilename, wopt = list(gdal = c("COMPRESS=LZW")),
              overwrite = TRUE)
