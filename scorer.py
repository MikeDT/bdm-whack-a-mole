# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 17:57:43 2019

@author: miketaylor
"""

import random


class Scorer:
    def __init__(self, hole_positions):
        self.volatility = 0
        self.hole_positions = hole_positions

    def get_score(self, score_manip, mouse_pos, frame_num):
        score = 10
        if score_manip == 'full_random':
            score = random.choice(range(0, 11))
        elif score_manip == 'static_skill':
            distance = (mouse_pos[0] - self.hole_positions[frame_num][0],
                        mouse_pos[1] - self.hole_positions[frame_num][1])
            distance = (distance[0]**2 + distance[1]**2)**0.5
            score = max(0, score - distance)
        elif score_manip == 'standard':
            score = 10
        return score
