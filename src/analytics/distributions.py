import numpy as np
import pandas as pd

from scipy.stats import gamma, norm, poisson
from src.settings.config import SCALE, BKG_COUNT_RATE
from src.utils import mean_count_rate


async def calculate_prior_log(act, mu_bkg) -> float:
    if min(act, mu_bkg) < 0:
        return -np.inf

    log_prior = 0

    log_prior += gamma.logpdf(act / SCALE, a=1.2, scale=1/0.0001)
    log_prior += norm.logpdf(mu_bkg, loc=10, scale=10)

    return log_prior

async def calculate_likelihood_log(lambda_params: np.ndarray, data: pd.DataFrame) -> float:
    x, y, act, mu_bkg = lambda_params

    if min(act, mu_bkg) < 0:
        return -np.inf

    if np.sqrt(x ** 2 + y ** 2) > 2000:
        return -np.inf

    count_rate = mean_count_rate(data.iloc[:, 0], data.iloc[:, 1], x, y, act, mu_bkg)

    distro = poisson.pmf(data.iloc[:, 2], mu=count_rate)
    distro = np.nan_to_num(distro)
    likelihood_log = np.sum(np.log(np.maximum(distro, 1e-323)))

    return likelihood_log


async def calculate_posterior_log(data: pd.DataFrame, lambda_params: np.ndarray) -> float:
    activity = lambda_params[2]
    prior = await calculate_prior_log(act=activity, mu_bkg=BKG_COUNT_RATE)
    likelihood = await calculate_likelihood_log(lambda_params, data=data)
    return  prior + likelihood
