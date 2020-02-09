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
    def __init__(self, hole_positions, max_score=10):
        self.max_score = max_score
        self.hole_positions = hole_positions
        self.trend = []  # include an actual trend list
        self.beta_a_start = 10
        self.beta_b_start = 10
        self.beta_a = self.beta_a_start
        self.beta_b = self.beta_b_start
        self.rw_grad = 1
        self.call_count = 0
        self.score_adj = 1

        self.low_score_bound = 0
        self.high_score_bound = 10
        self.mean_score = 5
        self.score_sd = 2

#    def increment_iter_adj(self, adj_type):
#        '''
#        Incerments the iterative adjuster, currently the beta distribution
#
#        Parameters
#        ----------
#        self : self
#
#        Raises
#        ------
#        na
#
#        Returns
#        -------
#        na
#        '''
#        self.call_count += 1
#        if adj_type == 'static':
#            self.score_adj = 1
#        elif adj_type == 'rnd_wlk':
#            self.score_adj = np.random.beta(self.beta_a, self.beta_b)
#        elif adj_type == 'rnd_wlk_pos':
#            self.beta_b += self.call_count*self.rw_grad
#            self.score_adj = np.random.beta(self.beta_a,
#                                            self.beta_b)
#        elif adj_type == 'rnd_wlk_neg':
#            self.beta_a += self.call_count*self.rw_grad
#            self.score_adj = np.random.beta(self.beta_a,
#                                            self.beta_b)
#        elif adj_type == 'design':
#            self.score_adj = np.random.beta(self.trend[self.call_count][0],
#                                            self.trend[self.call_count][1])

#    def reset_score_adj(self, default=True, *,
#                        beta_a=1, beta_b=1, call_count=1):
#        '''
#        Resets the beta distribution to its initial starting point (by default)
#        or a defined a/b val and call count
#
#        Parameters
#        ----------
#        default: Boolean
#            toggles whether the default is used or not
#        beta_a: int
#            the a value for the beta distribution
#        beta_b: int
#            the b value for the beta distribution
#        call_count: int
#            the call count (i.e. how many iterations have been performed)
#
#        Raises
#        ------
#        na
#
#        Returns
#        -------
#        na
#        '''
#        if default:
#            self.beta_a = self.beta_a_start
#            self.beta_b = self.beta_b_start
#            self.call_count = 0
#        else:
#            self.beta_a = beta_a
#            self.beta_b = beta_b
#            self.call_count = call_count

    def score_skill_adjust(self, score_raw, score_type, distance):
        '''
        Adjusts the score based on teh skill (i.e. euclidean distance measure)

        Parameters
        ----------
        score_type: string
            the score adjustment type

        Raises
        ------
        na

        Returns
        -------
        score: float
            the skill adjusted score (i.e. nearer to optimal = better score)
        '''
        if score_type == 'lin_dist_skill':
            score = score_raw - (min(self.max_score, 0.05*distance))
        elif score_type == 'non_lin_dist_skill':
            score = score_raw - (min(self.max_score, 0.05*distance**2))
        else:
            score = self.max_score
        return score

    def score_rand_adjust(self, score, adj_type='static'):
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
#        self.increment_iter_adj(adj_type)
#        score = min(score * self.score_adj, 10)
        return score

    def get_score(self, distance, score_type='boolean', adj_type=None):
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
        score_raw = self.max_score
        score_skill_adj = self.score_skill_adjust(score_raw, adj_type,
                                                  distance)
        score_skill_random_adj = self.score_rand_adjust(score_skill_adj)
        score_skill_random_adj = round(score_skill_random_adj, 2)
        return score_skill_random_adj


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
