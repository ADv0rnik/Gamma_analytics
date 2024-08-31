import asyncio

import numpy as np

from src.data_generators.base_data_generator import BaseDataGenerator
from src.config import (
    SCALE,
    BRANCH_RATIO,
    IS_FIXED_DISTANCE,
    mu_air,
    SRC_X,
    SRC_Y,
    EFFICIENCY,
    BKG_ACTIVITY, EFF_FILE, src_y_probe
)
from src.tools.data_formatter import formatter
from src.tools.interpolators import EfficiencyInterpolator
from src.utils import create_dataframe, calculate_angles


class AngularDataGenerator(BaseDataGenerator):
    def __init__(self, **kwargs):
        self.coordinates = kwargs["coordinates"]
        self.dist_predefined = IS_FIXED_DISTANCE
        self.activity = kwargs["activity"]
        self.background = BKG_ACTIVITY,
        self.src_x = SRC_X,
        self.src_y = SRC_Y,
        self.eff = EFFICIENCY

    async def __get_dist_arrays(self):
        jobs = []
        for probe in src_y_probe.values():
            jobs.append(asyncio.create_task(self.generate_count_rate_angular(
                self.coordinates[0],
                self.coordinates[1],
                src_y=probe,
                activity=self.activity
            )))
        return await asyncio.gather(*jobs)

    async def generate_data(self):
        data_dict = {'x': self.coordinates[0], 'y': self.coordinates[1]}
        if self.dist_predefined:
            gen_data = await self.generate_count_rate_angular(
                self.coordinates[0],
                self.coordinates[1],
                self.activity
            )
            data_dict["generic_count_rate"] = gen_data
            data_dict["pois_data"] = await self.get_from_poisson(gen_data)

        else:
            dist_dataset = await self.__get_dist_arrays()
            for i, item in enumerate(dist_dataset):
                data_dict[f"generic_data_{src_y_probe[i]}"] = item
        return await create_dataframe(data_dict)

    async def get_from_poisson(self, generated_data):
        """
        This function generates random numbers from a Poisson distribution with a mean of ``generated_data``.
        The Poisson distribution models the probability of a given number of events occurring in a fixed interval of time or space,
        given that these events occur with a known average rate.
        :param generated_data: simulated from count rate model dataset
        :return: array of poisson random count numbers
        """
        pois_data = np.zeros_like(generated_data)
        for i in range(len(generated_data)):
            pois_data[i] = np.random.poisson(generated_data[i], 1)[0]
        return pois_data

    async def generate_count_rate_angular(
            self,
            x_position,
            y_position,
            activity,
            src_y=SRC_Y
    ):
        """
        This function is taking into account an angular distribution of the detector efficiency.
        :param x_position: numpy array of x coordinates
        :param y_position: numpy array of y coordinates
        :param activity: Decimal value of the source activity performed in Bq
        :param src_y: y position of the orphan source
        :return: array of the angular_count_rate
        """
        efficiency_df = formatter.get_dataframe(EFF_FILE)
        efficiency_interpolator = EfficiencyInterpolator(efficiency_df)

        dist = np.sqrt((x_position - self.src_x) ** 2 + (y_position - src_y) ** 2)
        calc_angles = await calculate_angles(x_position, y_position, SRC_X, src_y)
        eff_rel = efficiency_interpolator.interpolate(calc_angles)

        angular_count_rate = (activity * SCALE * BRANCH_RATIO * self.eff * eff_rel * np.exp(-mu_air * dist)) / (
                    4 * np.pi * dist ** 2)
        return np.round(angular_count_rate, 2) + self.background

