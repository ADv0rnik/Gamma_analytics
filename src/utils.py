import os
import shutil

import numpy as np
import pandas as pd
import geopandas as gpd
import zipfile
import logging

from typing import Tuple
from geopandas import GeoDataFrame
from src.settings.config import SRC_Y, SRC_X, OUTPUT_DIR, EFFICIENCY, SCALE, BRANCH_RATIO, mu_air, WORK_DIR


logger = logging.getLogger("gamma")


async def generate_coordinates(distance: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    The function defines the distance range (part of the road near the source)
    Acquisition time is 1s.
    :param distance: integer value representing the distance between the starting point and the destination.
    :return: tuple of arrays
    """
    dist = abs(distance)
    x_coordinates = np.arange(-dist, dist + 1, 1)
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
    source_vector_x = x_position - src_x
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


async def create_job_dir(input_filename):
    job_name, _ = os.path.splitext(os.path.basename(input_filename))
    job_dir = os.path.join(WORK_DIR, job_name)
    if os.path.isdir(job_dir):
        shutil.rmtree(job_dir)
    os.mkdir(job_dir)
    return job_dir


def zip_files(files: list[str]) -> str:
    """
    The function create a zip archive of all the files in the given list.
    :param files: List of files to zip
    :return: String representation of the zip archive
    """
    basename, _ = os.path.splitext(files[0])
    zip_filename = f"{basename}.zip"
    logger.info(f"Creating archive: {zip_filename}")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for f in files:
            zip_f.write(filename=f, arcname=os.path.basename(f))
    return zip_filename


async def make_normalization(data_to_normalize: pd.DataFrame):
    only_gen_data = data_to_normalize.iloc[:, 2::1]
    norm_data = only_gen_data.apply(lambda x: x / x.max(), axis=0)
    for i, column in enumerate(norm_data.columns):
        norm_data.rename(columns={column: column + "_n"}, inplace=True)
    return pd.concat([data_to_normalize, norm_data], axis=1)


async def make_points_grid(geodata_array: np.ndarray) -> GeoDataFrame:
    points_gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(geodata_array[:, 0], geodata_array[:, 1]))
    points_gdf.to_file(os.path.join(OUTPUT_DIR, 'source_points.geojson'), driver='GeoJSON')
    return points_gdf


def mean_count_rate(
        x_position,
        y_position,
        src_x,
        src_y,
        activity,
        bkg,
        det_eff=EFFICIENCY,
):
    dist = np.sqrt((x_position - src_x) ** 2 + (y_position - src_y) ** 2)
    count_rate = (activity * SCALE * BRANCH_RATIO * det_eff * np.exp(-mu_air * dist)) / (4 * np.pi * dist ** 2)
    return np.round(count_rate, 2) + bkg
