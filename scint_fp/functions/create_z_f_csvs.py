# imports
import pandas as pd

from scint_flux.functions import read_calculated_fluxes
from scint_flux import look_up

scint_path = 12
DOY_list = [2016134]

"""
# read in csv with days
DOY_df = pd.read_csv('C:/Users/beths/OneDrive - University of Reading/Paper 2/categorize_days/days_to_be_read_in.csv')
# take only days of the target path
scint_path_string = 'P' + str(scint_path)
df_subset = DOY_df.iloc[np.where(DOY_df[scint_path_string] == 1)[0]]
df_subset['DOY_string'] = df_subset.year.astype(str) + df_subset.DOY.astype(str)
df_subset['DOY_string'] = df_subset['DOY_string'].astype(int)
DOY_list = df_subset.DOY_string.to_list()
"""

var_list = ['QH', 'kdown']

# time_res = '1min_sa10min'
# time_res = '1min'
time_res = '1min_sa10_mins_ending'

pair_id = look_up.scint_path_numbers[scint_path]

for DOY in DOY_list:
    # read the observations
    df = read_calculated_fluxes.extract_data(doy_list=[DOY],
                                             pair_id=pair_id,
                                             var_list=var_list,
                                             time_res=time_res)

    z_f_vals = df.z_f.dropna().resample('60T', closed='right', label='right').mean()
    z_f_vals.to_csv(
        'D:/Documents/scint_UM100/scint_UM100/data_retreval/z_f_csvs/z_f_' + str(scint_path) + '_' + str(DOY) + '.csv')

    print('end')
