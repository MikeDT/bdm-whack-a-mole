# -*- coding: utf-8 -*-
"""
test_distribution module
============

This module contains the pytest functions for the distribution
functions from the distributions module for the pygame Whack
a Mole game

Attributes:
    handled within the functions

Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: miketaylor
"""

import numpy as np

from .. import distributions


def test_norm_sample():
    np.random.seed(1)
    assert round(distributions.norm_sample(1, 1), 4) == 2.6243


def test_trunc_norm_sample():
    np.random.seed(1)
    assert round(distributions.trunc_norm_sample(1,
                                                 2,
                                                 3,
                                                 4), 4) == 3.3465
