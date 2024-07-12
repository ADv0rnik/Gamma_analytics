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
    EFF_FILE
)


async def calculate_fluence_rate(x_position, y_position, activity, src_x=SRC_X, src_y=SRC_Y, eff=EFFICIENCY):
    dist = np.sqrt((x_position - src_x) ** 2 + (y_position - src_y) ** 2)
    fluence_rate = (activity * SCALE * BRANCH_RATIO * eff * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
    return fluence_rate


async def calculate_fluence_rate_angular(x_position, y_position, activity, src_x=SRC_X, src_y=SRC_Y, eff=EFFICIENCY):
    efficiency_df = formatter.get_dataframe(EFF_FILE)
    efficiency_interpolator = EfficiencyInterpolator(efficiency_df)

    dist = np.sqrt((x_position - src_x) ** 2 + (y_position - src_y) ** 2)
    calc_angles = calculate_angles(x_position, y_position, SRC_X, SRC_Y)
    eff_rel = efficiency_interpolator.interpolate(calc_angles)

    angular_fluence_rate = (activity * SCALE * BRANCH_RATIO * eff * eff_rel * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
    return angular_fluence_rate


async def make_normalization(data_to_normalize: pd.DataFrame):
    only_sim_data = data_to_normalize.iloc[:, 2::1]
    norm_data = only_sim_data.apply(lambda x: x / x.max(), axis=0)
    for i, column in enumerate(norm_data.columns):
        norm_data.rename(columns={column: column + "_n"}, inplace=True)
    return pd.concat([data_to_normalize, norm_data], axis=1)
