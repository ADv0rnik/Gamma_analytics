from pathlib import Path
from nuclib.nuclides import Energy, BranchingRatio

# common params
BASE_DIR = Path(__file__).resolve().parent.parent
NORMALIZE = True

# Source params for ceasium-137
BRANCH_RATIO = BranchingRatio.CS_137.value
SOURCE_ENERGY = Energy.CS_137.value  # in KeV
SCALE = 1e6

# Position of the orphan source within Cartesian coordinate system
SRC_X = 0
SRC_Y = -50
DIST_MIN = 50
DIST_MAX = 150
STEP = 50
IS_FIXED_DISTANCE = False
# if the distance is not predefined
src_y_probe = {i: dist for i, dist in enumerate(range(DIST_MIN, DIST_MAX, STEP))}

# Detector params
EFFICIENCY = 0.00216  # from R. Finck calculations


