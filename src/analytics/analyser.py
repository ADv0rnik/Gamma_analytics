import asyncio
import numpy as np
from typing import Tuple

from src.analytics.run_analytics import calculate_count_rate, calculate_count_rate_angular
from src.config import IS_FIXED_DISTANCE, src_y_probe
from src.utils import create_dataframe


class Analyser:
    def __init__(
            self,
            activity: float,
            include_angles: bool,
            coordinates: Tuple[np.ndarray, np.ndarray] = None,
            dist_predefined: bool = IS_FIXED_DISTANCE
    ):
        self.coordinates = coordinates
        self.dist_predefined = dist_predefined
        self.include_angles = include_angles  # allows to take into account angular efficiency
        self.activity = activity

    async def __get_dist_arrays(self):
        jobs = []
        for probe in src_y_probe.values():
            jobs.append(asyncio.create_task(calculate_count_rate(
                self.coordinates[0],
                self.coordinates[1],
                src_y=probe,
                activity=self.activity
            )))
        return await asyncio.gather(*jobs)

    @staticmethod
    async def __get_from_poisson(simulation_data):
        pois_data = np.zeros_like(simulation_data)
        for i in range(len(simulation_data)):
            pois_data[i] = np.random.poisson(simulation_data[i], 1)[0]
        return pois_data

    async def construct_data(self):
        data_dict = {'x': self.coordinates[0], 'y': self.coordinates[1]}
        if not self.include_angles:
            if self.dist_predefined:
                sim_data = await calculate_count_rate(
                    self.coordinates[0],
                    self.coordinates[1],
                    self.activity
                )
                data_dict["sim_data"] = sim_data
                data_dict["pois_data"] = await self.__get_from_poisson(sim_data)
            else:
                dist_dataset = await self.__get_dist_arrays()
                for i, item in enumerate(dist_dataset):
                    data_dict[f"sim_data_{src_y_probe[i]}"] = item
            return await create_dataframe(data_dict)
        else:
            sim_data = await calculate_count_rate_angular(
                self.coordinates[0],
                self.coordinates[1],
                self.activity
            )
            data_dict["sim_data"] = sim_data
            data_dict["pois_data"] = await self.__get_from_poisson(sim_data)
            return await create_dataframe(data_dict)
