# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 17:35:16 2020

@author: miketaylor
"""
import numpy as np
from distributions import trunc_norm_sample as _trunc_norm_sample


class Hit_Checker:

    def __init__(self, MOLE_RADIUS, hit_type, luck_mean=0,
                 luck_sd=0.05, luck_low_bnd=-0.1, luck_high_bnd=0.1,
                 diff_fact=10):
        self.MOLE_RADIUS = MOLE_RADIUS
        self.hit_type = hit_type
        self.luck_mean = luck_mean
        self.luck_sd = luck_sd
        self.luck_low_bnd = luck_low_bnd
        self.luck_high_bnd = luck_high_bnd
        self.diff_fact = diff_fact
        self._trunc_luck = _trunc_norm_sample

    def check_mole_hit(self, num, left, distance, margin_drift_iter):
        """
        Checks whether a mole was hit, able to call a variety of methods
        dependent on the type of mole hit that is modelled for in the game at
        a given point in time (e.g. standard, with additional margin, binomial
        etc.
        """
        result = [False, False, False]
        if (num > 0 and left == 0):
            margin_hit_results = self._margin_hit_results(distance,
                                                          margin_drift_iter)
            if margin_hit_results[1]:
                if self.hit_type == 'Standard':
                    result = margin_hit_results + [True]
                elif self.hit_type == 'Binomial':
                    result = margin_hit_results + self._binom_hit_result(distance, margin_drift_iter)
        return result

    def _margin_hit_results(self, distance, margin_drift_iter):
        """
        As per the simple mole hit model, but with an added margin of error
        that can be adjusted intra or inter game
        """
        actual_hit = False
        margin_hit = False
        if distance < self.MOLE_RADIUS:
            actual_hit = True
        if distance < self.MOLE_RADIUS + margin_drift_iter:
            margin_hit = True
        return [actual_hit, margin_hit]

    def _binom_hit_result(self, distance, margin_drift_iter):
        """
        As per the simple mole hit model, but with an added margin of error
        that can be adjusted intra or inter game
        """
        dist_ratio = distance / (self.MOLE_RADIUS + margin_drift_iter)
        hit_prob = 1 / (1 + dist_ratio*self.diff_fact)
        hit_prob += self._trunc_luck(self.luck_mean, self.luck_sd,
                                     self.luck_low_bnd, self.luck_high_bnd)
        if (np.random.binomial(1, hit_prob, 1)[0]) > 0:
            binom_result = True
        else:
            binom_result = False
        return [binom_result]
