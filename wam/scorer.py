# -*- coding: utf-8 -*-
"""
scorer module
============

This module contains the Scorer and Drifting_Val class for the pygame
Whack a Mole game

Attributes:
    handled within the Scorer class

Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: DZLR3
"""

import numpy as np
import random
from wam.distributions import trunc_norm_sample as _trunc_norm_sample
from wam.distributions import norm_sample as _norm_sample


class Scorer:
    """
    Manages the scoring mechanism for the WAM game

    Attributes
    ----------
    min_score: float
        The minimum score that can be achieved
    max_score: float
        The maximum score that can be achieved
    skill_adjust: Bool
        Whether a score adjustment for skill (based on the distance from the
        centre) should be enacted
    skill_type: String/None
        The type of skill adjustment, i.e. None, linear or non linear
    rand_adjust: Bool
        Whether to perform a random_adjustment of the score
    rand_type: string
        The random adjustment type
    rand_mean: float
        The mean for the random adjustment (presuming it's gaussian)
    rand_sd: float
        The mean for the random adjustment (presuming it's gaussian)
    skill_luck_rat: float
        the skill to luck ratio

    Raises
    ------
    Assertion Error
        if the skill_luck_rat during init is not between 0 and 1

    Methods
    -------
    get_score(distance)
        gets the score for a given mole hit, moderated by the distance from the
        centre of the mole
    _skill_adjust(score, distance)
        adjusts the score based on the users skill
    _rand_adjust(score)
        gives a random adjustment to the score
    """
    def __init__(self, MOLE_RADIUS, *, min_score=1.0, max_score=10.0,
                 adjust=False, skill_type='linear_dist',
                 rand_type='uniform',
                 rand_mean=5, rand_sd=1,
                 #skill_luck_rat=0.5,
                 config_dict=None):
        self.MOLE_RADIUS = MOLE_RADIUS
        if type(config_dict) is dict:
            # Sets the Scorer instance parameters
            self.min_score = config_dict['min_score']
            self.max_score = config_dict['max_score']
            self.adjust = config_dict['adjust']
            self.skill_type = config_dict['skill_type']
            self.rand_type = config_dict['rand_type']
            self.rand_mean = config_dict['rand_mean']
            self.rand_sd = config_dict['rand_sd']
            self.skill_luck_rat = config_dict['skill_luck_rat']            
        else:
            # Sets the Scorer instance parameters
            self.min_score = min_score
            self.max_score = max_score
            self.adjust = adjust
            self.skill_type = skill_type
            self.rand_type = rand_type
            self.rand_mean = rand_mean
            self.rand_sd = rand_sd
            #self.skill_luck_rat = skill_luck_rat            

        # Assertion for the skill_luck_rat, only input deemed at risk of misuse
        try:
            assert self.skill_luck_rat <= 1.0
        except AssertionError:
            print('skill_luck_rat out of bounds, now set to 1.0')
        try:
            assert self.skill_luck_rat <= 1.0
        except AssertionError:
            print('skill_luck_rat out of bounds, now set to 0.0')
            self.skill_luck_rat = 0.0

        # Adds the distribution methods
        self._norm_sample = _norm_sample
        self._trunc_norm_sample = _trunc_norm_sample
        
    def get_score(self, distance, margin_drift_iter, skill_luck_rat):
        '''
        Gets the score for an attempted mole whack

        Parameters
        ----------
        distance: float
            the distance from the centre of the mole
        score_type: string
            how scores get calculated (i.e. the skill component)

        Returns
        -------
        score: float
            the luck adjusted score (i.e. nearer to luckier = better score)
        '''
        is_skill = np.random.binomial(1,skill_luck_rat, 1)[0]
        max_score = self.max_score
        if is_skill == 1:
            score = self._skill_adj(max_score, distance, margin_drift_iter)
            skill_status = 'skill'
        else:
            score = random.choice(list(range(1,max_score+1)))
            skill_status = 'luck'

        return score, skill_status

    def get_score_deprecated(self, distance, margin_drift_iter): # to be deprecated
        '''
        Gets the score for an attempted mole whack

        Parameters
        ----------
        distance: float
            the distance from the centre of the mole
        score_type: string
            how scores get calculated (i.e. the skill component)

        Returns
        -------
        score: float
            the luck adjusted score (i.e. nearer to luckier = better score)
        '''
        score = self.max_score
        if self.adjust:
            score = self.skill_luck_rat * self._skill_adj(score,
                                                          distance,
                                                          margin_drift_iter)
            score += (1-self.skill_luck_rat) * self._rand_adj(score)
        score = round(score, 2)
        return score

    def _skill_adj(self, score, distance, margin_drift_iter):
        '''
        Adjusts the score based on the skill (i.e. euclidean distance measure)

        NB this function may be deprecated in the future based on the binomial
        hit checking

        Parameters
        ----------
        score_raw: float
            the unadulterated score
        score_type: string
            the score adjustment type
        distance: float
            the euclidean distance from the mole centre
        margin_drift_iter: float
            the additional (typically drifted) margin that is added to the mole

        Returns
        -------
        score: float
            the skill adjusted score (i.e. nearer to optimal = better score)
        '''
        #precision = 1.0
        #if self.skill_type == 'linear_dist':
        precision = 1 - distance/(self.MOLE_RADIUS +
                                      margin_drift_iter)
        # elif self.skill_type == 'non_linear_dist':
        #     precision = 1 - distance/(self.MOLE_RADIUS +
        #                               margin_drift_iter)
        #    precision = precision**2
        score = precision*score
        score += 0.5
        score = round(score)
        print('skill_adj score, distance, precision', score, distance, precision)

        return score

    def _rand_adj(self, score):
        '''
        Adjusts the score based on a random beta dist (or not at all)

        NB this function may be deprecated in the future based on the binomial
        hit checking

        Parameters
        ----------
        score: float
            the score to be adjusted by luck
        adj_type: string
            the score adjustment type ()

        Raises
        ------
        AssertionError
            raised if an unknown rand_type is passed

        Returns
        -------
        score: float
            the luck adjusted score (i.e. nearer to luckier = better score)
        '''
        try:
            assert self.rand_type in ['uniform', 'normal']
        except AssertionError:
            print('rand type not recognised in _rand_adj')
        if self.rand_type == 'uniform':
            score = np.random.randint(self.min_score, self.max_score)
        elif self.rand_type == 'normal':
            x = self._trunc_norm_sample(self.rand_mean, self.rand_sd,
                                        self.min_score, self.max_score)
            score = x
        return score
