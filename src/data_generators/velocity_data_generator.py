import asyncio

import numpy as np

from src.data_generators.base_data_generator import BaseDataGenerator
from src.settings.config import (
    SCALE,
    BRANCH_RATIO,
    IS_FIXED_DISTANCE,
    mu_air,
    SRC_X,
    SRC_Y,
    EFFICIENCY,
    BKG_COUNT_RATE,
    src_y_probe
)
from src.utils import create_dataframe


class VelocityDataGenerator(BaseDataGenerator):
    def __init__(self, **kwargs):
        self.coordinates = kwargs["coordinates"]
        self.dist_predefined = IS_FIXED_DISTANCE
        self.activity = kwargs["activity"]
        self.background = BKG_COUNT_RATE,
        self.src_x = SRC_X,
        self.eff = EFFICIENCY
        self.speed = kwargs["speed"]
        self.start_point = kwargs["road_span"]
        self.span = kwargs["num_points"]
        self.time = kwargs["time"]

    async def __get_dist_arrays(self):
        jobs = []
        for probe in src_y_probe.values():
            jobs.append(asyncio.create_task(self.__generate_count_rate_acquisition_time(src_y=probe)))
        return await asyncio.gather(*jobs)

    async def generate_data(self):
        data_dict = {}
        if self.dist_predefined:
            gen_data, x_coord, y_coord = await self.__generate_count_rate_acquisition_time()
            data_dict["x"] = np.round(x_coord,0)
            data_dict["y"] = y_coord
            data_dict["generic_count_rate"] = gen_data
            data_dict["pois_data"] = await self.get_from_poisson(gen_data)
        else:
            dist_dataset = await self.__get_dist_arrays()
            for i, item in enumerate(dist_dataset):
                data_dict["x"] = np.round(item[1],0)
                data_dict["y"] = item[2]
                data_dict[f"generic_data_{src_y_probe[i]}"] = item[0]
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

    async def __generate_count_rate_acquisition_time(self, src_y=SRC_Y):
        x_position = np.arange(self.start_point, self.start_point + (self.speed * self.time * self.span), self.speed * self.time)
        y_position = np.zeros(self.span)

        dist = np.sqrt((x_position - self.src_x) ** 2 + (y_position - src_y) ** 2)
        count_rate = ((self.activity * SCALE * BRANCH_RATIO * EFFICIENCY * np.exp(-mu_air * dist)) / (
                    4 * np.pi * dist ** 2)) * self.time

        return np.round(count_rate, 2) + self.background, x_position, y_position