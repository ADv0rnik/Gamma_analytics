import csv
import os
import pandas as pd
import numpy as np

from scipy.interpolate import interp1d
from src.config import SOURCE_ENERGY, BASE_DIR, SRC_Y, SRC_X

x_coord = np.arange(-50, 51, 1)
y_coord = np.zeros(len(x_coord))


class DataFormatter:
    def __init__(self, filename):
        self.filename = filename

    def __csv_to_dict(self):
        """
        Transform the data from csv file to dictionary with headers as keys.
        :return: dictionary with headers as keys or ValueError
        """

        with open(self.filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            headers = [header.strip() for header in next(reader)]
            data_dict = {header: [] for header in headers}
            for row in reader:
                for i, value in enumerate(row):
                    try:
                        data_dict[headers[i]].append(float(value))
                    except ValueError as err:
                        return err
        return data_dict

    def get_dataframe(self):
        data = self.__csv_to_dict()
        return pd.DataFrame(data=data)


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
    source_vector_x = src_x - x_position
    source_vector_y = y_position - src_y
    pred_angles = np.arctan2(vector_y, vector_x) - np.arctan2(
        source_vector_y, source_vector_x
    )

    # convert negative radian values to positive
    pred_angles[pred_angles < 0] = pred_angles[pred_angles < 0] + 2 * np.pi

    return pred_angles * (180 / np.pi)


result = calculate_angles(x_coord, y_coord, SRC_X, SRC_Y)
