# -*- coding: utf-8 -*-
"""
test_distribution module
============

This module contains the pytest functions for the distribution
functions from the logger module for the pygame Whack
a Mole game

Attributes:
    handled within the functions

Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: miketaylor
"""

import logging
from time import time
import pygame
import csv
from pathlib import Path
import os

from .. import logger

test_logger = logger.WamLogger(usr_timestamp='test',
                               log_file_root='tests\\')
root_dir = os.getcwd()


def test_creation():
    try:
        open(root_dir + '\\tests\\WAM_Events_test.log')
        test = True
    # Do something with the file
    except IOError:
        test = False
    assert test


def test_pygame_event():
    test_logger.log_pygame_event('<test_event>')
    f = open(root_dir + '\\tests\\WAM_Events_test.log')
    text_lines = f.readlines()
    text = text_lines[-1]
    if text[-13:] == '<test_event>\n':
        test = True
    else:
        test = False
    assert test


def test_log_score():
    test_logger.log_score(10, 15)
    f = open(root_dir + '\\tests\\WAM_Events_test.log')
    text_lines = f.readlines()
    text = text_lines[-1]
    if text[-42:] == "11-Score {'score_inc': 10, 'score': 15})>\n":
        test = True
    else:
        test = False
    assert test


def test_log_pause():
    test_logger.log_pause('test')
    f = open(root_dir + '\\tests\\WAM_Events_test.log')
    text_lines = f.readlines()
    text = text_lines[-1]
    if text[-28:] == "8-Pause {'reason': test })>\n":
        test = True
    else:
        test = False
    assert test


def test_2x2_rate():
    test_logger.log_2x2_rate((5, 5), (0, 0), 10)
    f = open(root_dir + '\\tests\\WAM_Events_test.log')
    text_lines = f.readlines()
    text = text_lines[-1]
    if text[-62:] == ("7-Rate {'skill_vs_luck_rating': 0.5, 'hit_confidence': 0.5})>\n"):
        test = True
    else:
        test = False
    assert test


def test_log_mole_event():
    test_logger.log_mole_event((0, 0))
    f = open(root_dir + '\\tests\\WAM_Events_test.log')
    text_lines = f.readlines()
    text = text_lines[-1]
    if text[-28:] == ("10-MoleUp) {'loc': (0,0)})>\n"):
        test = True
    else:
        test = False
    assert test


def test_log_hit_result():
    test_logger.log_hit_result('test_result',
                               (0, 0),
                               100,
                               'test_relative_loc')
    f = open(root_dir + '\\tests\\WAM_Events_test.log')
    text_lines = f.readlines()
    text = text_lines[-1]
    if text[-123:] == ("9-Hit Attempt {'result': test_result, 'pos': " +
                       "(0, 0), 'distance': 100, 'relative_loc': " +
                       "test_relative_loc, 'window': None})>\n"):
        test = True
    else:
        test = False
    assert test


def test_log_shutdown():
    try:
        test_logger.log_end()
        # Tear Down the test log
        os.remove(root_dir + '\\tests\\WAM_Events_test.log')
        test = True
    except:
        test = False
    assert test
