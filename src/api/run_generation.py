import pandas as pd

from typing import Any
from src.data_generators.angular_data_generator import AngularDataGenerator
from src.data_generators.regular_data_generator import RegularDataGenerator
from src.data_generators.velocity_data_generator import VelocityDataGenerator
from src.data_generators.base_data_generator import BaseDataGenerator
from src.presentation.plot_maker import PlotMaker
from src.config import (
    NORMALIZED,
    IS_FIXED_DISTANCE,
    IS_POISSON
)
from src.utils import make_normalization


async def run_data_generation(**kwargs) -> dict[str, Any]:
    if kwargs["include_angles"]:
        default_data_generator = AngularDataGenerator(**kwargs)
    if kwargs["add_speed"]:
        velocity_data_generator = VelocityDataGenerator(**kwargs)
        df = await return_data_from_generator(velocity_data_generator)
        if kwargs["make_plot"]:
            return await return_dataplot(df, speed=kwargs["speed"], time=kwargs["time"])
        else:
            return {"data": df}
    else:
        default_data_generator = RegularDataGenerator(**kwargs)
        df = await return_data_from_generator(default_data_generator)

        if kwargs["make_plot"]:
            return await return_dataplot(df)
        else:
            return {"data": df}


async def return_data_from_generator(data_generator: BaseDataGenerator) -> pd.DataFrame:
    dataframe = await data_generator.generate_data()
    if NORMALIZED:
        dataframe = await make_normalization(dataframe)
    return dataframe


async def return_dataplot(dataframe: pd.DataFrame, **kwargs) -> dict[str, Any]:
    plot_generator = PlotMaker(dataframe)
    if IS_POISSON:
        fig = plot_generator.plot_poisson(
            speed=kwargs["speed"],
            time=kwargs["time"]
        )
    else:
        fig = plot_generator.plot_count_rate(
            normalized=NORMALIZED,
            dist_predefined=IS_FIXED_DISTANCE
        )
    return {
        "figure": fig,
        "data": dataframe
    }

