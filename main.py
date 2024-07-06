import asyncio
import os

import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from src.utils import DataFormatter
from src.config import (
    BRANCH_RATIO,
    EFFICIENCY,
    SRC_X,
    SRC_Y,
    SCALE,
    IS_FIXED_DISTANCE,
    src_y_probe,
    NORMALIZE,
    BASE_DIR
)

x_coord = np.arange(-300, 300, 1)  # 1s of measurements
y_coord = np.zeros(len(x_coord))

ATTENUATION_FILE = os.path.join(BASE_DIR, "nuclib", "attenuation_table.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

formatter = DataFormatter(ATTENUATION_FILE)
data = formatter.get_dataframe()

mu_air = 0.0015 # TODO: Needs to make an interpolator class for different types of approximation (Factory??)


async def calculate_fluence_rate(x_position, y_position, activity, src_x=SRC_X, src_y=SRC_Y, eff=EFFICIENCY):
    dist = np.sqrt((x_position - src_x) ** 2 + (y_position - src_y) ** 2)
    fluence_rate = (activity * SCALE * BRANCH_RATIO * eff * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
    return fluence_rate


# async def calculate_count_rate(x_position, y_position, activity, src_x=SRC_X, src_y=SRC_Y, eff=EFFICIENCY):
#     dist = np.sqrt((x_position - src_x) ** 2 + (y_position - src_y) ** 2)
#     fluence_rate = (activity * SCALE * BRANCH_RATIO * eff * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
#     return fluence_rate


async def create_dataframe(data: dict) -> pd.DataFrame:
    return pd.DataFrame(data)


def make_graph(data: pd.DataFrame, dist_predefined=IS_FIXED_DISTANCE, normalize=NORMALIZE) -> None:
    figure, ax = plt.subplots(figsize=(16, 6))
    x = data["x"]
    columns = [column for column in data.columns if column.startswith('sim') and not column.endswith('n')]
    columns_norm = [column for column in data.columns if column.startswith('sim') and column.endswith('n')]
    try:
        if dist_predefined:
            y = data["sim_data"]
            ax.plot(x, y, lw=1)
            plt.savefig(OUTPUT_DIR + "/" + "fig_single.png")
            # plt.show()
        elif normalize:
            data.plot(x="x", y=columns_norm, xlabel="Distance / m", ylabel="Fluence rate", grid=True)
            plt.savefig(OUTPUT_DIR + "/" + "fig_multi_norm_1.png")
            # plt.show()
        else:
            data.plot(x="x", y=columns)
            plt.savefig(OUTPUT_DIR + "/" + "fig_multi.png")
    except TypeError as e:
        print(f"An error occurred while creating plot: {e}")


async def get_arrays():
    jobs = []
    for probe in src_y_probe.values():
        jobs.append(asyncio.create_task(calculate_fluence_rate(x_coord, y_coord, src_y=probe, activity=100)))
    return await asyncio.gather(*jobs)


async def construct_data(dist_predefined=IS_FIXED_DISTANCE):
    data_dict = {'x': x_coord, 'y': y_coord}
    if dist_predefined:
        data_dict["sim_data"] = await calculate_fluence_rate(x_coord, y_coord, activity=100)
    else:
        dataset = await get_arrays()
        for i, item in enumerate(dataset):
            data_dict[f"sim_data_{src_y_probe[i]}"] = item
    return await create_dataframe(data_dict)


async def make_normalization(data_to_normalize: pd.DataFrame):
    only_sim_data = data_to_normalize.iloc[:, 2::1]
    norm_data = only_sim_data.apply(lambda x: x / x.max(), axis=0)
    for i, column in enumerate(norm_data.columns):
        norm_data.rename(columns={column: column + "_n"}, inplace=True)
    return pd.concat([data_to_normalize, norm_data], axis=1)


async def main():
    df = await construct_data()
    # df.to_csv("simulated_data.csv")
    if NORMALIZE:
        df = await make_normalization(df)
    print(df)
    make_graph(df)


if __name__ == '__main__':
    asyncio.run(main())
