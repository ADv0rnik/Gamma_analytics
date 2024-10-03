import numpy as np
import pandas as pd

from time import time
from typing import Tuple
from scipy.stats import multivariate_normal, uniform

from src.analytics.distributions import calculate_posterior_log


SIGMA_MH = 0.01
BETA_SIGMA = 1e-4


async def run_mcmc(
        dataframe: pd.DataFrame,
        simnum: int,
        burnin: int,
        init_params: Tuple[float, float, float, float] | None = None,
):
    mcmc_data = await get_data_from_mcmc(dataframe=dataframe, simnum=simnum, init_params=init_params)


async def get_data_from_mcmc(
        dataframe: pd.DataFrame,
        simnum: int,
        init_params: Tuple[float, float, float, float] | None = None,
):
    sigma = np.diag(np.ones(4) * 1000 ** 2)
    estimated_mean = np.zeros(4)
    estimated_sigma = np.zeros((4, 4))
    lambda_vec = np.zeros((simnum, 4))
    lambda_start_vector = np.zeros((simnum, 4))
    accept = 0
    count = 0
    time_segment_start = time()

    if init_params:
        lambda_ = np.array([*init_params])

    df_index = np.argmax(dataframe.iloc[:, 2])
    lambda_ = np.array([dataframe.iloc[df_index, 0], dataframe.iloc[df_index, 1], 100, np.mean(dataframe.iloc[:, 2])])

    print(f"Data reconstruction in progress...")

    for i in range(1, simnum + 1):
        count += 1
        lambda_start = lambda_.copy()
        covariance = SIGMA_MH ** 2 * sigma
        lambda_start[:4] = np.random.multivariate_normal(mean=lambda_[:4], cov=covariance, size=1)

        if i % 1000 == 0:
            dist_to_prop = np.sqrt((dataframe.iloc[:, 0] - lambda_start[0]) ** 2 + (dataframe.iloc[:, 1] - lambda_start[1]) ** 2)
            closest_to_prop = np.argmin(dist_to_prop)
            distance_to_x = lambda_start[0] - dataframe.iloc[closest_to_prop, 0]
            distance_to_y = lambda_start[1] - dataframe.iloc[closest_to_prop, 1]
            lambda_start[0] = lambda_start[0] - 2 * distance_to_x
            lambda_start[1] = lambda_start[1] - 2 * distance_to_y

        lambda_start_vector[i - 1, :] = lambda_start

        random_uniforms = uniform.rvs()
