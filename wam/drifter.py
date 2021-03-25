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
    noise_truncated=True
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
                 noise_truncated=True, gradient=1, amplitude=1,
                 always_pos=True, noise_low_bnd=0, noise_high_bnd=10,
                 drift_clip=False, clip_high_bnd=10, clip_low_bnd=0):

        # Sets the inital value
        self.init_val = variable
        self.last_val = variable
        self.call_count = 0

        # External distribution functions
        self._norm_sample = _norm_sample
        self._trunc_norm_sample = _trunc_norm_sample

        # Load either by input vals or config_dict (if present)
        if type(config_dict) is dict:
            self.noise = config_dict['noise']
            self.noise_mean = config_dict['noise_mean']
            self.noise_sd = config_dict['noise_sd']
            self.noise_low_bnd = config_dict['noise_low_bnd']
            self.noise_high_bnd = config_dict['noise_high_bnd']

            # Sets the gradient and amplitude (if cyclical) of the drift, and
            # the general conditions, e.g. whether it must be positive, is the
            # noise truncated
            self.drift_type = config_dict['drift_type']
            self.always_pos = config_dict['always_pos']
            self.noise_truncated = config_dict['noise_truncated']
            self.gradient = config_dict['gradient']
            self.amplitude = config_dict['amplitude']

            # Sets the dirfting clipping (i.e. so drifting cannot exceed a
            # defined set of boundaries)
            self.drift_clip = config_dict['drift_clip']
            self.clip_high_bnd = config_dict['clip_high_bnd']
            self.clip_low_bnd = config_dict['clip_low_bnd']

        else:
            # Sets the noise parameters
            self.noise = noise
            self.noise_mean = noise_mean
            self.noise_sd = noise_sd
            self.noise_low_bnd = noise_low_bnd
            self.noise_high_bnd = noise_high_bnd

            # Sets the gradient and amplitude (if cyclical) of the drift, and
            # the general conditions, e.g. whether it must be positive, is the
            # noise truncated
            self.drift_type = drift_type
            self.always_pos = always_pos
            self.noise_truncated = noise_truncated
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
            if self.noise_truncated:
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
