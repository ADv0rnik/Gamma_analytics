import csv
import os
import pandas as pd
import numpy as np

from scipy.interpolate import interp1d
from src.config import SOURCE_ENERGY, BASE_DIR, SRC_Y, SRC_X

x_coord = np.arange(-300, 301, 1)
y_coord = np.zeros(len(x_coord))


class DataFormatter:
    FILENAME = os.path.join(BASE_DIR, "nuclib", "attenuation_table.csv")

    @classmethod
    def csv_to_dataframe(cls):
        with open(cls.FILENAME, newline='') as csvfile:
            energy, mu = [], []
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader:
                energy.append(float(row[0]))
                mu.append(float(row[1]))
            dataframe = pd.DataFrame({"energy": energy, "mu": mu})
        return dataframe

    @classmethod
    def interpolate_data(cls, scaling_factor=1000):
        data = cls.csv_to_dataframe()
        x = data["energy"].to_numpy()
        y = data["mu"].to_numpy()
        f = interp1d(x, y)
        return f(SOURCE_ENERGY / scaling_factor)


formatter = DataFormatter()


def calculate_angles(
        x_position: np.ndarray,
        y_position: np.ndarray,
        src_x=SRC_X,
        src_y=SRC_Y
) -> np.ndarray:
    """
    The function calculates relative angles of incidence expressed in radians.
    The np.atan2 method is used. Radians are then converted to degrees by multiplying by 180/pi.
    Vector_x and Vector_y are velocity vectors of i-th measurement expressed as a difference between
    current (i) and previous (i - 1) coordinates within Cartesian coordinate system.

    :param x_position: numpy array of x coordinates
    :param y_position: numpy array of y coordinates
    :param src_x: x position of the orphan source
    :param src_y: y position of the orphan source
    :return: numpy array of relative angles expressed in degrees
    """

    vector_x = np.append(np.diff(x_position), [0])
    vector_y = np.append(np.diff(y_position), [0])
    source_vector_x = x_position - src_x
    source_vector_y = y_position - src_y

    pred_angles = np.arctan2(vector_y, vector_x) - np.arctan2(
        source_vector_y, source_vector_x
    )
    # if pred_angles
    return pred_angles * (180 / np.pi)


result = calculate_angles(x_coord, y_coord, SRC_X, SRC_Y)
print(result)

#TODO: Check the negative values of angles and convert them to positive values in the range from 0 to 360.
