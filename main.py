import asyncio

from src.analytics.run_analytics import calculate_fluence_rate, make_normalization, calculate_fluence_rate_angular
from src.presentation.plot_maker import make_graph
from src.utils import create_dataframe
from src.config import (
    IS_FIXED_DISTANCE,
    src_y_probe,
    x_coord,
    y_coord,
    NORMALIZED,
)


async def get_dist_arrays():
    jobs = []
    for probe in src_y_probe.values():
        jobs.append(asyncio.create_task(calculate_fluence_rate(x_coord, y_coord, src_y=probe, activity=100)))
    return await asyncio.gather(*jobs)


async def construct_data(dist_predefined=IS_FIXED_DISTANCE):
    data_dict = {'x': x_coord, 'y': y_coord}
    if dist_predefined:
        data_dict["sim_data"] = await calculate_fluence_rate_angular(x_coord, y_coord, activity=100)
    else:
        dist_dataset = await get_dist_arrays()
        for i, item in enumerate(dist_dataset):
            data_dict[f"sim_data_{src_y_probe[i]}"] = item
    return await create_dataframe(data_dict)


async def run_analytics(make_plot=True):
    df = await construct_data()
    if NORMALIZED:
        df = await make_normalization(df)
    if make_plot:
        make_graph(df)
    else:
        df.to_csv("simulated_data_eff_ref_eff_rel.csv")


if __name__ == '__main__':
    asyncio.run(run_analytics())
