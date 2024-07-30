import numpy as np
import pandas as pd

from src.tools.interpolators import EfficiencyInterpolator
from src.tools.data_formatter import formatter
from src.utils import calculate_angles
from src.config import (
    SCALE,
    BRANCH_RATIO,
    mu_air,
    SRC_X,
    SRC_Y,
    EFFICIENCY,
    EFF_FILE,
    BKG_ACTIVITY
)


async def calculate_count_rate(
        x_position,
        y_position,
        activity,
        background=BKG_ACTIVITY,
        src_x=SRC_X,
        src_y=SRC_Y,
        eff=EFFICIENCY
):
    dist = np.sqrt((x_position - src_x) ** 2 + (y_position - src_y) ** 2)
    count_rate = (activity * SCALE * BRANCH_RATIO * eff * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
    return np.round(count_rate + background, 1)


async def calculate_count_rate_angular(
        x_position,
        y_position,
        activity,
        background=BKG_ACTIVITY,
        src_x=SRC_X,
        src_y=SRC_Y,
        eff=EFFICIENCY):
    """
    This function is taking into account an angular distribution of the detector efficiency.
    :param x_position: numpy array of x coordinates
    :param y_position: numpy array of y coordinates
    :param activity: Decimal value of the source activity performed in Bq
    :param background: background activity performed in Bq
    :param src_x: x position of the orphan source
    :param src_y: y position of the orphan source
    :param eff: reference efficiency of the detector
    :return: array of the angular_count_rate
    """
    efficiency_df = formatter.get_dataframe(EFF_FILE)
    efficiency_interpolator = EfficiencyInterpolator(efficiency_df)

    dist = np.sqrt((x_position - src_x) ** 2 + (y_position - src_y) ** 2)
    calc_angles = await calculate_angles(x_position, y_position, SRC_X, SRC_Y)
    eff_rel = efficiency_interpolator.interpolate(calc_angles)

    angular_count_rate = (activity * SCALE * BRANCH_RATIO * eff * eff_rel * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
    return np.round(angular_count_rate, 1) + background


async def make_normalization(data_to_normalize: pd.DataFrame):
    only_sim_data = data_to_normalize.iloc[:, 2::1]
    norm_data = only_sim_data.apply(lambda x: x / x.max(), axis=0)
    for i, column in enumerate(norm_data.columns):
        norm_data.rename(columns={column: column + "_n"}, inplace=True)
    return pd.concat([data_to_normalize, norm_data], axis=1)
