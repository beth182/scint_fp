# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def lc_polar_plot(path_name,
                  df):
    """

    :param path_name:
    :param df: landcover pandas dataframe
    :return:
    """

    # set the colours of the path
    colour_dict = {'BCT_IMU': 'red', 'SCT_SWT': 'mediumorchid', 'IMU_BTT': 'green', 'BTT_BCT': 'blue'}
    color_here = colour_dict[path_name]

    # deal with masked values in pandas df col
    for col_name in df.columns:
        df[col_name].iloc[~np.isin(np.arange(len(df)), np.where(df[col_name] >= 0)[0])] = 0

    # combine vegitation into one lc type
    df['Veg'] = df['Grass'] + df['Deciduous'] + df['Evergreen'] + df['Shrub']

    # define the angles of the sectors in the plot
    interval = 360 / len(df)
    start = interval / 2
    thetas = np.arange(start, 360, interval)
    assert len(thetas) == len(df)
    df['thetas'] = thetas

    # define width of sector
    width = [360 / len(df) for _ in range(len(df))]

    # set up plot
    fig = px.bar_polar(template="simple_white")

    # add each bar one by one

    fig.add_trace(go.Barpolar(
        r=list(df['Building']),
        theta=list(df['thetas']),
        marker_color='dimgrey',
        width=width,
        name='Building'))

    fig.add_trace(go.Barpolar(
        r=list(df['Impervious']),
        theta=list(df['thetas']),
        marker_color='lightgrey',
        width=width,
        name='Impervious'))

    fig.add_trace(go.Barpolar(
        r=list(df['Water']),
        theta=list(df['thetas']),
        marker_color='deepskyblue',
        width=width,
        name='Water'))

    fig.add_trace(go.Barpolar(
        r=list(df['Veg']),
        theta=list(df['thetas']),
        marker_color='lawngreen',
        width=width,
        name='Vegetation'))

    # fix layout
    layout_options = {"legend_x": 0.15,
                      "legend_y": 0.5,
                      # "polar_radialaxis_ticks": "",
                      # "polar_radialaxis_showticklabels": False,
                      # "polar_angularaxis_ticks": "",
                      # "polar_angularaxis_showticklabels": False,
                      "font": {'size': 20},
                      "grid": {'ygap': 0}
                      }

    fig.update_layout(**layout_options)

    fig.update_traces(marker_line={'color': 'black'})
    fig.update_polars(radialaxis=dict(range=[0, 100],
                                      tickvals=[20, 40, 60, 80],
                                      # angle=90,
                                      # tickangle=90,
                                      linewidth=5,
                                      linecolor=color_here,
                                      color=color_here),
                      angularaxis=dict(linewidth=15,
                                       layer="below traces",
                                       linecolor=color_here,
                                       color=color_here,
                                       tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                                       ticktext=['N', 'N-E', 'E', 'S-E', 'S', 'S-W', 'W', 'N-W']
                                       ))

    # show figure and save manually
    fig.show()
