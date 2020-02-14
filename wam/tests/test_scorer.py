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


def test_Scorer():
    test_scorer = scorer.Scorer(min_score=0, max_score=10,
                                skill_adjust=False, skill_type=None,
                                rand_adjust=False, rand_type='uniform',
                                rand_mean=5, rand_sd=1,
                                skill_luck_rat=1.0)
    assert test_scorer.min_score == 0
    assert test_scorer.max_score == 10
    assert test_scorer.skill_adjust is False
    assert test_scorer.skill_type is None
    assert test_scorer.rand_adjust is False
    assert test_scorer.rand_type == 'uniform'
    assert test_scorer.rand_mean == 5
    assert test_scorer.rand_sd == 1
    assert test_scorer.skill_luck_rat == 1.0
    
def test_get_score():
    test_scorer = scorer.Scorer(min_score=0, max_score=10,
                            skill_adjust=False, skill_type=None,
                            rand_adjust=False, rand_type='uniform',
                            rand_mean=5, rand_sd=1,
                            skill_luck_rat=1.0)
    assert test_scorer.get_score(10) == 10 # no adjustment
    test_scorer.skill_adjust = True
    assert test_scorer.get_score(10) == 10.0 # s
    test_scorer.skill_adjust = 'linear_dist'
    assert test_scorer.get_score(10) == 9.5 # s
    test_scorer.skill_adjust = 'non_linear_dist'
    assert test_scorer.get_score(10) == 5.0 # s    

