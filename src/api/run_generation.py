from typing import Any
from src.data_generators.angular_data_generator import AngularDataGenerator
from src.data_generators.regular_data_generator import RegularDataGenerator
from src.data_generators.velocity_data_generator import VelocityDataGenerator
from src.presentation.plot_maker import PlotMaker
from src.config import (
    NORMALIZED,
    IS_FIXED_DISTANCE
)
from src.utils import make_normalization


async def run_data_generation(**kwargs) -> dict[str, Any]:
    default_data_generator = None
    if kwargs["include_angles"]:
        default_data_generator = AngularDataGenerator(**kwargs)
    if kwargs["add_speed"]:
        default_data_generator = VelocityDataGenerator(**kwargs)
    else:
        default_data_generator = RegularDataGenerator(**kwargs)
        dataframe = await default_data_generator.generate_data()
        if NORMALIZED:
            dataframe = await make_normalization(dataframe)

        if kwargs["make_plot"]:
            plot_generator = PlotMaker(dataframe)
            fig = plot_generator.plot_default_count_rate(
                normalized=NORMALIZED,
                dist_predefined=IS_FIXED_DISTANCE
            )
            return {
                "figure": fig,
                "data": dataframe
            }
        else:
            return {
                "data": dataframe
            }
