import matplotlib.pyplot as plt
import pandas as pd
import os

from scint_fp.functions.sa_lc_fractions import lc_fractions_in_sa as lc


def plot_combined_raster(save_path):
    """

    :return:
    """

    df_sa_columns = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']

    P13_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/IMU_BTT.tif'
    P13_sa_df = lc.landcover_fractions_in_SA_weighted(P13_file, save_path)

    P13_df_sa_data = [[P13_sa_df.loc[1]['sa_weight_percent'],
                       P13_sa_df.loc[2]['sa_weight_percent'],
                       P13_sa_df.loc[3]['sa_weight_percent'],
                       P13_sa_df.loc[4]['sa_weight_percent'],
                       P13_sa_df.loc[5]['sa_weight_percent'],
                       P13_sa_df.loc[6]['sa_weight_percent'],
                       P13_sa_df.loc[7]['sa_weight_percent']]]

    P13_sa_df = pd.DataFrame(P13_df_sa_data, columns=df_sa_columns)
    P13_sa_df.index = ['IMU_BTT']

    P15_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/SCT_SWT.tif'
    P15_sa_df = lc.landcover_fractions_in_SA_weighted(P15_file, save_path)

    P15_df_sa_data = [[P15_sa_df.loc[1]['sa_weight_percent'],
                       P15_sa_df.loc[2]['sa_weight_percent'],
                       P15_sa_df.loc[3]['sa_weight_percent'],
                       P15_sa_df.loc[4]['sa_weight_percent'],
                       P15_sa_df.loc[5]['sa_weight_percent'],
                       P15_sa_df.loc[6]['sa_weight_percent'],
                       P15_sa_df.loc[7]['sa_weight_percent']]]

    P15_sa_df = pd.DataFrame(P15_df_sa_data, columns=df_sa_columns)
    P15_sa_df.index = ['SCT_SWT']

    P11_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/BTT_BCT.tif'
    P11_sa_df = lc.landcover_fractions_in_SA_weighted(P11_file, save_path)

    P11_df_sa_data = [[P11_sa_df.loc[1]['sa_weight_percent'],
                       P11_sa_df.loc[2]['sa_weight_percent'],
                       P11_sa_df.loc[3]['sa_weight_percent'],
                       P11_sa_df.loc[4]['sa_weight_percent'],
                       P11_sa_df.loc[5]['sa_weight_percent'],
                       P11_sa_df.loc[6]['sa_weight_percent'],
                       P11_sa_df.loc[7]['sa_weight_percent']]]

    P11_sa_df = pd.DataFrame(P11_df_sa_data, columns=df_sa_columns)
    P11_sa_df.index = ['BTT_BCT']

    P12_file = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/BCT_IMU.tif'
    P12_sa_df = lc.landcover_fractions_in_SA_weighted(P12_file, save_path)

    P12_df_sa_data = [[P12_sa_df.loc[1]['sa_weight_percent'],
                       P12_sa_df.loc[2]['sa_weight_percent'],
                       P12_sa_df.loc[3]['sa_weight_percent'],
                       P12_sa_df.loc[4]['sa_weight_percent'],
                       P12_sa_df.loc[5]['sa_weight_percent'],
                       P12_sa_df.loc[6]['sa_weight_percent'],
                       P12_sa_df.loc[7]['sa_weight_percent']]]
    # a dataframe of one source area
    P12_sa_df = pd.DataFrame(P12_df_sa_data, columns=df_sa_columns)
    P12_sa_df.index = ['BCT_IMU']

    combine = pd.concat([P13_sa_df, P12_sa_df, P11_sa_df, P15_sa_df])

    color_list = ["dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]

    fig, ax = plt.subplots(figsize=(12, 12))

    combine.plot(ax=ax, kind='bar', stacked=True, color=color_list, width=0.85)

    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax.set_ylim(0, 100)
    ax.set_xlim(-.5, len(combine.index) - 0.5)

    plt.savefig(save_path + 'landcover_fractions.png', bbox_inches='tight')
    # plt.show()


if __name__ == '__main__':

    save_path = os.getcwd().replace('\\', '/') + '/'

    plot_combined_raster(save_path=save_path)

    print('end')
