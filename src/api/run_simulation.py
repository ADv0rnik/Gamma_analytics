import numpy as np
import pandas as pd

from time import time
from typing import Tuple
from scipy.stats import multivariate_normal


SIGMA_MH = 0.01
BETA_SIGMA = 1e-4


async def run_mcmc(
        dataframe: pd.DataFrame,
        init_params: Tuple[int],
        simnum: int,
        specified_params: bool = False,
):
    sigma = np.diag(np.ones(4) * 1000**2)
    estimated_mean = np.zeros(4)
    estimated_sigma = np.zeros((4, 4))
    lambda_vec = np.zeros((simnum, 4))
    lambda_star_vec = np.zeros((simnum, 4))
    accept = 0
    count = 0
    time_segment_start = time()

    if not specified_params:
        df_index = np.argmax(dataframe.iloc[:, 2])
        lambda_ = np.array([dataframe.iloc[df_index, 0], dataframe.iloc[df_index, 1], 20, np.mean(dataframe.iloc[:, 2])])
    elif specified_params:
        lambda_ = np.array(*init_params)

    print(f"Data reconstruction in progress...")
