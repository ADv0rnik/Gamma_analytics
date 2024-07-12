import asyncio
from typing import Tuple

from src.analytics.run_analytics import calculate_fluence_rate
from src.config import IS_FIXED_DISTANCE, src_y_probe
from src.utils import create_dataframe


class Analyser:
    def __init__(
            self,
            coordinates: Tuple[float, float] = None,
            activity: int = 100,
            dist_predefined: bool = IS_FIXED_DISTANCE,
            include_angles: bool = True
    ):
        self.coordinates = coordinates
        self.dist_predefined = dist_predefined
        self.include_angles = include_angles  # allows to take into account angular efficiency
        self.activity = activity

    async def __get_dist_arrays(self):
        jobs = []
        for probe in src_y_probe.values():
            jobs.append(asyncio.create_task(calculate_fluence_rate(
                self.coordinates[0],
                self.coordinates[1],
                src_y=probe,
                activity=self.activity
            )))
        return await asyncio.gather(*jobs)

    async def construct_data(self):
        data_dict = {'x': self.coordinates[0], 'y': self.coordinates[1]}
        if not self.include_angles:
            if self.dist_predefined:
                data_dict["sim_data"] = await calculate_fluence_rate(
                    self.coordinates[0],
                    self.coordinates[1],
                    self.activity
                )
            else:
                dist_dataset = await self.__get_dist_arrays()
                for i, item in enumerate(dist_dataset):
                    data_dict[f"sim_data_{src_y_probe[i]}"] = item
            return await create_dataframe(data_dict)
        else:
            pass
