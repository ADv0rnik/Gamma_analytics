import traceback
import warnings

import numpy as np
import pandas as pd
import logging

from time import time
from typing import Tuple
from scipy.stats import uniform

from src.analytics.distributions import calculate_posterior_log
from src.presentation.plot_maker import PlotMaker
from src.utils import make_points_grid


logger = logging.getLogger("gamma")


async def run_mcmc(
        dataframe: pd.DataFrame,
        simnum: int,
        burn_in: int,
        init_params: Tuple[float, float, float, float] | None = None,
):
    try:
        mcmc_data = await get_data_from_mcmc(dataframe=dataframe, simnum=simnum, init_params=init_params)
        mcmc_data_burn = mcmc_data[burn_in:, :]
        points_ = await make_points_grid(mcmc_data_burn)
        plot_maker = PlotMaker(data=dataframe)
        mcmc_plot = plot_maker.plot_mcmc_sequence(burnin_data=mcmc_data_burn)
        mcmc_posterior_act_plot = plot_maker.plot_activity_density(burnin_data=mcmc_data_burn)
        mcmc_points_density = plot_maker.plot_points(points=points_)
    except Exception as err:
        logger.error(f"An {Exception.__name__} occurred while running simulation: {traceback.format_exc(limit=1)}")
    else:
        logger.info("Reconstruction complete")
        return {
            "mcmc_plot": mcmc_plot,
            "act_density": mcmc_posterior_act_plot,
            "plot_density": mcmc_points_density,
        }


async def get_data_from_mcmc(
        dataframe: pd.DataFrame,
        simnum: int,
        init_params: Tuple[float, float, float, float] | None = None,
):
    warnings.filterwarnings('ignore')

    sigma_mh = 0.01
    beta_sigma = 1e-4
    sigma = np.diag(np.ones(4) * 1000 ** 2)
    estimated_mean = np.zeros(4)
    estimated_sigma = np.zeros((4, 4))
    lambda_vector = np.zeros((simnum, 4))
    lambda_start_vector = np.zeros((simnum, 4))
    accept = 0
    count = 0
    time_segment_start = time()

    if init_params:
        lambda_ = np.array([*init_params])
    else:
        df_max_index = np.argmax(dataframe.iloc[:, 2])
        lambda_ = np.array([dataframe.iloc[df_max_index, 0], dataframe.iloc[df_max_index, 1], 100, np.mean(dataframe.iloc[:, 2])])

    logger.info(f"Data reconstruction in progress. Lambda input params: {lambda_}")

    for i in range(1, simnum + 1):
        count += 1
        lambda_start = lambda_.copy()
        covariance = sigma_mh ** 2 * sigma
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
        p1 = await calculate_posterior_log(data=dataframe, lambda_params=lambda_start)
        p2 = await calculate_posterior_log(data=dataframe, lambda_params=lambda_)
        posterior = np.exp(p1 - p2)
        accept_prob = np.min([1, posterior])

        if random_uniforms < accept_prob:
            lambda_ = lambda_start.copy()
            accept += 1

        lambda_vector[i - 1, :] = lambda_.copy()

        w = 1 / i
        estimated_mean = (1 - w) * estimated_mean + w * lambda_[:4]
        estimated_sigma = (1 - w) * estimated_sigma + w * np.outer(lambda_[:4] - estimated_mean, lambda_[:4] - estimated_mean)

        if i > 100:
            sigma = np.diag(np.diag(estimated_sigma)) + np.eye(len(estimated_mean)) * beta_sigma

        if i % 100 == 0:
            if accept / count < 0.24:
                sigma_mh = max(0.95, (1 - 5 / np.sqrt(i))) * sigma_mh
            else:
                sigma_mh = min(1.05, 1 + 5 / np.sqrt(i)) * sigma_mh
            accept = 0
            count = 0

        if i % 1000 == 0:
            time_segment_end = time()
            time_difference = time_segment_end - time_segment_start
            time_left = (simnum - i) / 1000
            print(f"{100 * round(i / simnum, 2):.2f}% done. Segment duration: {time_difference:.2f} seconds. ETA in: {time_left * time_difference:.2f} seconds or {time_left * time_difference / 60:.2f} minutes.")
            time_segment_start = time()

    return lambda_vector