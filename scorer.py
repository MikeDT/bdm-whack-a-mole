# -*- coding: utf-8 -*-
"""
scorer module
============

This module contains the Scorer class for the pygame Whack a Mole game

Attributes:
    handled within the Scorer class

Todo:
    * integrate drifter calss with the score rand adjust drift
    (as it's agnostic to the drift need)

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole)

@author: miketaylor
"""

import numpy as np
import scipy.stats as stats


class Scorer:
    """
    Manages the scoring mechanism for the WAM game

    Attributes
    ----------
    hole_positions: array
        the relative positions of each of the mole holes
    max_score: int
        the maximum score achievable for a hit

    Methods
    -------
    iter_adj(adj_type)
        Adjusts the score_adj variable each score check is made (to support
        drifting, random adjustments etc.)
    reset_score_adj(default=True, beta_a=1, beta_b=1, call_count=1)
        resets the beta distributions that control the drift
    get_score(mouse_pos, frame_num, score_type='boolean', adj_type='static')
        gets the score for a attempted hit, calling get_distance as required
        ad adjusting the score based upon the score_adj
    """
    def __init__(self, *, min_score=0, max_score=10,
                 skill_adjust=False, skill_type=None,
                 rand_adjust=False, rand_type='uniform',
                 rand_mean=5, rand_sd=1,
                 skill_luck_rat=1.0):
        self.min_score = min_score
        self.max_score = max_score
        self.skill_adjust = skill_adjust
        self.skill_type = skill_type
        self.rand_adjust = rand_adjust
        self.rand_type = rand_type
        self.rand_mean = rand_mean
        self.rand_sd = rand_sd
        self.skill_luck_rat = skill_luck_rat

    def get_score(self, distance):
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

        Raises
        ------
        na

        Returns
        -------
        score: float
            the luck adjusted score (i.e. nearer to luckier = better score)
        '''
        score = self.max_score
        if self.skill_adjust:
            score = self.skill_luck_rat * self._skill_adj(score,
                                                          distance,
                                                          self.skill_type)
        if self.rand_adjust:
            score += (1-self.skill_luck_rat) * self._rand_adj(score,
                                                              self.rand_type)
        score = round(score, 2)
        return score

    def _skill_adjust(self, score, distance):
        '''
        Adjusts the score based on teh skill (i.e. euclidean distance measure)

        Parameters
        ----------
        score_raw: float
            the unadulterated score
        score_type: string
            the score adjustment type
        distance: float
            the euclidean distance from the mole centre

        Raises
        ------
        na

        Returns
        -------
        score: float
            the skill adjusted score (i.e. nearer to optimal = better score)
        '''
        if self.skill_type == 'linear_dist':
            score -= min(self.max_score, 0.05*distance)
        elif self.skill_type == 'non_linear_dist':
            score -= min(self.max_score, 0.05*distance**2)
        else:
            score = self.score
        return score

    def _rand_adj(self, score):
        '''
        Adjusts the score based on a random beta dist (or not at all)

        Parameters
        ----------
        score: float
            the score to be adjusted by luck
        adj_type: string
            the score adjustment type ()

        Raises
        ------
        na

        Returns
        -------
        score: float
            the luck adjusted score (i.e. nearer to luckier = better score)
        '''
        if self.rand_type == 'static':
            pass
        elif self.rand_type == 'uniform':
            score = np.random.randint(self.min_score, self.max_score)
        elif self.rand_type == 'normal':
            X = stats.truncnorm((self.min_score - self.rand_mean) /
                                self.rand_sd,
                                (self.max_score - self.rand_mean) /
                                self.rand_sd,
                                loc=self.rand_mean, scale=self.rand_sd)
            score = X.rvs(1)[0]
        return score


class Drifting_Val:
    """
    Manages the drifting of a variable over time

    Attributes
    ----------
    beta_a_start: array
        the relative positions of each of the mole holes
    max_score: int
        the maximum score achievable for a hit

    Methods
    -------
    method(variable)
        desc
    """
    def __init__(self, variable, *,
                 noise=False, noise_mean=10, noise_sd=10, noise_trunc=True,
                 drift_type='static', gradient=1, amplitude=1,
                 always_pos=True, low_bnd=0, high_bnd=10,
                 drift_clip=False, clip_high_bnd=10, clip_low_bnd=0):

        # Sets the noise parameters
        self.noise = noise
        self.noise_mean = noise_mean
        self.noise_sd = noise_sd
        self.low_bnd = low_bnd
        self.high_bnd = high_bnd

        # Sets the gradient and amplitude (if cyclical) of the drift, and the
        # general conditions, e.g. whether it must be positive, is the noise
        # truncated
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

        # Sets the inital value (where the first last_val is also the initial)
        self.init_val = variable
        self.last_val = variable

    @property
    def drift_iter(self):
        '''
        Creates noise for the random walk

        Parameters
        ----------
        self: na

        Raises
        ------
        na

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
        self: na

        Raises
        ------
        na

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
        self: na

        Raises
        ------
        na

        Returns
        -------
       noise: float
            The noise for the random walk, either a truncated or regular
            gaussian
        '''
        if self.noise:
            if self.noise_trunc:
                noise = self._trunc_norm_sample
            else:
                noise = self._norm_sample
        else:
            noise = 0
        return noise

    @property
    def _trunc_norm_sample(self):
        '''
        Creates noise for the random walk

        Parameters
        ----------
        self: na

        Raises
        ------
        na

        Returns
        -------
        x: float
            random sample from a truncated normal distribution
            (with mean etc. defined) at initialisation
        '''
        X = stats.truncnorm((self.low_bnd - self.noise_mean) / self.noise_sd,
                            (self.high_bnd - self.noise_mean) / self.noise_sd,
                            loc=self.noise_mean, scale=self.noise_sd)
        x = X.rvs(1)[0]
        return(x)

    @property
    def _norm_sample(self):
        '''
        Creates noise for the random walk

        Parameters
        ----------
        self: na

        Raises
        ------
        na

        Returns
        -------
        x: float
            random sample from a normal distribution (with mean etc. defined)
            at initialisation,
        '''
        x = np.random.normal(self.noise_mean, self.noise_sd)
        return x

    def reset_counter(self):
        '''
        Resets the call counter to 0

        Parameters
        ----------
        self: na

        Raises
        ------
        na

        Returns
        -------
        na
        '''
        self.call_count = 0
