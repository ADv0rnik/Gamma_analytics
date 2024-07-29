import os
import numpy as np
from pathlib import Path
from pydantic_settings import BaseSettings

from nuclib.nuclides import Energy, BranchingRatio
from src.tools.data_formatter import formatter
from src.tools.interpolators import AttenuationInterpolator


# common params
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
ENV_PATH = os.path.join(BASE_DIR, '.env')

ATTENUATION_FILE = os.path.join(BASE_DIR, "nuclib", "attenuation_table.csv")
EFF_FILE = os.path.join(BASE_DIR, "nuclib", "relative_efficiency_HPGe.csv")

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

NORMALIZED = False
CALCULATE_ANGLES = True  # taking angular distribution into account

# Source params for ceasium-137
BRANCH_RATIO = BranchingRatio.CS_137.value
SOURCE_ENERGY = Energy.CS_137.value  # in KeV
SCALE = 1e6
BKG_ACTIVITY = 10

# Position of the orphan source within Cartesian coordinate system.
# Use IS_FIXED_DISTANCE=True if the distance from the road to the source (SRC_X and SRC_Y) is specified.
IS_FIXED_DISTANCE = True
SRC_X = 0
SRC_Y = 50
DIST_MIN = -300
DIST_MAX = 300
STEP = 50

# if the distance is not predefined (IS_FIXED_DISTANCE=False)
SRC_Y_MIN = 50
SRC_Y_MAX = 150
src_y_probe = {i: dist for i, dist in enumerate(range(SRC_Y_MIN, SRC_Y_MAX, STEP))}

# defines the distance range (part of the road near the source)
x_coord = np.arange(DIST_MIN, DIST_MAX + 1, 1)  # 1s of measurements
y_coord = np.zeros(len(x_coord))

# Detector params
EFFICIENCY = 0.00216  # from R. Finck calculations

attenuation_df = formatter.get_dataframe(ATTENUATION_FILE)
attenuation_interpolator = AttenuationInterpolator(attenuation_df)

mu_air = attenuation_interpolator.interpolate(SOURCE_ENERGY)  # mu_air = 0.0015


class ApiSettings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    PROJECT_VERSION: str
    PROJECT_HOST: str
    PROJECT_PORT: int

    class Config:
        env_file = ENV_PATH
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = ApiSettings()
