import os
from typing import Tuple

import numpy as np
import pandas as pd
import zipfile

from src.config import SRC_Y, SRC_X, OUTPUT_DIR


async def simulate_coordinates(distance: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    The function defines the distance range (part of the road near the source)
    Acquisition time is 1s.
    :param distance: integer value representing the distance between the starting point and the destination.
    :return: tuple of arrays
    """
    x_coordinates = np.arange(-distance, distance + 1, 1)
    y_coordinates = np.zeros(len(x_coordinates))
    return x_coordinates, y_coordinates


async def calculate_angles(
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
    pred_angles[pred_angles > np.pi] = pred_angles[pred_angles > np.pi] - 2 * np.pi
    pred_angles[pred_angles < -np.pi] = pred_angles[pred_angles > np.pi] + 2 * np.pi

    return pred_angles * (180 / np.pi)


async def create_dataframe(data: dict) -> pd.DataFrame:
    return pd.DataFrame(data)


def zip_files(files: list[str]):
    basename, _ = os.path.splitext(files[0])
    zip_filename = f"{basename}.zip"
    print(f"Creating {zip_filename}")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for f in files:
            zip_f.write(filename=f, arcname=os.path.basename(f))
    return zip_filename


