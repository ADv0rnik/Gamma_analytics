import numpy as np
import pandas as pd

from scipy.stats import gamma, norm, poisson
from src.config import SCALE, BKG_COUNT_RATE
from src.data_generators.regular_data_generator import RegularDataGenerator


async def calculate_prior_log(act, mu_bkg):
    if min(act, mu_bkg) < 0:
        return -np.inf

    log_prior = 0

    log_prior += gamma.logpdf(act / SCALE, a=1.2, scale=1/0.0001)
    log_prior += norm.logpdf(mu_bkg, loc=10, scale=10)

    return log_prior

async def calculate_likelihood_log(lambda_params: tuple, data: pd.DataFrame):
    x, y, act, mu_bkg = lambda_params
    if min(act, mu_bkg) < 0:
        return -np.inf

    data_generator = RegularDataGenerator(
        coordinates = (data["x"], data["y"]),
        dist_predefined = True,
        activity = act,
        background = mu_bkg,
        src_x = x,
        src_y = y
    )

    mean_count_rate = await data_generator.generate_data()
    likelihood_log = np.sum(poisson.logpmf(data["pois_data"], mu=mean_count_rate["generic_count_rate"]))
    return likelihood_log


async def calculate_posterior_log(data: pd.DataFrame, x, y, activity, bkg_cps):
    prior = await calculate_prior_log(act=activity, mu_bkg=bkg_cps)
    likelihood = await calculate_likelihood_log(data=data, x=x, y=y, act=activity, mu_bkg=bkg_cps)
    return  prior + likelihood
