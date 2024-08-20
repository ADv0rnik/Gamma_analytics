from src.data_generators.angular_data_generator import AngularDataGenerator
from src.data_generators.regular_data_generator import RegularDataGenerator
from src.data_generators.velocity_data_generator import VelocityDataGenerator


class GeneratorFactory:
    def __init__(self, **kwargs):
        self.params = kwargs

    async def return_data_generator(self) -> AngularDataGenerator | RegularDataGenerator | VelocityDataGenerator:
        if self.params["include_angles"]:
            return AngularDataGenerator(**self.params)
        if self.params["add_speed"]:
            return  VelocityDataGenerator(**self.params)
        else:
            return RegularDataGenerator(**self.params)