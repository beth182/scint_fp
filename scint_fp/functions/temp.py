import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np

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


