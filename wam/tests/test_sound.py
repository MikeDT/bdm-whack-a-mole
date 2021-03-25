# -*- coding: utf-8 -*-
"""
test_sound module
============

This module contains the pytest functions for the sound class from
the scorer module for the pygame Whack a Mole game

Attributes:
    handled within the functions

Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: miketaylor
"""


import numpy as np
import pygame

from .. import sound

pygame.init()

test_sound = sound.SoundEffect(main_track_loc="..//sounds//themesong.wav",
                               fire_sound_loc="..//sounds//fire.wav",
                               pop_sound_loc="..//sounds//pop.wav",
                               hurt_sound_loc="..//sounds//hurt.wav",
                               select_sound_loc="..//sounds//select.wav",
                               level_sound_loc="..//sounds//point.wav")


def test_sound_init():
    assert test_sound.main_track_loc == "..//sounds//themesong.wav"
    assert test_sound.fire_sound_loc == "..//sounds//fire.wav"
    assert test_sound.pop_sound_loc == "..//sounds//pop.wav"
    assert test_sound.hurt_sound_loc == "..//sounds//hurt.wav"
    assert test_sound.select_sound_loc == "..//sounds//select.wav"
    assert test_sound.level_sound_loc == "..//sounds//point.wav"
    assert test_sound.fire_vol == 1.0
    assert test_sound.pop_vol == 0.8
    assert test_sound.hurt_vol == 0.3
    assert test_sound.level_vol == 0.7
    assert test_sound.music_vol == 0.15
