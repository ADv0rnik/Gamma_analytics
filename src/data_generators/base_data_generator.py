from abc import ABC, abstractmethod


class BaseDataGenerator(ABC):

    @abstractmethod
    async def generate_data(self):
        pass

    @abstractmethod
    async def get_from_poisson(self, *args):
        pass