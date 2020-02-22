# -*- coding: utf-8 -*-
"""
test_hit_checker module
============

This module contains the pytest functions for the drifter module
and associated Hit_Checker class for the pygame Whack a Mole game

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

from .. import drifter

test_drifter = drifter.Drifting_Val(50, drift_type='static', noise=False,
                                    noise_mean=10, noise_sd=5,
                                    noise_truncated=True, gradient=1,
                                    amplitude=1, always_pos=True,
                                    noise_low_bnd=0, noise_high_bnd=10,
                                    drift_clip=False, clip_high_bnd=10,
                                    clip_low_bnd=0)

config_dict = {'drift_type': 'static',
               'noise': False,
               'noise_mean': 10,
               'noise_sd': 5,
               'noise_truncated': True,
               'gradient': 1,
               'amplitude': 1,
               'always_pos': True,
               'noise_low_bnd': 0,
               'noise_high_bnd': 10,
               'drift_clip': False,
               'clip_high_bnd': 10,
               'clip_low_bnd': 0}

def test_Drifting_Val_init():
    assert test_drifter.init_val == 50
    assert test_drifter.noise is False
    assert test_drifter.noise_mean == 10
    assert test_drifter.noise_sd == 5
    assert test_drifter.amplitude == 1
    assert test_drifter.always_pos is True
    assert test_drifter.noise_low_bnd == 0
    assert test_drifter.noise_high_bnd == 10
    assert test_drifter.drift_clip is False
    assert test_drifter.clip_high_bnd == 10
    assert test_drifter.clip_low_bnd == 0


def test_Drifting_Val_init_dict():
    test_drifter = drifter.Drifting_Val(50, config_dict=config_dict)
    assert test_drifter.init_val == 50
    assert test_drifter.noise is False
    assert test_drifter.noise_mean == 10
    assert test_drifter.noise_sd == 5
    assert test_drifter.amplitude == 1
    assert test_drifter.always_pos is True
    assert test_drifter.noise_low_bnd == 0
    assert test_drifter.noise_high_bnd == 10
    assert test_drifter.drift_clip is False
    assert test_drifter.clip_high_bnd == 10
    assert test_drifter.clip_low_bnd == 0


def test_Drifting_Val_drif_iter_static():
    assert test_drifter.drift_iter == 50


def test_Drifting_Val_drif_linear():
    test_drifter.drift_type = 'linear'
    assert test_drifter.drift_iter == 50
    assert test_drifter.drift_iter == 51
    assert test_drifter.drift_iter == 52


def test_Drifting_Val_drif_linear_noise():
    test_drifter.noise = True
    np.random.seed(1)
    assert round(test_drifter.drift_iter, 4) == 59.1689
    assert round(test_drifter.drift_iter, 4) == 62.2946


def test_Drifting_Val_drif_linear_noise_clip():
    test_drifter.drift_clip = True
    assert round(test_drifter.drift_iter, 4) == 10
    test_drifter.init_val = -1000
    assert round(test_drifter.drift_iter, 4) == 0
