# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 11:49:05 2020

@author: miketaylor

takes game situation (if artifical)
retrieves user actions 

one human agent
multiple artifical agents

create an agent (with the agent type dictating the agent type)

All agents called via same API
    check_mouse_event
    get_agent_mouse_pos
    check_key_event
    check_events_rate

"""

# -*- coding: utf-8 -*-
"""
agent module
============

This module contains the agent base and child classe for the pygame
 Whack a Mole game

Attributes:
    handled within the individual agent classes

Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license
    
@author: miketaylor
"""

import numpy as np


class Agent:
    """
    tbc

    Attributes
    ----------
    tbc: dt
        blurb

    Methods
    -------
    name(arg)
        desc
    """
    def __init__(self):
        pass
