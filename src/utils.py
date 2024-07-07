import numpy as np
import pandas as pd

from src.config import SRC_Y, SRC_X


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


async def create_dataframe(data: dict) -> pd.DataFrame:
    return pd.DataFrame(data)
