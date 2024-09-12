import numpy as np
import pandas as pd

from scipy.stats import gamma, norm
from src.config import SCALE


async def calculate_prior_log(act, mu_bkg=10):
    if min(act, mu_bkg) < 0:
        return -np.inf

    log_prior = 0

    log_prior += gamma.logpdf(act / SCALE, a=1.2, scale=1/0.0001)
    log_prior += norm.logpdf(mu_bkg, loc=10, scale=10)

    return log_prior

async def calculate_likelihood_log(data: pd.DataFrame, act, mu_bkg=10):
    if min(act, mu_bkg) < 0:
        return -np.inf


