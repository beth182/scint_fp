import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import contextily as cx
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import geopandas as gpd
import matplotlib.colors as colors
import matplotlib as mpl
mpl.rcParams.update({'font.size': 15})  # updating the matplotlib fontsize

# CHANGE HERE
doy_choice = 123
sa_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/123_1200_all_paths/'


# deal with files
file_list = []
os.chdir(sa_dir)
for file in glob.glob("*.tif"):
    file_list.append(sa_dir + file)


# colours ##############################################################################################################
colour_list = [(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (0.13, 0.55, 0.13, 1.0), (1.0, 0.65, 0.0, 1.0), (1.0, 0.0, 1.0, 1.0)]


# initalize plot #######################################################################################################
raster0 = rasterio.open(file_list[0])
fig, ax = plt.subplots(figsize=(10, 10))

# plot lancover map
# landcover_location = 'C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/BIG_MAP/BIG_MAP_CROP.tif'
landcover_location = 'C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/Elliott/LandUseMM_7classes_32631.tif'
landcover_raster = rasterio.open(landcover_location)

color_list_lc = ["white", "dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]
# make a color map of fixed colors
cmap_lc = colors.ListedColormap(color_list_lc)
bounds_lc = [0, 1, 2, 3, 4, 5, 6, 7, 8]
norm_lc = colors.BoundaryNorm(bounds_lc, cmap_lc.N)

rasterio.plot.show(landcover_raster, ax=ax, cmap=cmap_lc, norm=norm_lc, interpolation='nearest', alpha=0.5)

ax.set_xlim(278553.32064617483, 288213.50645262643)
ax.set_ylim(5705765.4782133335, 5715078.469181076)


# handle raster ########################################################################################################
for i, filename in enumerate(file_list):
    replc = filename.replace('.', '_')
    splt = replc.split('_')
    # time_string = splt[-3] + ':' + splt[-2]
    time_string = splt[-5][-3:] + ' - ' + splt[-4]

    raster = rasterio.open(filename)
    raster_array = raster.read()

    # make all 0 vals in array nan
    raster_array[raster_array == 0.0] = np.nan

    # force non-zero vals to be 1
    bool_arr = np.ones(raster_array.shape)

    # remove nans in bool array
    nan_index = np.where(np.isnan(raster_array))
    bool_arr[nan_index] = 0.0

    # get location of max val
    ind_max_2d = np.unravel_index(np.nanargmax(raster_array), raster_array.shape)[1:]
    max_coords = raster.xy(ind_max_2d[0], ind_max_2d[1])

    # make plot ########################################################################################################

    colour_here = list(colour_list[i])

    rasterio.plot.show(bool_arr, transform=raster.transform, contour=True, contour_label_kws={}, ax=ax,
                       colors=[colour_here])
    ax.scatter(max_coords[0], max_coords[1], color=colour_here, marker='o', s=30, label=time_string)

# plot paths
df = gpd.read_file('C:/Users/beths/Desktop/LANDING/scint_path_shp/BCT_IMU.shp')
df.plot(edgecolor='red', ax=ax, linewidth=4.0, linestyle='--')

df = gpd.read_file('C:/Users/beths/Desktop/LANDING/scint_path_shp/BTT_BCT.shp')
df.plot(edgecolor='blue', ax=ax, linewidth=4.0, linestyle='--')

df = gpd.read_file('C:/Users/beths/Desktop/LANDING/scint_path_shp/IMU_BTT.shp')
df.plot(edgecolor='forestgreen', ax=ax, linewidth=4.0, linestyle='--')

df = gpd.read_file('C:/Users/beths/Desktop/LANDING/scint_path_shp/IMU_SWT.shp')
df.plot(edgecolor='orange', ax=ax, linewidth=4.0, linestyle='--')

df = gpd.read_file('C:/Users/beths/Desktop/LANDING/scint_path_shp/SCT_SWT.shp')
df.plot(edgecolor='magenta', ax=ax, linewidth=4.0, linestyle='--')

plt.legend(loc='upper left')

plt.yticks(rotation=90)

plt.title('DOY: ' + str(doy_choice) + ' 1200 UTC')

# plt.savefig('C:/Users/beths/Desktop/LANDING/' + 'sa_lines_' + str(doy_choice) + '.png', bbox_inches='tight')
plt.show()

print('end')








# looking at wind directions
"""
filepath240 = 'C:/Users/beths/Desktop/LANDING/New folder1/LASMkII_Fast_IMU_2016142_1min_wd_correction_240.nc'
filepath250 = 'C:/Users/beths/Desktop/LANDING/New folder1/LASMkII_Fast_IMU_2016142_1min_wd_correction_250.nc'
filepath260 = 'C:/Users/beths/Desktop/LANDING/New folder1/LASMkII_Fast_IMU_2016142_1min_wd_correction_260.nc'
filepath270 = 'C:/Users/beths/Desktop/LANDING/New folder1/LASMkII_Fast_IMU_2016142_1min_wd_correction_270.nc'
filepath280 = 'C:/Users/beths/Desktop/LANDING/New folder1/LASMkII_Fast_IMU_2016142_1min_wd_correction_280.nc'


file240 = nc.Dataset(filepath240)
z0240 = file240.variables['z_0'][:][file240.variables['z_0'][:].mask == False][0]
zd240 = file240.variables['z_d'][:][file240.variables['z_d'][:].mask == False][0]
qh240 = file240.variables['QH'][:]
zf240 = file240.variables['z_f'][:][file240.variables['z_f'][:].mask == False][0]

file250 = nc.Dataset(filepath250)
z0250 = file250.variables['z_0'][:][file250.variables['z_0'][:].mask == False][0]
zd250 = file250.variables['z_d'][:][file250.variables['z_d'][:].mask == False][0]
qh250 = file250.variables['QH'][:]
zf250 = file250.variables['z_f'][:][file250.variables['z_f'][:].mask == False][0]

file260 = nc.Dataset(filepath260)
z0260 = file260.variables['z_0'][:][file260.variables['z_0'][:].mask == False][0]
zd260 = file260.variables['z_d'][:][file260.variables['z_d'][:].mask == False][0]
qh260 = file260.variables['QH'][:]
zf260 = file260.variables['z_f'][:][file260.variables['z_f'][:].mask == False][0]

file270 = nc.Dataset(filepath270)
z0270 = file270.variables['z_0'][:][file270.variables['z_0'][:].mask == False][0]
zd270 = file270.variables['z_d'][:][file270.variables['z_d'][:].mask == False][0]
qh270 = file270.variables['QH'][:]
zf270 = file270.variables['z_f'][:][file270.variables['z_f'][:].mask == False][0]

file280 = nc.Dataset(filepath280)
z0280 = file280.variables['z_0'][:][file280.variables['z_0'][:].mask == False][0]
zd280 = file280.variables['z_d'][:][file280.variables['z_d'][:].mask == False][0]
qh280 = file280.variables['QH'][:]
zf280 = file280.variables['z_f'][:][file280.variables['z_f'][:].mask == False][0]

z0_list = [z0240, z0250, z0260, z0270, z0280]
zd_list = [zd240, zd250, zd260, zd270, zd280]
zf_list = [zf240, zf250, zf260, zf270, zf280]
wd_list = [240,250,260,270,280]

time = file250.variables['time'][:]

minvals = []
maxvals = []

for i in range(0, len(qh240)):
    list_i = [qh240[i],qh250[i],qh260[i],qh270[i],qh280[i]]
    minval = min(list_i)
    max_val = max(list_i)

    minvals.append(minval)
    maxvals.append(max_val)

print('end')

plt.plot(wd_list, zd_list, marker='o')
plt.xlabel('wd')
plt.ylabel('zd')


plt.plot(time, qh240, label=240)
plt.plot(time, qh250, label=250)
plt.plot(time, qh260, label=260)
plt.plot(time, qh270, label=270)
plt.plot(time, qh280, label=280)
plt.legend()
plt.xlabel('time')
plt.ylabel('QH')





plt.plot(time, np.asarray(maxvals) - np.asarray(minvals), marker='.')
plt.ylabel('qh diff')
plt.xlabel('time')
"""


