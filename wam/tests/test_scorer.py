# -*- coding: utf-8 -*-
"""
test_scorer module
============

This module contains the pytest functions for the Scorer and Drifting_Val class from
the scorer module for the pygame Whack a Mole game

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

from .. import scorer

test_scorer = scorer.Scorer(10, min_score=0, max_score=10,
                            adjust=False, skill_type='linear_dist',
                            rand_type='uniform',
                            rand_mean=5, rand_sd=1,
                            skill_luck_rat=1.0)


def test_Scorer_init():
    assert test_scorer.min_score == 0
    assert test_scorer.max_score == 10
    assert test_scorer.adjust is False
    assert test_scorer.skill_type == 'linear_dist'
    assert test_scorer.rand_type == 'uniform'
    assert test_scorer.rand_mean == 5
    assert test_scorer.rand_sd == 1
    assert test_scorer.skill_luck_rat == 1.0


def test_get_score_no_adj():
    assert test_scorer.get_score(10, 10) == 10.0


def test_get_score_adj_lin_dist():
    test_scorer.adjust = True
    test_scorer.skill_type = 'linear_dist'
    assert test_scorer.get_score(10, 10) == 5.0  # linear decay


def test_get_score_adj_non_lin_dist():
    test_scorer.adjust = True
    test_scorer.skill_type = 'non_linear_dist'
    assert test_scorer.get_score(10, 10) == 2.5  # quadratic decay


def test_get_score_adj_luck_unif():
    test_scorer.adjust = True
    test_scorer.skill_luck_rat = 0.0
    np.random.seed(1)
    assert test_scorer.get_score(10, 10) == 5.0


def test_get_score_adj_luck_norm():
    test_scorer.adjust = True
    test_scorer.rand_type='normal'
    np.random.seed(1)
    assert test_scorer.get_score(10, 10) == 4.79