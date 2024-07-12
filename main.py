import asyncio

from src.analytics.analyser import Analyser
from src.analytics.run_analytics import make_normalization
from src.presentation.plot_maker import make_graph
from src.config import (
    x_coord,
    y_coord,
    NORMALIZED,
)


async def run_analytics(make_plot=True):
    analyser = Analyser(
        coordinates=(x_coord, y_coord),
        include_angles=False
    )

    df = await analyser.construct_data()
    if NORMALIZED:
        df = await make_normalization(df)
    if make_plot:
        make_graph(df)
    else:
        df.to_csv("simulated_data_eff_ref_eff_rel.csv")


if __name__ == '__main__':
    asyncio.run(run_analytics())
