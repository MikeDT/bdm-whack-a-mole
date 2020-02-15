# -*- coding: utf-8 -*-
"""
test_hit_checker module
============

This module contains the pytest functions for the hit_checker module
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

from .. import hit_checker

test_hit_checker = hit_checker.Hit_Checker(10, 'Standard', luck_mean=0,
                                           luck_sd=0.05, luck_low_bnd=-0.1,
                                           luck_high_bnd=0.1, diff_fact=1)


def test_Hit_Checker_init():
    assert test_hit_checker.MOLE_RADIUS == 10
    assert test_hit_checker.hit_type == 'Standard'
    assert test_hit_checker.luck_mean == 0
    assert test_hit_checker.luck_sd == 0.05
    assert test_hit_checker.luck_low_bnd == -0.1
    assert test_hit_checker.luck_high_bnd == 0.1
    assert test_hit_checker.diff_fact == 1


def test_check_mole_hit_full_miss():
    assert test_hit_checker.check_mole_hit(2, 0, 25, 10) == [False,
                                                             False,
                                                             False]


def test_check_mole_hit_full_hit():
    assert test_hit_checker.check_mole_hit(2, 0, 10, 10) == [True,
                                                             True,
                                                             True]


def test_check_mole_hit_margin_hit():
    assert test_hit_checker.check_mole_hit(2, 0, 12, 10) == [False,
                                                             True,
                                                             True]


def test_check_mole_hit_binom_miss():
    test_hit_checker.hit_type = 'Binomial'
    np.random.seed(1)
    assert test_hit_checker.check_mole_hit(2, 0, 10, 10) == [True, True, False]
