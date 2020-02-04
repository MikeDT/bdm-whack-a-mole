# -*- coding: utf-8 -*-
"""
main
====

Primary module, contains the majority of the game code for the
Whack a Mole game

Attributes:
    na

Todo:
    * animate mole for toggling animation durations
    * make the game constants a config read
        * sort pause_reason text import
        * 
    * clean up game pause text (push to a dictionary, reason: text)
    * make hole positions a config change
    * create log string function, then log it
    * sort check key event
    * check mouse_event needs more abstraction
    * build 2x2 rater
    * make all check events link to a ting that checks whether the agent is artificial or not
    * put all logging stuff into the logger class, just pass it the situ
    
    * abstract the screen functionality to make the GameManager
        standalone
    * confidence in hit vs precision of hit?
    * confidence in score feels like it would make more sense
        for instant feedback (otherwise confidence is anchored to just one)
    * confidence in target
    * degree of luck
    * hit but don't do properly?
    * read the BdM papers
    * if touch on playing screen and vice versa

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole)

@author: miketaylor
"""


import pygame
import random
import numpy as np
from sound import SoundEffect
from logger import WamLogger
from scorer import Scorer
import re


class GameManager:
    def __init__(self):

        # Define constants
        self.SCREEN_WIDTH = 1424
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        self.MOLE_WIDTH = 90
        self.MOLE_HEIGHT = 81
        self.FONT_SIZE = 18
        self.FONT_TOP_MARGIN = self.SCREEN_HEIGHT + 100 - 26
        self.STAGE_SCORE_GAP = 4
        self.LEFT_MOUSE_BUTTON = 1
        self.GAME_TITLE = "BDM Whack-A-Mole Experiment"

        # Define file locations
        self.intro_txt_file_loc = 'text\\intro.txt'
        self.hole_pos_file_loc = 'config\\hole_positions.txt'
        self.pause_info_file_loc = 'config\\pause_info.txt'

        # Initialize player's score, number of missed hits and stage data
        self.feedback = True
        self.intro_complete = False
        self.stage_time_change = True
        self.demo_len = 5
        self.stage, self.demo = 'Demo', True
        self.stage_type = 'Standard'  # Standard or Attempts
        self.score = 0
        self.misses = 0
        self.mole_count = 0  # moles hit in stage
        self.feedback_count = 0  # iterations since last player feedback
        self.feedback_limit = 1  # iterations per player feedback
        self.update_count = 0  # iterations since last score update
        self.update_delay = 0  # iterations per score update
        self.stage_length = 10
        self.stages = 5
        self.stage_pts = range(self.demo_len,
                               self.stages*self.stage_length + self.demo_len,
                               self.stage_length)
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,
                                               self.SCREEN_HEIGHT + 100))
        pygame.display.set_caption(self.GAME_TITLE)
        if self.SCREEN_WIDTH == 1600:
            self.background = pygame.image.load("images/bg 1600x1300.png")
        else:
            self.background = pygame.image.load("images/bg_2x2_1424x700.png")

        # Create/Import the hole positions in background
        self.hole_positions = self.get_hole_pos()

        # Initialize the mole's sprite sheet (6 different states)
        sprite_sheet = pygame.image.load("images/mole.png")
        self.mole = []
        self.mole.append(sprite_sheet.subsurface(169, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(309, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(449, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(575, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(717, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(853, 0, 116, 81))

        # Initialise sound effects
        self.soundEffect = SoundEffect()
        self.pause_reason = False
        self.pause_list = [False, 'standard', 'hit_conf',
                           'rate_skill', 'rate_env', 'stage']
        self.event_key_dict = {'49': '1', '50': '2', '51': '3', '52': '4',
                               '53': '5', '54': '6', '55': '7', '56': '8',
                               '57': '9'}

        # Initialise the score adjustment functions and data
        self.scorer = Scorer(self.hole_positions)
        self.margin = 10
        self.score_type = 'Normal'  # 'boolean' or 'nonlin_dist_skill'
        self.adj_type = 'static' # random_walk_neg, random_walk_pos, static, designed
        self.hit_type = 'Margin'

        # Import text information
        self.font_obj = pygame.font.SysFont("comicsansms", 20)
        self.intro_txt = open(self.intro_txt_file_loc, 'r').read().split('\n')
        self.pause_reason_dict = self.get_pause_dict()
        
        # Define pause transitions
        self.pause_trans_dict = {'hit_conf': 'reward_conf',
                                 'reward_conf': 'player_skill',
                                 'player_skill': False}

        # Sets up logging
        self.wam_logger = WamLogger()

    def get_hole_pos(self):
        hole_pos_lst = open(self.hole_pos_file_loc, 'r').read().split('|')
        def cleaner(a): return re.sub("|".join(['\(', '\)', ' ']), '', a)
        hole_pos_lst = [cleaner(x).split(',') for x in hole_pos_lst]
        hole_pos_lst = [[int(x) for x in sub_lst] for sub_lst in hole_pos_lst]
        return hole_pos_lst

    def get_pause_dict(self):
        pause_list = open(self.pause_info_file_loc, 'r').read().split('\n')
        pause_list = [x.split(' |') for x in pause_list]
        pause_dict = {x[0]: x[1] for x in pause_list}
        return pause_dict

    @staticmethod
    def text_objects(text, font):
        """
        Sets the text objects for the gui, static method as only called once
        """
        text_surface = font.render(text, True, (50, 50, 50))  # (0,0,0) = black
        return text_surface, text_surface.get_rect()

    def intro(self):
        """
        Sets the introduction text on the screen and provides a set of
        instructions to the user
        """
        while self.intro_complete is False:
            loc_y = self.SCREEN_HEIGHT/2 - 80
            for line in self.intro_txt:
                self.write_text(line, location_y=loc_y)
                loc_y += 40

#            self.check_key_event()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.wam_logger.log_end()
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.intro_complete = True
                    elif event.key == pygame.K_q:
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_CTRL:
                            pygame.quit()
                            self.wam_logger.log_end()

    def write_text(self, string, colour=(255, 255, 255),
                   location_x=None, location_y=None):
        """
        Writes text to the screen, defaulting to the centre
        """
        if location_x is None:
            location_x = self.background.get_rect().centerx
        if location_y is None:
            location_y = self.SCREEN_HEIGHT / 2
        text = self.font_obj.render(string, True, colour)
        text_pos = text.get_rect()
        text_pos.centerx = location_x
        text_pos.centery = location_y
        self.screen.blit(text, text_pos)
        pygame.display.update()

    def check_key_event(self, event=False):
        """
        Monitors the game for events
        """
        if event:
            event_list = [] + [event]
        else:
            event_list = pygame.event.get()
        for event in event_list:
            self.current_event = event
            if self.current_event.type == pygame.QUIT:
                self.loop = False
                self.wam_logger.log_end()
                pygame.quit()
            if self.current_event.type == pygame.KEYDOWN:
                if self.current_event.key == pygame.K_c:
                    self.pause_reason = False
                elif self.current_event.key == pygame.K_p:
                    self.pause_reason = 'standard'
                    self.pause()
                elif self.current_event.key == pygame.K_q:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:
                        pygame.quit()
                        self.wam_logger.log_end()

    def check_events_rate(self, action):
        """
        Monitors the game for player feedback provided via keys
        """
        for event in pygame.event.get():
            self.curr_event = event
            if event.type == pygame.QUIT:
                self.wam_logger.log_end()
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1,
                                 pygame.K_2,
                                 pygame.K_3,
                                 pygame.K_4,
                                 pygame.K_5,
                                 pygame.K_6,
                                 pygame.K_7]:
                    event_act = self.event_key_dict[str(event.key)]
                    self.wam_logger.log_event_rate(action[0], event_act)
#                    self.wam_logger.log_it("<Event(7-Rate {'" +
#                                           action[0] + "': " +
#                                           event_act + " })>")
                    self.pause_reason = action[1]
                elif event.key == pygame.K_q:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:
                        pygame.quit()
                        self.wam_logger.log_end()
                        
    def two_by_two_rate(self):
        """
        refactor check mouse event into two, i.e. mole hit check or 2x2
        then take xy coordinates, only unpause if the spot is given in the grid
        cast te confidence etc as part of the hit info into the logger
        """
        pass
    
    def pause(self):
    
         while self.pause_reason:
            if self.pause_reason in ['standard', 'stage', 'demo']:
                if self.pause_reason == 'stage':
                    self.update()
                    self.write_text(self.pause_reason_dict[self.pause_reason],
                                    location_y=self.SCREEN_HEIGHT/2 + 40)
                    self.check_key_event()
                elif self.pause_reason == 'standard':
                    self.write_text(self.pause_reason_dict[self.pause_reason])
                    self.check_key_event()
                else:
                    self.write_text(self.pause_reason_dict[self.pause_reason],
                                    location_y=self.SCREEN_HEIGHT/2 + 40)
                    self.scorer.reset_score_adj()
                    self.check_key_event()

            elif self.pause_reason == 'hit_conf':
                self.write_text(self.pause_reason_dict[self.pause_reason],
                                location_y=self.SCREEN_HEIGHT/2 - 80)
                self.check_events_rate(('hit_conf', 'reward_conf'))
                #self.check_event_rate((self.pause_reason,
                  #                     self.pause_trans_dict[self.pause_reason]))
            elif self.pause_reason == 'reward_conf':
                self.write_text(self.pause_reason_dict[self.pause_reason],
                                location_y=self.SCREEN_HEIGHT/2 - 40)
                self.check_events_rate(('reward_conf', 'player_skill'))
                #self.check_event_rate((self.pause_reason,
                 #                      self.pause_trans_dict[self.pause_reason]))
            elif self.pause_reason == 'player_skill':
                self.write_text(self.pause_reason_dict[self.pause_reason],
                                location_y=self.SCREEN_HEIGHT/2)
                #self.check_event_rate((self.pause_reason,
                 #                      self.pause_trans_dict[self.pause_reason]))
                self.check_events_rate(('player_skill', False))

    def pause_new(self):
        """
        HAndles pause events, needs to be abstracted into more functions
        """
        self.wam_logger.log_pause(self.pause_reason)
#        self.wam_logger.log_it("<Event(8-Pause {'reason': " +
#                               str(self.pause_reason) + " })>")
        location_y = self.SCREEN_HEIGHT/2 - 80
        while self.pause_reason:
            if self.pause_reason in ['standard',
                                     'stage',
                                     'demo']:
                self.write_text(self.pause_reason_dict[self.pause_reason],
                                location_y=location_y)
                self.check_key_event()
            elif self.pause_reason in ['hit_conf',
                                       'reward_conf',
                                       'player_skill']:
                self.write_text(self.pause_reason_dict[self.pause_reason],
                                location_y=location_y)

            location_y += 40

    def set_player_stage(self):
        """
        Sets the game stage based upon the stage type and pause_reason
        """
        if self.stage_type == 'Standard':
            if (self.mole_count) in self.stage_pts:
                if self.demo:
                    self.misses = 0
                    self.score = 0
                    self.stage = 1
                    self.pause_reason = 'demo'
                    self.demo = False
                    self.pause()
                else:
                    self.soundEffect.play_stage_up()
                    self.pause_reason = 'stage'
                    self.pause()
                    self.stage += 1

    def get_interval_by_stage(self, initial_interval):
        """
        Gets the game interval (i.e. the time between mole pop ups from holes)
        period by stage
        """
        if self.stage == 'Demo':
            stage = 1
        else:
            stage = self.stage
        if self.stage_time_change:
            new_interval = initial_interval - stage * 0.15
            if new_interval > 0:
                return new_interval
            else:
                return 0.05
        else:
            return 1.0

    def check_mole_hit(self, mouse_pos, current_hole_position):
        """
        Checks whether a mole was hit, able to call a variety of methods
        dependent on the type of mole hit that is modelled for in the game at
        a given point in time (e.g. standard, with additional margin, binomial
        etc.
        """
        self.mouse_x = mouse_pos[0]
        self.mouse_y = mouse_pos[1]
        self.current_hole_x = current_hole_position[0]
        self.current_hole_y = current_hole_position[1]
        self.distance = ((self.mouse_x - self.current_hole_x)**2 +
                         (self.mouse_y - self.current_hole_y)**2)**0.5
        self.relative_loc = (self.mouse_x - self.current_hole_x,
                             self.mouse_y - self.current_hole_y)
        self.feedback_count += 1
        if self.feedback_count == self.feedback_limit:
            self.feedback_count = 0
            self.pause_reason = 'hit_conf'
            self.pause()
        if self.hit_type == 'Margin':
            self.set_mole_hit_res_margin()
        elif self.hit_type == 'Standard':
            self.set_mole_hit_res_standard()
        elif self.hit_type == 'Binomial':
            self.set_mole_hit_res_binom()
        #self.log_hit_result()
        self.wam_logger.log_hit_result(self.result, self.mouse_x, self.mouse_y,
                                       self.distance, self.relative_loc)
        return self.result[0]

    def set_mole_hit_res_binom(self):
        """
        As per the simple mole hit model, but with an added margin of error
        that can be adjusted intra or inter game
        """
        actual_hit = False
        binom_hit = False   
        if ((self.mouse_x > self.current_hole_x) and
            (self.mouse_x < self.current_hole_x + self.MOLE_WIDTH) and
            (self.mouse_y > self.current_hole_y) and
            (self.mouse_y < self.current_hole_y + self.MOLE_HEIGHT)):
            if (np.random.binomial(1, 0.5, 1)[0]) > 0:
                actual_hit, binom_hit = True, True
            else:
                actual_hit, binom_hit = False, True
        else:
            if (np.random.binomial(1, 0.5, 1)[0]) > 0:
                actual_hit, binom_hit = True, False
            else:
                actual_hit, binom_hit = False, False
        self.result = (actual_hit, binom_hit)

    def set_mole_hit_res_margin(self):
        """
        As per the simple mole hit model, but with an added margin of error
        that can be adjusted intra or inter game
        """                
        actual_hit = False
        margin_hit = False
        if ((self.mouse_x > self.current_hole_x) and
            (self.mouse_x < self.current_hole_x + self.MOLE_WIDTH) and
            (self.mouse_y > self.current_hole_y) and
            (self.mouse_y < self.current_hole_y + self.MOLE_HEIGHT)):
            actual_hit = True
        if ((self.mouse_x > self.current_hole_x - self.margin) and
            (self.mouse_x < self.current_hole_x + self.MOLE_WIDTH + self.margin) and
            (self.mouse_y > self.current_hole_y - self.margin) and
            (self.mouse_y < self.current_hole_y + self.MOLE_HEIGHT + self.margin)):
            margin_hit = True
        self.result = (actual_hit, margin_hit)

    def set_mole_hit_res_standard(self):
        """
        Simplest model of mole hits, with no adjustment
        """
        actual_hit = False
        if ((self.mouse_x > self.current_hole_x) and
            (self.mouse_x < self.current_hole_x + self.MOLE_WIDTH) and
            (self.mouse_y > self.current_hole_y) and
            (self.mouse_y < self.current_hole_y + self.MOLE_HEIGHT)):
            actual_hit = True
        self.result = (actual_hit, actual_hit)
#
#    def log_hit_result(self):
#        """
#        Logs the hit result based on the current mole hit criteria
#        """
#        log_string = ("{'pos': (" +
#                      str(self.mouse_x) + "," +
#                      str(self.mouse_y) + ")," +
#                      "'distance: " + str(self.distance) + "," +
#                      "'relative_loc: " + str(self.relative_loc) + "," +
#                      "'window': None})>")
#        if self.result == (True, True):
#            self.wam_logger.log_it("<Event(9.1-TrueHit " + log_string)
#        elif self.result == (False, True):
#            self.wam_logger.log_it("<Event(9.2-FakeMiss " + log_string)
#        elif self.result == (True, False):
#            self.wam_logger.log_it("<Event(9.3-FakeHit " + log_string)
#        else:
#            self.wam_logger.log_it("<Event(9.4-TrueMiss " + log_string)

    def score_update_check(self):
        """
        Checks whether an update should be performed
        """
        if self.demo:
            self.update()
        elif self.update_count == self.update_delay:
            self.update()
        else:
            self.update_count += 1

    def update(self, really_update=True):
        """
        Updates the game's stage, score, misses on the gui
        """
        # Update gui with player's score
        current_score_string = "SCORE: " + str(self.score)
        score_text = self.font_obj.render(current_score_string,
                                          True, (1, 1, 1))
        score_text_pos = score_text.get_rect()
        score_text_pos.centerx = self.background.get_rect().centerx
        score_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(score_text, score_text_pos)

        # Update gui with player's misses
        current_misses_string = "MISSES: " + str(self.misses)
        misses_text = self.font_obj.render(current_misses_string,
                                           True, (1, 1, 1))
        misses_text_pos = misses_text.get_rect()
        misses_text_pos.centerx = self.SCREEN_WIDTH / 5 * 4
        misses_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(misses_text, misses_text_pos)

        # Update gui with player's stage
        current_stage_string = "STAGE: " + str(self.stage)
        stage_text = self.font_obj.render(current_stage_string,
                                          True, (1, 1, 1))
        stage_text_pos = stage_text.get_rect()
        stage_text_pos.centerx = self.SCREEN_WIDTH / 5 * 1
        stage_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(stage_text, stage_text_pos)

    def get_agent_mouse_pos(self, human=True):
        if human:
            pygame.mouse.get_pos()
        else:
            pass

    def check_mouse_event(self, event, num, left, mole_is_down, interval, frame_num):
        """
        Checks whether a couse event has resulted in a mole hit
        
        requires further abstraction
        """
        if (event.type == pygame.MOUSEBUTTONDOWN and
            event.button == self.LEFT_MOUSE_BUTTON):
            self.soundEffect.play_fire()
            if (self.check_mole_hit(pygame.mouse.get_pos(),
                                 self.hole_positions[frame_num]) and
                num > 0 and left == 0):
                num = 3
                left = 14
                mole_is_down = False
                interval = 0
                mouse_pos = self.get_agent_mouse_pos()
                score_inc = self.scorer.get_score(mouse_pos,
                                                  frame_num,
                                                  self.score_type,
                                                  self.adj_type)
                self.score += score_inc
                self.wam_logger.log_score(score_inc, self.score)
#                score_str = ("score_inc: " + str(score_inc) + "," +
#                               "score: " + str(self.score) + "})>")
#                self.wam_logger.log_it("<Event(11-Score {" + score_str)

                # Stop popping sound effect
                self.soundEffect.stop_pop()
                # Play hurt sound
                if self.feedback:
                    self.soundEffect.play_hurt()
                self.mole_count += 1
                self.score_update_check()
            else:
                self.misses += 1
                self.mole_count += 1
                self.score_update_check()
            self.set_player_stage()

        return num, left, mole_is_down, interval, frame_num
    
    def pop_mole(self, num, mole_is_down, interval, frame_num):
        self.screen.blit(self.background, (0, 0))
        self.score_update_check()
        num = 0
        mole_is_down = False
        #interval = 0.5
        frame_num = random.randint(0, 8)
        self.wam_logger.log_mole_event(self.hole_positions[frame_num])
#        log_string = (
#                      "{'loc': (" +
#                      str(self.hole_positions[frame_num][0]) + "," +
#                      str(self.hole_positions[frame_num][1]) + ")})>"
#                      )
#        self.wam_logger.log_it("<Event(10-MoleUp) " + log_string)
        return num, mole_is_down, interval, frame_num

    def show_mole_frame(self, num, frame_num, left):
        '''
        Shows the specific mole animation frame at a given hole position

        Parameters
        ----------
        tbd : to be reworked

        Raises
        ------
        na

        Returns
        -------
        tbd : to be reworked
        '''
        pic = self.mole[num]
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(pic,
                         (self.hole_positions[frame_num][0] - left,
                          self.hole_positions[frame_num][1]))

    def animate_mole(self, num, left, mole_is_down, interval,
                     frame_num, initial_interval, cycle_time, clock):
        '''
        Animates/governs the mole popping/whacking/dropping sequence

        Parameters
        ----------
        tbd : to be reworked

        Raises
        ------
        na

        Returns
        -------
        tbd : to be reworked
        '''
        self.show_mole_frame(num, frame_num, left)
        self.score_update_check()
        if mole_is_down is False:
            num += 1
        else:
            num -= 1
        if num == 4:  # i.e. the period of whacking
            interval = 0.5
        elif num == 3:
            num -= 1
            mole_is_down = True
            self.soundEffect.play_pop()
            interval = 0.5  # self.get_interval_by_stage(initial_interval)
        else:
            interval = .5  # 0.1
        cycle_time = 0
        return num, left, mole_is_down, interval, frame_num, initial_interval, cycle_time, clock

    def create_moles(self):
        """
        Creates a set of moles
        """
        for i in range(len(self.mole)):
            self.mole[i].set_colorkey((0, 0, 0))
            self.mole[i] = self.mole[i].convert_alpha()

    def play_game(self):
        """
        Play the whack a mole game
        """
        # Time control variables
        cycle_time = 0
        num = -1
        loop = True
        mole_is_down = False
        interval = 0.1
        initial_interval = 1
        frame_num = 0
        left = 0
        clock = pygame.time.Clock()
        self.create_moles()
        while loop:

            # log game events, and check whether key or mouse
            # events have occurred (and react appropriately)
            for event in pygame.event.get():
                self.wam_logger.log_pygame_event(event)
                if self.intro_complete is False:
                    self.intro()
                if event.type == pygame.QUIT:
                    loop = False
                self.check_key_event(event)
                num, left, mole_is_down, interval, frame_num = self.check_mouse_event(event, num, left, mole_is_down, interval, frame_num)

            # refreshes screen at the point of mole popping
            if num > 5:
                self.screen.blit(self.background, (0, 0))
                self.score_update_check()
                num = -1
                left = 0

            # pops the mole, if it's time
            if num == -1:
                num, mole_is_down, interval, frame_num = self.pop_mole(num, mole_is_down, interval, frame_num)

            # drops the mole, if it's time
            mil = clock.tick(self.FPS)
            sec = mil / 1000.0
            cycle_time += sec
            if cycle_time > interval:
                num, left, mole_is_down, interval, frame_num, initial_interval, cycle_time, clock = self.animate_mole(num, left, mole_is_down, interval, frame_num, initial_interval, cycle_time, clock)

            # Update the display
            pygame.display.flip()
