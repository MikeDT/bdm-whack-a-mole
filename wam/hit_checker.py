# -*- coding: utf-8 -*-
"""
hit_checker module
============

This module contains the Hit_Checker class for the WAM game

Attributes:
    handled within the Hit_Checker class

Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: DZLR3
"""

import numpy as np
from wam.distributions import trunc_norm_sample as _trunc_norm_sample


class Hit_Checker:
    """
    Checks whether a mole hit happened truly, happened with a margin of error
    and whether it will be communicated to the end user, post some
    probabilistic manipulation

    Attributes
    ----------
    MOLE_RADIUS: int
        The true radius of the mole
    hit_type: string
        the type of hit, either 'Standard' or 'Binomial'
    luck_mean: float
        the mean about which the truncated noise added to the binomial outcome
        is added
    luck_sd: float
        the standard deviation of the luck factor
    luck_low_bnd: float
        the lower bound of the truncated luck noise
    luck_high_bnd: float
        the higher bound of the truncated luck noise

    Methods
    -------
    check_mole_hit
        checks whether the mole was hit, returning a 3 boolean tuple, with
        the True Hit, the Margin Hit, and the Binomial Hit results
    _get_true_hit_res
        checks whether a hit happened in actuality
    _get_marg_hit_res
        checks whether a hit happen when considering an error margin
    _get_marg_hit_res
        checks whether a hit happen when binomial an error margin
    """

    def __init__(self, MOLE_RADIUS, hit_type='Standard', luck_mean=0,
                 luck_sd=0.05, luck_low_bnd=-0.1, luck_high_bnd=0.1,
                 diff_fact=1, config_dict=None):
        self.MOLE_RADIUS = MOLE_RADIUS
        if type(config_dict) == dict:
            self.hit_type = config_dict['hit_type']
            self.luck_mean = config_dict['luck_mean']
            self.luck_sd = config_dict['luck_sd']
            self.luck_low_bnd = config_dict['luck_low_bnd']
            self.luck_high_bnd = config_dict['luck_high_bnd']
            self.diff_fact = config_dict['diff_fact']
        else:
            self.hit_type = hit_type
            self.luck_mean = luck_mean
            self.luck_sd = luck_sd
            self.luck_low_bnd = luck_low_bnd
            self.luck_high_bnd = luck_high_bnd
            self.diff_fact = diff_fact
        self._trunc_luck = _trunc_norm_sample

    def check_mole_hit(self, num, left, distance, margin_drift_iter):
        '''
        Checks whether a mole was hit

        Parameters
        ----------
        num: int
            the number for the mole animation frame
        left:
            the remaining steps
        distance: float
            the distance from the centre of the mole
        margin_drift_iter: float
            the additional (generous or penalising) margin around the mole
            that still results in a possible hit

        Raises
        ------
        AssertionError
            raised should the distance not be a float or an int (i.e.
            something incorrect was passed by an external process)

        Returns
        -------
        score: [Bool]
            Boolean in a len 1 list, for simpler addition to the results tuple,
            describing the final hit result communicated to the end user
        '''
        try:
            assert type(distance) in [float, int]
            assert type(margin_drift_iter) in [float, int]
            true_hit, margin_hit, binom_hit = False, False, False
            if (num > 0 and left == 0):
                true_hit = self._get_true_hit_res(distance)
                margin_hit = self._get_marg_hit_res(distance,
                                                    margin_drift_iter)
                if margin_hit:
                    if self.hit_type == 'Standard':
                        binom_hit = True
                    elif self.hit_type == 'Binomial':
                        binom_hit = self._get_bin_hit_res(distance,
                                                          margin_drift_iter)
                else:
                    binom_hit = False
        except AssertionError:
            print('Either distance or margin_drift_iter not a float or int')
        return [true_hit, margin_hit, binom_hit]

    def _get_true_hit_res(self, distance):
        '''
        Assesses whether a mole hit happened based only on the mole radius and
        the distance

        Parameters
        ----------
        distance: float
            the distance from the centre of the mole

        Returns
        -------
        true_hit: Bool
            boolean describing whether a hit happened based only on the mole
            radius and distance
        '''
        true_hit = False
        if distance <= self.MOLE_RADIUS:
            true_hit = True
        else:
            true_hit = False
        return true_hit

    def _get_marg_hit_res(self, distance, margin_drift_iter):
        '''
        Assesses whether a mole hit happened when considering the margin

        Parameters
        ----------
        distance: float
            the distance from the centre of the mole
        margin_drift_iter: float
            the additional (generous or penalising) margin around the mole
            that still results in a possible hit

        Returns
        -------
        margin_hit: Bool
            boolean describing whether a hit happened based on the mole radius,
            the doctored extra margin and distance
        '''
        if distance < self.MOLE_RADIUS + margin_drift_iter:
            margin_hit = True
        else:
            margin_hit = False
        return margin_hit

    def _get_bin_hit_res(self, distance, margin_drift_iter):
        '''
        Assesses whether a mole hit happened when considering the binomial
        decay function, plus truncated gaussian noise

        Parameters
        ----------
        distance: float
            the distance from the centre of the mole
        margin_drift_iter: float
            the additional (generous or penalising) margin around the mole
            that still results in a possible hit

        Raises
        ------
        AssertionError
            raised if the distance ratio is not between 0 and 1

        Returns
        -------
        margin_hit: Bool
            boolean describing whether a hit happened based on the mole radius,
            the doctored extra margin and distance
        '''
        dist_ratio = distance / (self.MOLE_RADIUS + margin_drift_iter)
        try:
            assert 0 < dist_ratio <= 1
            hit_prob = 1 / (1 + dist_ratio*self.diff_fact)
            hit_prob += self._trunc_luck(self.luck_mean, self.luck_sd,
                                         self.luck_low_bnd, self.luck_high_bnd)
            hit_prob = max(hit_prob, 0)
            hit_prob = min(hit_prob, 1)
            if (np.random.binomial(1, hit_prob, 1)[0]) > 0:
                binom_hit = True
            else:
                binom_hit = False
        except AssertionError:
            print('Distance ratio not between 0 and 1.0')
        return binom_hit
