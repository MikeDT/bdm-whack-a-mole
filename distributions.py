# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 08:46:56 2020

@author: miketaylor
"""
import scipy.stats as stats
import numpy as np


def trunc_norm_sample(mean, sd, low_bnd, high_bnd):
    '''
    Creates a single sample from a init determind truncated normal
    distribution

    Parameters
    ----------
    mean: float
        mean for the normal distribution sample
    sd: float
        standard deviations
    low_bnd: float
        the low bound of the truncated sample
    high_bnd: float
        the high bound of the truncated sample

    Returns
    -------
    x: float
        random sample from a truncated normal distribution
        (with mean etc. defined) at initialisation
    '''
    X = stats.truncnorm((low_bnd - mean) / sd,
                        (high_bnd - mean) / sd,
                        loc=mean, scale=sd)
    x = X.rvs(1)[0]
    return(x)


def norm_sample(mean, sd):
    ''' scipy.
    Creates a single sample from a init determined truncated normal
    distribution

    Parameters
    ----------
    mean: float
        mean for the normal distribution sample
    sd: float
        standard deviations

    Returns
    -------
    x: float
        random sample from a normal distribution (with mean etc. defined)
        at initialisation,
    '''
    x = np.random.normal(mean, sd)
    return x
