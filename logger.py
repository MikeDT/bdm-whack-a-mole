# -*- coding: utf-8 -*-
"""
logger module
============

This module contains the WamLogger class for the pygame Whack a Mole game

Attributes:
    na

Todo:
    * sort docstrings (e.g. class)

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: miketaylor
"""

import logging
from time import time
import pygame
import csv


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
        self.logger = logging.getLogger('WAM Events ' + self.timestamp)
        self.log_file_root = r'../bdm-whack-a-mole/logs/'
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
        OSError
            If the file cannot be created
        '''
        self.logger.setLevel(logging.DEBUG)
        try:
            self.fh = logging.FileHandler(self.log_file_root +
                                          'WAM Events ' +
                                          self.timestamp + '.log')
        except OSError:
            print('Log file could not be created')
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

    def log_class_dict(self, class_name, class_dict):
        with open(self.log_file_root + ' WAM Conditions' +
                  self.timestamp + '.log',
                  'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([class_name])
            for key, value in class_dict.items():
                writer.writerow([key, value])
            writer.writerow([])

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
            however the class does write to the logger in the event of a
            logging failure (assumption being the logging component is
            sufficiently robust and well documented to not require additional
            non-naked exceptions)
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
        '''
        Logs a generic event in the game (i.e. pygame native)

        Parameters
        ----------
        event: pygame event object
            pygame event object

        Returns
        -------
        na
            logs the event via _log_it
        '''
        self._log_it(event)

    def log_2x2_rate(self, mouse_pos, TWO_X_TWO_LOC, TWO_X_TWO_LEN):
        '''
        Logs the players rating using the 2x2 grid system

        Parameters
        ----------
        mouse_pos: 2 int tuple
            The xy coorindates of the rating

        Returns
        -------
        na
            logs the event via _log_it
        '''
        x = (mouse_pos[0] - TWO_X_TWO_LOC[0]) / TWO_X_TWO_LEN
        y = (mouse_pos[1] - TWO_X_TWO_LOC[1]) / TWO_X_TWO_LEN
        self._log_it("<Event(7-Rate {xy : " + str((x, y)) + " })>")

    def log_score(self, score_inc, score):
        '''
        Logs the score, and the increment to the score

        Parameters
        ----------
        score_inc: float
            The increment to the score
        score: float
            The current score

        Returns
        -------
        na
            logs the event via _log_it
        '''
        score_str = ("score_inc: " + str(score_inc) + "," +
                     "score: " + str(score) + "})>")
        self._log_it("<Event(11-Score {" + score_str)

    def log_pause(self, pause_reason):
        '''
        Logs a pause request

        Parameters
        ----------
        pause_reason: string
            The reason for the pause (e.g. demo ending, stage etc.)

        Returns
        -------
        na
            logs the event via _log_it
        '''
        self._log_it("<Event(8-Pause {'reason': " + str(pause_reason) + " })>")

    def log_event_rate(self, action, event_act):
        '''
        Logs the rating event result

        Parameters
        ----------
        action: string
            The rating type (partially deprecated)
        event_act: int
            The rating

        Returns
        -------
        na
            logs the event via _log_it
        '''
        self._log_it("<Event(7-Rate {'" + action + "': " + event_act + " })>")

    def log_mole_event(self, xy):
        '''
        Logs the hit result for a given attempt

        Parameters
        ----------
        xy: tuple
            The x and y coordinates of a mole emerging

        Raises
        ------
        AssertionError
            Checks whether the xy coordinate is indeed a length two object

        Returns
        -------
        na - logs the event via _log_it
        '''
        try:
            assert len(xy) == 2
        except AssertionError:
            print('Mole event xy coorindates did not contain exactly two dims')
        log_string = ("{'loc': (" +
                      str(xy[0]) + "," + str(xy[1]) +
                      ")})>")
        self._log_it("<Event(10-MoleUp) " + log_string)

    def log_hit_result(self, result, xy, distance, relative_loc):
        '''
        Logs the hit result for a given attempt

        Parameters
        ----------
        result: tuple
            The actual hit, margin hit and reported hit results
        xy: tuple
            The x and y coordinates of a mole emerging
        distance: int
            The distance from the centre of the mole
        relative_loc: 2 int tuple
            The relative location from mole centre for the strike

        Raises
        ------
        AssertionError
            Checks whether the xy coordinate is indeed a length two object

        Returns
        -------
        na - logs the event via _log_it
        '''
        try:
            assert len(xy) == 2
        except AssertionError:
            print('Mole event xy coorindates did not contain exactly two dims')
        log_string = ("{'pos': (" +
                      str(xy[0]) + "," +
                      str(xy[1]) + ")," +
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
        shuts down the logger and log file

        Parameters
        ----------
        self : self

        Returns
        -------
        na - ends log
        '''
        self.logger.info('******* HAPPY ANALYSING...LOG COMPLETE!!! *******')
        logging.shutdown()
        self.fh.close()
        self.ch.close()
