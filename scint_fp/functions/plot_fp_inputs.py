import netCDF4 as nc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter


def plot_footprint_model_inputs(nc_file_path, csv_file_path):
    """

    :return:
    """

    ncdf_file = nc.Dataset(nc_file_path)

    csv_df = pd.read_csv(csv_file_path)

    try:
        csv_df['Unnamed: 0'] = pd.to_datetime(csv_df['Unnamed: 0'], format='%Y-%m-%d %H:%M:%S')
    except ValueError:
        csv_df['Unnamed: 0'] = pd.to_datetime(csv_df['Unnamed: 0'], format='%d/%m/%Y %H:%M')

    csv_df.index = csv_df['Unnamed: 0']
    csv_df = csv_df.drop('Unnamed: 0', 1)

    csv_df = csv_df[['sig_v']]

    file_time = ncdf_file.variables['time']
    time_dt = nc.num2date(file_time[:], file_time.units)
    ustar = ncdf_file.variables['ustar']
    L = ncdf_file.variables['L']
    stab_param = ncdf_file.variables['stab_param']

    # create pandas dataframe of vals
    nc_df_dict = {'time': time_dt, 'ustar': ustar, 'L': L, 'stab_param': stab_param}
    nc_df = pd.DataFrame(nc_df_dict)

    nc_df = nc_df.set_index('time')
    nc_df.index = nc_df.index.round('1s')
    # filter out any times which are NOT unstable
    nc_df.loc[nc_df.stab_param > -0.03] = np.nan

    df = nc_df.merge(csv_df, how='outer', left_index=True, right_index=True)

    # find first instance of nc file which isnt a nan

    min_ustar = min(df[~np.isnan(df['ustar'])].index)
    min_L = min(df[~np.isnan(df['L'])].index)
    min_zL = min(df[~np.isnan(df['stab_param'])].index)
    min_sigv = min(df[~np.isnan(df['sig_v'])].index)

    min_time_df = min(min_ustar, min_L, min_zL, min_sigv)

    max_ustar = max(df[~np.isnan(df['ustar'])].index)
    max_L = max(df[~np.isnan(df['L'])].index)
    max_zL = max(df[~np.isnan(df['stab_param'])].index)
    max_sigv = max(df[~np.isnan(df['sig_v'])].index)

    max_time_df = max(max_ustar, max_L, max_zL, max_sigv)

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=(12,12))

    ax1.plot(df.index[np.where(~np.isnan(df['sig_v']))], df['sig_v'][np.where(~np.isnan(df['sig_v']))[0]], marker='.', linewidth=0.5, color='red')
    ax1.set_ylabel('$\sigma$v (m s$^{-1}$)')
    ax2.plot(df.index, df['ustar'], marker='.', linewidth=0.5, color='blue')
    ax2.set_ylabel('u$_{*}$ (m s$^{-1}$)')

    ax3.plot(df.index, df['L']*-1, marker='.', linewidth=0.5, color='green')
    ax3.set_ylabel('L (m)')
    ax3.set_yscale('log')
    ax3.set_ylim(ax3.get_ylim()[::-1])

    ax4.plot(df.index, df['stab_param']*-1, marker='.', linewidth=0.5, color='purple')
    ax4.set_ylabel('z$_{f}$/L')
    ax4.set_yscale('log')
    ax4.set_ylim(ax4.get_ylim()[::-1])

    ax1.set_xlim(min_time_df, max_time_df)
    ax2.set_xlim(min_time_df, max_time_df)
    ax3.set_xlim(min_time_df, max_time_df)
    ax4.set_xlim(min_time_df, max_time_df)

    ax3.xaxis.set_major_formatter(DateFormatter('%H'))
    ax4.xaxis.set_major_formatter(DateFormatter('%H'))

    plt.gcf().autofmt_xdate()

    fig.subplots_adjust(wspace=0.15, hspace=0)

    # plt.show()
    plt.savefig('C:/Users/beths/OneDrive - University of Reading/Working Folder/in_vars.png', bbox_inches='tight')

    print('end')


nc_filepath = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/142/LASMkII_Fast_IMU_2016142_1min_sa10min.nc'
footprint_csv_path = 'D:/Documents/scintillometer_footprints/scint_fp/test_outputs/met_inputs_minutes_142.csv'

# nc_filepath = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/111/LASMkII_Fast_IMU_2016111_1min_sa10min.nc'
# footprint_csv_path = 'D:/Documents/scintillometer_footprints/scint_fp/test_outputs/met_inputs_minutes_111.csv'

plot_footprint_model_inputs(nc_filepath, footprint_csv_path)
