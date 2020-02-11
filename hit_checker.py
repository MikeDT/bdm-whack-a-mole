# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 17:35:16 2020

@author: miketaylor
"""
import numpy as np


class Hit_Checker:

    def __init__(self, MOLE_RADIUS, hit_type):
        self.MOLE_RADIUS = MOLE_RADIUS
        self.hit_type = hit_type

    def check_mole_hit(self, num, left, distance, margin_drift_iter):
        """
        Checks whether a mole was hit, able to call a variety of methods
        dependent on the type of mole hit that is modelled for in the game at
        a given point in time (e.g. standard, with additional margin, binomial
        etc.
        """
        print('checking')
        result = [False, False, False]
        if (num > 0 and left == 0):
            margin_hit_results = self._margin_hit_results(distance,
                                                          margin_drift_iter)
            if margin_hit_results[1]:
                if self.hit_type == 'Standard':
                    result = margin_hit_results + [True]
                elif self.hit_type == 'Binomial':
                    result = margin_hit_results + self._binom_hit_result
        print ('result', result)
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

    @property
    def _binom_hit_result(self):
        """
        As per the simple mole hit model, but with an added margin of error
        that can be adjusted intra or inter game
        """
        if (np.random.binomial(1, 0.9, 1)[0]) > 0:
            binom_result = True
        else:
            binom_result = False
        return [binom_result]