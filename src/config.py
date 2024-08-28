import os
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
IS_POISSON = True # Set this parameter to True if Poisson distribution is needed

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

NORMALIZED = True

# Source params for ceasium-137
BRANCH_RATIO = BranchingRatio.CS_137.value
SOURCE_ENERGY = Energy.CS_137.value  # in KeV
SCALE = 1e6
BKG_ACTIVITY = 5 # in cps

# Position of the orphan source within Cartesian coordinate system.
# Use IS_FIXED_DISTANCE=True if the distance from the road to the source (SRC_X and SRC_Y) is specified.
IS_FIXED_DISTANCE = False
SRC_X = 0
SRC_Y = 50
STEP = 20 # for recalculating source to detector distance (in meters)

# if the distance is not predefined (IS_FIXED_DISTANCE=False)
SRC_Y_MIN = 20
SRC_Y_MAX = 100
src_y_probe = {i: dist for i, dist in enumerate(range(SRC_Y_MIN, SRC_Y_MAX, STEP))}

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

# TODO: Create logger
# TODO: Create error handlers
