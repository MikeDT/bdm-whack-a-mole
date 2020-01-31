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

    def log_it(self, event=False):
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
