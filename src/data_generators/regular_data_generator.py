import asyncio
import numpy as np

from src.data_generators.base_data_generator import BaseDataGenerator
from src.settings.config import (
    SCALE,
    BRANCH_RATIO,
    IS_FIXED_DISTANCE,
    src_y_probe,
    mu_air,
    SRC_X,
    SRC_Y,
    EFFICIENCY
)
from src.utils import create_dataframe
from .generators_utils import gen_background


class RegularDataGenerator(BaseDataGenerator):
    def __init__(self, **kwargs):
        self.coordinates = kwargs["coordinates"]
        self.dist_predefined = IS_FIXED_DISTANCE
        self.activity = kwargs["activity"]
        self.src_x = SRC_X,
        self.src_y = SRC_Y,
        self.eff = EFFICIENCY

    async def __get_dist_arrays(self):
        jobs = []
        for probe in src_y_probe.values():
            jobs.append(asyncio.create_task(self.generate_count_rate(
                self.coordinates[0],
                self.coordinates[1],
                src_y=probe,
                activity=self.activity
            )))
        return await asyncio.gather(*jobs)

    async def generate_data(self):
        data_dict = {'x': self.coordinates[0], 'y': self.coordinates[1]}
        if self.dist_predefined:
            gen_data = await self.generate_count_rate(
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

    async def generate_count_rate(
            self,
            x_position,
            y_position,
            activity,
            src_y=SRC_Y,
    ):
        dist = np.sqrt((x_position - self.src_x) ** 2 + (y_position - src_y) ** 2)
        bkg_arr = await gen_background(len(dist))
        count_rate = (activity * SCALE * BRANCH_RATIO * self.eff * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
        return np.round(count_rate, 2) + bkg_arr