from calendar import isleap
import os

from scint_eval.functions import file_read
from scint_eval.functions import sort_model_wind
from scint_eval.functions import sort_model
from scint_eval.functions import array_retrieval


def collect_model_inputs(DOYstart, DOYstop, run, variable, height, model_site, model_grid_letter, path_number):
    """
    find all the needed files from the model
    :return:
    """

    if run == '21Z':
        # string out of the chosen starting DOY and year
        str_year = str(DOYstart)[:4]
        str_DOY = str(DOYstart)[4:]
        # if the start DOY is the first day of the year:
        if str_DOY == '001':
            # we now have to start with the year before the chosen year
            new_start_year = int(str_year) - 1
            # to get the start DOY, we need to know what the last DOY of the previous year is
            # so is it a leap year (366 days) or not?
            if isleap(new_start_year):
                # leap year
                new_start_DOY = 366
            else:
                # normal year
                new_start_DOY = 365
            # combining the new start year and new DOY start
            DOYstart_mod = int(str(new_start_year) + str(new_start_DOY))
        else:
            new_start_DOY = str(int(str_DOY) - 1).zfill(3)
            DOYstart_mod = int(str_year + new_start_DOY)
    else:
        DOYstart_mod = DOYstart
    DOYstop_mod = DOYstop - 1

    ####################################################################################################################

    file_dict_ukv = file_read.finding_files('new',
                                            'ukv',
                                            DOYstart_mod,
                                            DOYstop_mod,
                                            model_site,
                                            run,
                                            'Davis',
                                            '15min',
                                            variable,
                                            'L2',
                                            model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                            )

    # ordering UKV model files
    # file_read.py
    files_ukv = file_read.order_model_stashes('ukv', file_dict_ukv, variable)

    save_folder = '../plots/' + str(DOYstart) + '_' + str(DOYstop) + '_' + variable + '_' + model_site + '_' + str(
        path_number) + '/'
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)



    if variable == 'wind':

        ukv_sort_output = sort_model_wind.sort_models_wind(variable, 'ukv', files_ukv, height, DOYstart, DOYstop,
                                                           model_site, save_folder, 'new',
                                                           grid_choice=model_grid_letter)

        # define dict for included models
        included_models_ws = {}
        # stringtimelon, stringwindlon, lontimedict, lonwinddict, modheightvaluelon
        group_ukv_ws = [ukv_sort_output[3], ukv_sort_output[4], ukv_sort_output[0], ukv_sort_output[1],
                        ukv_sort_output[6]]

        included_models_wd = {}
        # stringtimelon, stringdirlon, lontimedict, londirdict, modheightvaluelon
        group_ukv_wd = [ukv_sort_output[3], ukv_sort_output[5], ukv_sort_output[0], ukv_sort_output[2],
                        ukv_sort_output[6]]

        # append to dict
        included_models_ws['ukv'] = group_ukv_ws
        included_models_wd['ukv'] = group_ukv_wd

        mod_time_ws, mod_vals_ws = array_retrieval.retrive_arrays_model(included_models_ws, 'ukv')
        mod_time_wd, mod_vals_wd = array_retrieval.retrive_arrays_model(included_models_wd, 'ukv')

        assert mod_time_wd.all() == mod_time_ws.all()

        mod_time = mod_time_ws
        mod_vals = {'ws': mod_vals_ws, 'wd': mod_vals_wd}
        mod_height = ukv_sort_output[6]


    else:

        ukv_sort_output = sort_model.sort_models(variable, 'ukv', files_ukv, height, DOYstart, DOYstop,
                                                           model_site, save_folder, 'new',
                                                           grid_choice=model_grid_letter)

        # define dict for included models
        included_models = {}

        # stringtimelon, stringtemplon, lontimedict, lontempdict, modheightvaluelon
        group_ukv = [ukv_sort_output[5], ukv_sort_output[6], ukv_sort_output[0], ukv_sort_output[1], ukv_sort_output[10]]
        # append to dict
        included_models['ukv'] = group_ukv

        mod_time, mod_vals = array_retrieval.retrive_arrays_model(included_models, 'ukv')
        mod_height = ukv_sort_output[10]


    return mod_time, mod_vals, mod_height
