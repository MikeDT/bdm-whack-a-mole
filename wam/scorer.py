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
    def __init__(self, MOLE_RADIUS, *, min_score=0, max_score=10,
                 adjust=False, skill_type='linear_dist',
                 rand_type='uniform',
                 rand_mean=5, rand_sd=1,
                 skill_luck_rat=1.0):
        # Assertion for the skill_luck_rat, only input deemed at risk of misuse
        try:
            assert skill_luck_rat <= 1.0
        except AssertionError:
            print('skill_luck_rat out of bounds, now set to 1.0')
        try:
            assert skill_luck_rat <= 1.0
        except AssertionError:
            print('skill_luck_rat out of bounds, now set to 0.0')
            skill_luck_rat = 0.0

        # Sets the Scorer instance parameters
        self.MOLE_RADIUS = MOLE_RADIUS
        self.min_score = min_score
        self.max_score = max_score
        self.adjust = adjust
        self.skill_type = skill_type
        self.rand_type = rand_type
        self.rand_mean = rand_mean
        self.rand_sd = rand_sd
        self.skill_luck_rat = skill_luck_rat

        # Adds the distribution methods
        self._norm_sample = _norm_sample
        self._trunc_norm_sample = _trunc_norm_sample

    def get_score(self, distance, margin_drift_iter):
        '''
        Gets the score for an attempted mole whack

        Parameters
        ----------
        distance: float
            the distance from the centre of the mole
        score_type: string
            how scores get calculated (i.e. the skill component)
        adj_type: string
            how scores get adjusted (i.e. the luck component)

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
        precision = 1.0
        if self.skill_type == 'linear_dist':
            precision = 1 - distance/(self.MOLE_RADIUS +
                                      margin_drift_iter)
        elif self.skill_type == 'non_linear_dist':
            precision = 1 - distance/(self.MOLE_RADIUS +
                                      margin_drift_iter)
            precision = precision**2
        score = precision*score
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


class Drifting_Val:
    """
    Manages the drifting of a variable over time

    Attributes
    ----------
    noise: Bool
        whether to add noise to the drift
    noise_mean: float
        the mean of the gaussian noise
    noise_sd: float
        the standard deviation of the gaussian noise
    noise_trunc=True
        whether the noise should be truncated
    drift_type: string
        the drift type for the model, e.g. linear, static etc.
    gradient: float
        the graident for any linear drift
    amplitude: float
        the amplitude of any sinusoidal type drift
    always_pos: Bool
        whether the outcome must always be positive (i.e. max of 0 and val)
    noise_low_bnd: float
        the low boundary for the added noise
    noise_high_bnd: float
        the high boundary for the added noise
    drift_clip: Bool
        the clipping for the drifting (i.e. ensuring it stays within set
        boundaries)
    clip_high_bnd: float
        the high boundary for the clipping
    clip_low_bnd: float
        the low boundary for the clipping

    Methods
    ----------
    drift_iter
        Property method, drifts the initially supplied variable in the
        fashion determined during initialisation (or changed in flight)
    _function
        Property method, creates the movement for the drifting variable
    _noise
        Property method, creates noise for the random walk
    _trunc_norm_sample:
        Property method, creates a single sample from a init determined
        truncated normal distribution
    _norm_sample(self):
        Creates a single sample from a init determined truncated normal
        distribution
    reset_counter(self):
        '''
        Resets the call counter to 0

    Methods
    -------
    method(variable)
        desc
    """
    def __init__(self, variable, *, config_dict=None,
                 drift_type='static', noise=False, noise_mean=10, noise_sd=10,
                 noise_trunc=True, gradient=1, amplitude=1,
                 always_pos=True, noise_low_bnd=0, noise_high_bnd=10,
                 drift_clip=False, clip_high_bnd=10, clip_low_bnd=0):

        # Sets the inital value
        self.init_val = variable
        self.last_val = variable

        # External distribution functions
        self._norm_sample = _norm_sample
        self._trunc_norm_sample = _trunc_norm_sample

        # Load either by input vals or config_dict (if present)
        if config_dict is None:
            # Sets the noise parameters
            self.noise = noise
            self.noise_mean = noise_mean
            self.noise_sd = noise_sd
            self.noise_low_bnd = noise_low_bnd
            self.noise_high_bnd = noise_high_bnd

            # Sets the gradient and amplitude (if cyclical) of the drift, and
            # the general conditions, e.g. whether it must be positive, is the
            # noise truncated
            self.call_count = 0
            self.drift_type = drift_type
            self.always_pos = always_pos
            self.noise_trunc = noise_trunc
            self.gradient = gradient
            self.amplitude = amplitude

            # Sets the dirfting clipping (i.e. so drifting cannot exceed a
            # defined set of boundaries)
            self.drift_clip = drift_clip
            self.clip_high_bnd = clip_high_bnd
            self.clip_low_bnd = clip_low_bnd

    @property
    def drift_iter(self):
        '''
        Property method, drifts the initially supplied variable in the
        fashion determined during initialisation (or changed in flight)

        Parameters
        ----------
        self: self

        Returns
        -------
        self.last_val: float
            The newly incremented value for the drifting variable
        '''
        if self.drift_type == 'static':
            pass
        else:
            self.last_val = self.init_val + self._function + self._noise
            self.call_count += 1
        if self.always_pos:
            if self.last_val > 0:
                pass
            else:
                self.last_val = 0
        if self.drift_clip:
            if self.last_val > self.clip_high_bnd:
                self.last_val = self.clip_high_bnd
            elif self.last_val < self.clip_low_bnd:
                self.last_val = self.clip_low_bnd
        return self.last_val

    @property
    def _function(self):
        '''
        Creates the movement for the drifting variable

        Parameters
        ----------
        self: self

        Returns
        -------
        x: float
            the degree of change from the initial variable setting
        '''
        if self.drift_type == 'static':
            x = 0
        elif self.drift_type == 'sin':
            x = np.sin(self.call_count) * self.amplitude
        elif self.drift_type == 'linear':
            x = self.gradient * self.call_count
        elif self.drift_type == 'linear+sin':
            x = (np.sin(self.call_count) * self.amplitude +
                 self.gradient * self.call_count)
        elif self.drift_type == 'random':
            x = (np.random.random_sample() - 0.5) * 2 * self.amplitude
        return x

    @property
    def _noise(self):
        '''
        Creates noise for the random walk

        Parameters
        ----------
        self: self

        Returns
        -------
        noise: float
            The noise for the random walk, either a truncated or regular
            gaussian
        '''
        if self.noise:
            if self.noise_trunc:
                noise = self._trunc_norm_sample(self.noise_mean,
                                                self.noise_sd,
                                                self.noise_low_bnd,
                                                self.noise_high_bnd)
            else:
                noise = self._norm_sample(self.noise_mean,
                                          self.noise_sd)
        else:
            noise = 0
        return noise

    def reset_counter(self):
        '''
        Resets the call counter to 0

        Parameters
        ----------
        self: self
        '''
        self.call_count = 0
