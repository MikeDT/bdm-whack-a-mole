# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 17:57:43 2019

@author: miketaylor
"""

import random
import numpy as np

class Scorer:
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

    def iter_adj(self, adj_type):
        self.call_count += 1
        if adj_type == 'static':
            self.score_adj = 1
        elif adj_type == 'random_walk':
            self.score_adj = np.random.beta(self.beta_a, self.beta_b)
        elif adj_type == 'random_walk_pos':
            self.beta_b += self.call_count*self.rw_grad
            self.score_adj = np.random.beta(self.beta_a,
                                            self.beta_b)
        elif adj_type == 'random_walk_neg':
            self.beta_a += self.call_count*self.rw_grad
            self.score_adj = np.random.beta(self.beta_a,
                                            self.beta_b)
        elif adj_type == 'designed_trend':
            self.score_adj = np.random.beta(self.trend[self.call_count][0],
                                            self.trend[self.call_count][1])

    def reset(self, default=True, *, beta_a=1, beta_b=1, call_count=1):
        if default:
            self.beta_a = self.beta_a_start
            self.beta_b = self.beta_b_start
            self.call_count = 0
        else:
            self.beta_a = beta_a
            self.beta_b = beta_b
            self.call_count = call_count

    def get_score(self, mouse_pos, frame_num,
                  score_type='boolean', adj_type='static'):
        self.iter_adj(adj_type)
        if score_type == 'boolean':
            score = self.max_score
        elif score_type == 'lin_dist_skill':
            distance = (mouse_pos[0] - self.hole_positions[frame_num][0],
                        mouse_pos[1] - self.hole_positions[frame_num][1])
            distance = (distance[0]**2 + distance[1]**2)**0.5
            score = 10 - (min(10, 0.05*distance))
        elif score_type == 'non_lin_dist_skill':
            distance = (mouse_pos[0] - self.hole_positions[frame_num][0],
                        mouse_pos[1] - self.hole_positions[frame_num][1])
            distance = (distance[0]**2 + distance[1]**2)**0.5
            score = 10 - (min(10, 0.05*distance**1.1))
        else:
            score = self.max_score
        score = min(score * self.score_adj, 10)
        return round(score)
