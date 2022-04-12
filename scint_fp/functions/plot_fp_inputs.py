import netCDF4 as nc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib as mpl
import datetime as dt

mpl.rcParams.update({'font.size': 16})  # updating the matplotlib fontsize

def plot_footprint_model_inputs(nc_file_path_123, csv_file_path_123,
                                nc_file_path_126, csv_file_path_126):
    """

    :return:
    """

    ncdf_file_123 = nc.Dataset(nc_file_path_123)
    ncdf_file_126 = nc.Dataset(nc_file_path_126)

    csv_df_123 = pd.read_csv(csv_file_path_123)
    csv_df_126 = pd.read_csv(csv_file_path_126)

    try:
        csv_df_123['Unnamed: 0'] = pd.to_datetime(csv_df_123['Unnamed: 0'], format='%Y-%m-%d %H:%M:%S')
    except ValueError:
        csv_df_123['Unnamed: 0'] = pd.to_datetime(csv_df_123['Unnamed: 0'], format='%d/%m/%Y %H:%M')

    try:
        csv_df_126['Unnamed: 0'] = pd.to_datetime(csv_df_123['Unnamed: 0'], format='%Y-%m-%d %H:%M:%S')
    except ValueError:
        csv_df_126['Unnamed: 0'] = pd.to_datetime(csv_df_126['Unnamed: 0'], format='%d/%m/%Y %H:%M')

    csv_df_123.index = csv_df_123['Unnamed: 0']
    csv_df_123 = csv_df_123.drop('Unnamed: 0', 1)

    csv_df_126.index = csv_df_126['Unnamed: 0']
    csv_df_126 = csv_df_126.drop('Unnamed: 0', 1)

    csv_df_123 = csv_df_123[['sig_v']]
    csv_df_126 = csv_df_126[['sig_v']]

    csv_df_123.columns = ['sig_v_123']
    csv_df_126.columns = ['sig_v_126']

    file_time_123 = ncdf_file_123.variables['time']
    time_dt_123 = nc.num2date(file_time_123[:], file_time_123.units)
    ustar_123 = ncdf_file_123.variables['ustar']
    L_123 = ncdf_file_123.variables['L']
    stab_param_123 = ncdf_file_123.variables['stab_param']


    file_time_126 = ncdf_file_126.variables['time']
    time_dt_126 = nc.num2date(file_time_126[:], file_time_126.units)
    ustar_126 = ncdf_file_126.variables['ustar']
    L_126 = ncdf_file_126.variables['L']
    stab_param_126 = ncdf_file_126.variables['stab_param']


    # create pandas dataframe of vals
    nc_df_dict_123 = {'time_123': time_dt_123, 'ustar_123': ustar_123, 'L_123': L_123, 'stab_param_123': stab_param_123}
    nc_df_123 = pd.DataFrame(nc_df_dict_123)

    nc_df_dict_126 = {'time_126': time_dt_126, 'ustar_126': ustar_126, 'L_126': L_126, 'stab_param_126': stab_param_126}
    nc_df_126 = pd.DataFrame(nc_df_dict_126)

    nc_df_123 = nc_df_123.set_index('time_123')
    nc_df_123.index = nc_df_123.index.round('1s')
    # filter out any times which are NOT unstable
    nc_df_123.loc[nc_df_123.stab_param_123 > -0.03] = np.nan

    nc_df_126 = nc_df_126.set_index('time_126')
    nc_df_126.index = nc_df_126.index.round('1s')
    # filter out any times which are NOT unstable
    nc_df_126.loc[nc_df_126.stab_param_126 > -0.03] = np.nan

    df_123 = nc_df_123.merge(csv_df_123, how='outer', left_index=True, right_index=True)
    df_126 = nc_df_126.merge(csv_df_126, how='outer', left_index=True, right_index=True)

    # construct datetime obj for both days with same year day etc. (for colourbar)
    format_index_123 = df_123.index.strftime('%H:%M')
    format_index_126 = df_126.index.strftime('%H:%M')

    index_list_123 = []
    for i in format_index_123:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_123.append(datetime_object)

    index_list_126 = []
    for i in format_index_126:
        datetime_object = dt.datetime.strptime(i, '%H:%M')
        index_list_126.append(datetime_object)

    df_123.index = index_list_123
    df_126.index = index_list_126

    df_123 = df_123.loc[~df_123.index.duplicated()]
    df_126 = df_126.loc[~df_126.index.duplicated()]

    df = pd.concat([df_123, df_126], axis=1)

    resample_df = df.resample('10T', closed='right', label='right').median()

    # find first instance of nc file which isnt a nan

    min_ustar = min([min(df[~np.isnan(df['ustar_123'])].index), min(df[~np.isnan(df['ustar_126'])].index)])
    min_L = min([min(df[~np.isnan(df['L_123'])].index), min(df[~np.isnan(df['L_126'])].index)])
    min_zL = min([min(df[~np.isnan(df['stab_param_123'])].index), min(df[~np.isnan(df['stab_param_126'])].index)])
    min_sigv = min([min(df[~np.isnan(df['sig_v_123'])].index), min(df[~np.isnan(df['sig_v_126'])].index)])

    min_time_df = min(min_ustar, min_L, min_zL, min_sigv)

    max_ustar = max([max(df[~np.isnan(df['ustar_123'])].index), max(df[~np.isnan(df['ustar_126'])].index)])
    max_L = max([max(df[~np.isnan(df['L_123'])].index), max(df[~np.isnan(df['L_126'])].index)])
    max_zL = max([max(df[~np.isnan(df['stab_param_123'])].index), max(df[~np.isnan(df['stab_param_126'])].index)])
    max_sigv = max([max(df[~np.isnan(df['sig_v_123'])].index), max(df[~np.isnan(df['sig_v_126'])].index)])

    max_time_df = max(max_ustar, max_L, max_zL, max_sigv)

    fig, ((ax1, ax2, ax3)) = plt.subplots(nrows=1, ncols=3, sharex=True, figsize=(15,5))

    # plt.suptitle('DOY: ' + nc_df.index[0].strftime('%j'))

    # ax1.scatter(df.index, df['sig_v_123'], color='red', label='123', alpha=0.3, edgecolors='None', marker='.')
    # ax1.scatter(df.index, df['sig_v_126'], color='blue', label='126', alpha=0.3, edgecolors='None', marker='.')
    ax1.plot(df.index[np.where(~np.isnan(df['sig_v_123']))], df['sig_v_123'][np.where(~np.isnan(df['sig_v_123']))[0]],
             marker='o', linewidth=0.5, color='red', label='Cloudy', markersize=4)
    ax1.plot(df.index[np.where(~np.isnan(df['sig_v_126']))], df['sig_v_126'][np.where(~np.isnan(df['sig_v_126']))[0]],
             marker='o', linewidth=0.5, color='blue', label='Clear', markersize=4)

    ax1.legend()
    ax1.set_ylabel('$\sigma$v (m s$^{-1}$)')

    ax2.scatter(df.index, df['ustar_123'], color='red', alpha=0.3, edgecolors='None', marker='.')
    ax2.scatter(df.index, df['ustar_126'], color='blue', alpha=0.3, edgecolors='None', marker='.')

    ax2.plot(resample_df.index, resample_df['ustar_123'], marker='o', linewidth=0.5, color='red', markersize=4)
    ax2.plot(resample_df.index, resample_df['ustar_126'], marker='o', linewidth=0.5, color='blue', markersize=4)
    # ax2.scatter(resample_df.index, resample_df['ustar_123'], color='red', edgecolors='None', marker='o')

    ax2.set_ylabel('u$_{*}$ (m s$^{-1}$)')

    # ax4.scatter(df.index, df['L_123']*-1, color='red', alpha=0.3, edgecolors='None', marker='.')
    # ax4.scatter(df.index, df['L_126'] * -1, color='blue', alpha=0.3, edgecolors='None', marker='.')
    #
    # ax4.plot(resample_df.index, resample_df['L_123']*-1, marker='o', linewidth=0.5, color='red', markersize=4)
    # ax4.plot(resample_df.index, resample_df['L_126'] * -1, marker='o', linewidth=0.5, color='blue', markersize=4)
    #
    # ax4.set_ylabel('- L (m)')
    # ax4.set_yscale('log')
    # ax4.set_ylim(ax3.get_ylim()[::-1])

    ax3.scatter(df.index, df['stab_param_123']*-1, color='red', alpha=0.3, edgecolors='None', marker='.')
    ax3.scatter(df.index, df['stab_param_126'] * -1, color='blue', alpha=0.3, edgecolors='None', marker='.')

    ax3.plot(resample_df.index, resample_df['stab_param_123']*-1, marker='o', linewidth=0.5, color='red', markersize=4)
    ax3.plot(resample_df.index, resample_df['stab_param_126'] * -1, marker='o', linewidth=0.5, color='blue', markersize=4)

    ax3.set_ylabel('- z$_{f}$/L', labelpad=-5)
    ax3.set_yscale('log')
    ax3.set_ylim(ax3.get_ylim()[::-1])

    ax1.set_xlim(min_time_df, max_time_df)
    ax2.set_xlim(min_time_df, max_time_df)
    ax3.set_xlim(min_time_df, max_time_df)
    # ax4.set_xlim(min_time_df, max_time_df)

    ax3.xaxis.set_major_formatter(DateFormatter('%H'))
    # ax4.xaxis.set_major_formatter(DateFormatter('%H'))

    plt.gcf().autofmt_xdate()
    plt.tight_layout()


    fig.subplots_adjust(wspace=0.22, hspace=0)

    # plt.show()
    plt.savefig('C:/Users/beths/OneDrive - University of Reading/Working Folder/in_vars.png', bbox_inches='tight')

    print('end')



# nc_filepath = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/142/LASMkII_Fast_IMU_2016142_1min_sa10min.nc'
# footprint_csv_path = 'D:/Documents/scintillometer_footprints/scint_fp/test_outputs/met_inputs_minutes_142.csv'

# nc_filepath = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/scint_data_testing/data/2016/London/L1/IMU/DAY/111/LASMkII_Fast_IMU_2016111_1min_sa10min.nc'
# footprint_csv_path = 'D:/Documents/scintillometer_footprints/scint_fp/test_outputs/met_inputs_minutes_111.csv'

nc_filepath_123 = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/123/LASMkII_Fast_IMU_2016123_1min_sa10min.nc'
footprint_csv_path_123 = 'C:/Users/beths/Desktop/LANDING/fp_output/met_inputs_minutes_123.csv'

nc_filepath_126 = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/2016/London/L1/IMU/DAY/126/LASMkII_Fast_IMU_2016126_1min_sa10min.nc'
footprint_csv_path_126 = 'C:/Users/beths/Desktop/LANDING/fp_output/met_inputs_minutes_126.csv'

plot_footprint_model_inputs(nc_filepath_123, footprint_csv_path_123, nc_filepath_126, footprint_csv_path_126)
