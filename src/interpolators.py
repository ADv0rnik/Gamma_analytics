from abc import ABC

from scipy.interpolate import interp1d
from src.base_interpolator import BaseInterpolator


class Interpolator(BaseInterpolator, ABC):

    def __init__(self, data):
        self.data = data


class AttenuationInterpolator(Interpolator):

    def interpolate(self, dataframe,  *args, scaling_factor=1000):
        x = dataframe["energy_mev"].to_numpy()
        y = dataframe["mu"].to_numpy()
        f = interp1d(x, y)
        return f(args[0] / scaling_factor)
