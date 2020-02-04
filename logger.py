# -*- coding: utf-8 -*-
"""
logger module
============

This module contains the WamLogger class for the pygame Whack a Mole game

Attributes:
    handled within the WamLogger Class

Todo:
    * sort naked exception handling

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole)

@author: miketaylor
"""

import logging
from time import time
import os
import pygame


class WamLogger:
    """
    Logs the events within the game to a .log (text) file

    Attributes
    ----------
    na

    Methods
    -------
    create_log_instance()
        creates the logging text .log file
    log_it(event)
        logs an event that is passed to it
    end_log()
        closes down the log
    """
    def __init__(self):
        self.timestamp = str(time())
        self.logger = logging.getLogger('BDM-WAM ' + self.timestamp)
        if not len(self.logger.handlers):
            self.create_log_instance()

    def create_log_instance(self):
        '''
        Creates an instance of the log file in the log folder, marked up with
        the current timestamp

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
        self.logger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(r'../bdm-whack-a-mole/logs/' +
                                      'BDM-WAM ' +
                                      self.timestamp + '.log')
        self.fh.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.ERROR)

        # create formatter and add it to the handlers
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - ' +
                                           '%(levelname)s - %(message)s')
        self.fh.setFormatter(self.formatter)
        self.ch.setFormatter(self.formatter)

        # add the handlers to the logger
        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.ch)

    def _log_it(self, event=False):
        '''
        logs events within the game, either by being passed an event, or by
        pulling event from the pygame construct, then adding to the logger

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
        if event:
            try:
                self.logger.info(event)
            except:
                self.logger.info('Event Logging Failure')
        else:
            try:
                self.logger.info(pygame.event.get())
            except:
                self.logger.info('Event Logging Failure')

    def log_pygame_event(self, event):
        self._log_it(event)

    def log_score(self, score_inc, score):
        score_str = ("score_inc: " + str(score_inc) + "," +
                     "score: " + str(score) + "})>")
        self._log_it("<Event(11-Score {" + score_str)

    def log_pause(self, pause_reason):
        self._log_it("<Event(8-Pause {'reason': " + str(pause_reason) + " })>")

    def log_event_rate(self, action, event_act):
        self._log_it("<Event(7-Rate {'" + action + "': " + event_act + " })>")

    def log_mole_event(self, xy):
        log_string = ("{'loc': (" +
                      str(xy[0]) + "," + str(xy[1]) +
                      ")})>")
        self._log_it("<Event(10-MoleUp) " + log_string)

    def log_hit_result(self, result, mouse_x, mouse_y, distance, relative_loc):
        """
        Logs the hit result based on the current mole hit criteria
        """
        log_string = ("{'pos': (" +
                      str(mouse_x) + "," +
                      str(mouse_y) + ")," +
                      "'distance: " + str(distance) + "," +
                      "'relative_loc: " + str(relative_loc) + "," +
                      "'window': None})>")
        if result == (True, True):
            self._log_it("<Event(9.1-TrueHit " + log_string)
        elif result == (False, True):
            self._log_it("<Event(9.2-FakeMiss " + log_string)
        elif result == (True, False):
            self._log_it("<Event(9.3-FakeHit " + log_string)
        else:
            self._log_it("<Event(9.4-TrueMiss " + log_string)

    def log_end(self):
        '''
        shuts down the log file

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
        self.logger.info('************* HAPPY ANALYSING... ' +
                         'LOG COMPLETE!!! ************* ')
        logging.shutdown()
        self.fh.close()
        self.ch.close()
