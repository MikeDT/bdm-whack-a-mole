# -*- coding: utf-8 -*-
"""
scorer module
============

This module contains the Scorer class for the pygame Whack a Mole game

Attributes:
    handled within the Scorer class

Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole)

@author: miketaylor
"""

import numpy as np


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
    get_distance(mouse_pos, frame_num)
        gets the euclidean distance between the strike and the mole centre,
        using the mouse position and the frame_num (which provides the mole
        hole location)
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

    def increment_iter_adj(self, adj_type):
        '''
        Incerments the iterative adjuster, currently the beta distribution

        Parameters
        ----------
        self : self

        Raises
        ------
        na

        Returns
        -------
        na
        '''
        self.call_count += 1
        if adj_type == 'static':
            self.score_adj = 1
        elif adj_type == 'rnd_wlk':
            self.score_adj = np.random.beta(self.beta_a, self.beta_b)
        elif adj_type == 'rnd_wlk_pos':
            self.beta_b += self.call_count*self.rw_grad
            self.score_adj = np.random.beta(self.beta_a,
                                            self.beta_b)
        elif adj_type == 'rnd_wlk_neg':
            self.beta_a += self.call_count*self.rw_grad
            self.score_adj = np.random.beta(self.beta_a,
                                            self.beta_b)
        elif adj_type == 'design':
            self.score_adj = np.random.beta(self.trend[self.call_count][0],
                                            self.trend[self.call_count][1])

    def reset_score_adj(self, default=True, *,
                        beta_a=1, beta_b=1, call_count=1):
        '''
        Resets the beta distribution to its initial starting point (by default)
        or a defined a/b val and call count

        Parameters
        ----------
        default: Boolean
            toggles whether the default is used or not
        beta_a: int
            the a value for the beta distribution
        beta_b: int
            the b value for the beta distribution
        call_count: int
            the call count (i.e. how many iterations have been performed)

        Raises
        ------
        na

        Returns
        -------
        na
        '''
        if default:
            self.beta_a = self.beta_a_start
            self.beta_b = self.beta_b_start
            self.call_count = 0
        else:
            self.beta_a = beta_a
            self.beta_b = beta_b
            self.call_count = call_count

    def get_distance(self, mouse_pos, frame_num):
        '''
        Calculates the euclidean distance of the mouse position (or hand
        strike in touch screen deployment) and the mole that has popped

        Parameters
        ----------
        mouse_pos: tuple (2 long)
            the x,y coordinates of the mouse location
        frame_num: int
            the id of the mole (refers to the hole_positions attribute)

        Raises
        ------
        na

        Returns
        -------
        distance: float
            the euclidean distance from the optimal strike position
        '''
        distance = (mouse_pos[0] - self.hole_positions[frame_num][0],
                    mouse_pos[1] - self.hole_positions[frame_num][1])
        distance = (distance[0]**2 + distance[1]**2)**0.5
        return distance

    def score_skill_adjust(self, score_raw, score_type):
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
            score = score_raw - (min(10, 0.05*self.get_distance))
        elif score_type == 'non_lin_dist_skill':
            score = score_raw - (min(10, 0.05*self.get_distance))
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
        self.increment_iter_adj(adj_type)
        score = min(score * self.score_adj, 10)
        return score

    def get_score(self, mouse_pos, frame_num,
                  score_type='boolean', adj_type=None):
        '''
        Gets the score for an attempted mole whack

        Parameters
        ----------
        mouse_pos: tuple (2 long)
            the x,y coordinates of the mouse location
        frame_num: int
            the id of the mole (refers to the hole_positions attribute)
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
        score_skill_adj = self.score_skill_adjust(score_raw, adj_type)
        score_skill_random_adj = self.score_rand_adjust(score_skill_adj)
        score_skill_random_adj = round(score_skill_random_adj, 2)
        return score_skill_random_adj
