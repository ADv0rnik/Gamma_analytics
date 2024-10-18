import numpy as np

from src.settings.config import BKG_SIGMA, BKG_COUNT_RATE


async def gen_background(arr_length: int) -> np.ndarray:
    bkg = np.zeros(arr_length)
    for i in range(arr_length):
        bkg[i] = np.random.normal(BKG_COUNT_RATE, BKG_SIGMA)
    return bkg