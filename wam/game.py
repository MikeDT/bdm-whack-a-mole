# -*- coding: utf-8 -*-
"""
main
====

Primary module, contains the majority of the game code for the
Whack a Mole game

Attributes:
    na

Todo:
    * fix pause between moles
    * make the game constants a config read (and write to a log)
    * sort check key event
    * create agent class for check events etc.
    * abstract the screen functionality to make the GameManager standalone
    * sort all the doc strings

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: DZLR3
"""


import pygame
import random
import pyautogui
from wam.sound import SoundEffect
from wam.logger import WamLogger
from wam.scorer import Scorer
from wam.drifter import Drifting_Val
from wam.hit_checker import Hit_Checker
import re
import pickle
import numpy as np


class GameManager:
    """
    The primary class, which manages the game and the access to the relevant
    other modules and classes

    Attributes
    ----------
    na

    Methods
    -------
    _get_hole_pos
        Property method, imports the hole poositions from the file (NB they
        reflect the image but do not dictate the image in the current
        implementation)
    _get_hole_centre
        Property method, returns the hole centre positions (i.e. where the
        middle of the mole is considered to be upon full emergence)
    _get_pause_dict
        Property method, imports a text file and creates a dictionary for the
        text displayed under given game pause conditions
    """
    # def __init__(self, file_config_loc=r"config\\Default.pkl",
    #              usr_timestamp=False):
    #     # hard coded stuff to integrate properly...
    #     self.skill_luck_rat = 1.0
    #     self.skill_ratio_master = 0.8
        
    #     self.skill_flip_counter = 0        
    #     self.skill_flip_floor = 8

    #     # Define file locations
    #     self.intro_txt_file_loc = 'text\\intro.txt'
    #     self.hole_pos_file_loc = 'config\\hole_positions.txt'
    #     self.pause_info_file_loc = 'text\\pause_info.txt'
    #     self.screen_img_file_loc = "images\\bg_2x2_v3_raw.png"
    #     self.mole_img_file_loc = "images\\mole.png"
    #     self.splash_img_file_loc = "images\\Splash_Screen.png"
    #     self.end_img_file_loc = "images\\End_Screen.png"
    #     self.file_config_loc = file_config_loc
    def __init__(self, file_config_loc=r"config/Default.pkl",
                  usr_timestamp=False):
        # hard coded stuff to integrate properly...
        self.skill_luck_rat = 1.0
        self.skill_ratio_master = 0.8
        self.skill_flip_counter = 0
        self.skill_flip_floor = 8
        # Define file locations
        self.intro_txt_file_loc = 'text/intro.txt'
        self.hole_pos_file_loc = 'config/hole_positions.txt'
        self.pause_info_file_loc = 'text/pause_info.txt'
        self.screen_img_file_loc = "images/bg_2x2_v3_raw.png"
        self.mole_img_file_loc = "images/mole.png"
        self.splash_img_file_loc = "images/Splash_Screen.png"
        self.end_img_file_loc = "images/End_Screen.png"

        try: 
            open('config/UK.txt', 'r')
            self.UK = True
        except:
            self.UK = False

        self.file_config_loc = file_config_loc
         
        master_dict = self.get_config_dict
        self.CONDITION_SET = master_dict['conditions_meta']['cond_set_name']
        import_dict = master_dict['main_game']

        # Define constants
        self.SCREEN_WIDTH = import_dict['SCREEN_WIDTH']
        self.SCREEN_HEIGHT = import_dict['SCREEN_HEIGHT']
        self.COMM_BAR_HEIGHT = import_dict['COMM_BAR_HEIGHT']
        self.TWO_X_TWO_LEN = import_dict['TWO_X_TWO_LEN']
        self.TWO_X_TWO_LOC = import_dict['TWO_X_TWO_LOC']
        self.FPS = import_dict['FPS']
        self.MOLE_WIDTH = import_dict['MOLE_WIDTH']
        self.MOLE_HEIGHT = import_dict['MOLE_HEIGHT']
        self.MOLE_RADIUS = import_dict['MOLE_RADIUS']
        self.MARGIN_START = import_dict['MARGIN_START']
        self.FONT_SIZE = import_dict['FONT_SIZE']
        self.FONT_TOP_MARGIN = (import_dict['SCREEN_HEIGHT'] +
                                import_dict['COMM_BAR_HEIGHT'] - 26)
        self.STAGE_SCORE_GAP = import_dict['STAGE_SCORE_GAP']

        # Initialize player's score, number of missed hits and stage data
        self.FEEDBACK = import_dict['FEEDBACK']
        self.stage_time_change = import_dict['stage_time_change']
        self.demo_len = import_dict['demo_len']
        self.demo = import_dict['demo']
        if self.demo:
            self.stage = 'Demo'
        else:
            self.stage = 1
        self.stage_type = import_dict['stage_type']
        self.feedback_limit = import_dict['feedback_limit']
        self.update_delay = import_dict['update_delay']
        self.stage_length = import_dict['stage_length']
        self.stages = import_dict['stages']
        self.stage_pts = [i for i in range(self.demo_len,
                                           self.stages*self.stage_length +
                                           self.demo_len,
                                           self.stage_length)]

        # Initialise Timing
        self.post_whack_interval = import_dict['post_whack_interval']
        self.mole_pause_interval = import_dict['mole_pause_interval']
        self.animation_interval = import_dict['animation_interval']
        self.mole_down_interval = import_dict['mole_down_interval']

        # Set game starting paramters
        self.score = 0
        self.score_t0 = 0
        self.misses = 0
        self.mole_count = 0  # moles hit in stage
        self.feedback_count = 0  # iterations since last player feedback
        self.update_count = 0  # iterations since last score update
        self.last_rate = False
        self.intro_complete = False

        # Initialise the score adjustment functions and data
        self.scorer = Scorer(self.MOLE_RADIUS,
                             config_dict=master_dict['scorer'])
        self.margin = Drifting_Val(self.MARGIN_START,
                                   config_dict=master_dict['margin_drifter'])
        self.hit_checker = Hit_Checker(self.MOLE_RADIUS,
                                       config_dict=master_dict['hit_checker'])

        # Initialise sound effects
        self.sound_effect = SoundEffect()

        # Import text information
        self.intro_txt = open(self.intro_txt_file_loc, 'r').read().split('\n')
        self.pause_reason_dict = self._get_pause_dict

        # Initialize screen and inputs
        self.GAME_TITLE = 'BDM Whack A Mole'
        self.LEFT_MOUSE_BUTTON = 1
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,
                                               self.SCREEN_HEIGHT +
                                               self.COMM_BAR_HEIGHT))
        pygame.display.set_caption(self.GAME_TITLE)
        self.background = pygame.image.load(self.screen_img_file_loc)
        self.splash_page = pygame.image.load(self.splash_img_file_loc)
        self.end_page = pygame.image.load(self.end_img_file_loc)
        self.screen.fill([255, 255, 255])

        # Create/Import the hole positions in background
        self.hole_positions = self._get_hole_pos  # for the animation
        self.hole_positions_centre = self._get_hole_cent  # for the hit centre

        # Set up keyboard linkages
        self.event_key_dict = {'49': '1', '50': '2', '51': '3', '52': '4',
                               '53': '5', '54': '6', '55': '7', '56': '8',
                               '57': '9'}
        # Setup pause conditions
        self.pause_reason = False
        self.pause_list = [False, 'standard', '2x2', 'stage']

        # Initialize the mole's sprite sheet (6 different states)
        sprite_sheet = pygame.image.load(self.mole_img_file_loc)
        self.mole = []
#        self.mole.append(sprite_sheet.subsurface(1, 0, 90, 81))  # no mole
        self.mole.append(sprite_sheet.subsurface(169, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(309, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(449, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(575, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(717, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(853, 0, 116, 81))

        # Sets up logging and log all the initial conditions
        self.wam_logger = WamLogger(usr_timestamp)
        self.log_init_conditions()

    @property
    def get_config_dict(self):
        master_dict = pickle.load(open(self.file_config_loc, 'rb'))
        return master_dict

    def log_init_conditions(self):
        self.wam_logger.log_class_dict('game_manager', self.__dict__)
        self.wam_logger.log_class_dict('sounds',
                                       self.sound_effect.__dict__)
        self.wam_logger.log_class_dict('margin',
                                       self.margin.__dict__)
        self.wam_logger.log_class_dict('hit_checker',
                                       self.hit_checker.__dict__)
        self.wam_logger.log_class_dict('scorer',
                                       self.scorer.__dict__)

    @property
    def _get_hole_pos(self):
        '''
        Property method, imports the hole poositions from the file
        (NB they reflect the image but do not dictate the image in the
        current implementation)

        Parameters
        ----------
        self : self

        Raises
        ------
        OSError
            If the file cannot be found

        Returns
        -------
        hole_pos_lst
            A list of hole position lists
        '''
        try:
            hole_pos_lst = open(self.hole_pos_file_loc, 'r').read().split('|')
            def cleaner(a): return re.sub("|".join(['\(', '\)', ' ']), '', a)
        except OSError:
            print("get_hole_pos function did not find the hole position file")
        hole_pos_lst = [cleaner(x).split(',') for x in hole_pos_lst]
        hole_pos_lst = [[int(x) for x in sub_lst] for
                        sub_lst in hole_pos_lst]

        return hole_pos_lst

    @property
    def _get_hole_cent(self):
        '''
        Property method, returns the hole centre positions (i.e. where the
        middle of the mole is considered to be upon full emergence)

        Parameters
        ----------
        self : self

        Returns
        -------
        hole_pos_centre: list
            list of the hole positions
        '''
        hole_pos_centre = [(x + self.MOLE_WIDTH/2, y + self.MOLE_HEIGHT/2) for
                           (x, y) in self.hole_positions]
        return hole_pos_centre

    @property
    def _get_pause_dict(self):
        '''
        Property method, imports a text file and creates a dictionary for the
        text displayed under given game pause conditions

        Parameters
        ----------
        self : self

        Raises
        ------
        OSError
            If the file cannot be found

        Returns
        -------
        pause_dict: dict
            dictionary of pause conditions and pause text
        '''
        try:
            pause_list = open(self.pause_info_file_loc, 'r').read().split('\n')
        except OSError:
            print("get_hole_pos function did not find the hole position file")
        pause_list = [x.split(' | ') for x in pause_list]
        pause_dict = {x[0]: x[1] for x in pause_list}
        return pause_dict

    # @property
    # @staticmethod
    # def _text_objects(text, font):
    #     '''
    #     Property method, imports a text file and creates a dictionary for the
    #     text displayed under given game pause conditions

    #     Parameters
    #     ----------
    #     self : self

    #     Returns
    #     -------
    #     pause_dict: dict
    #         dictionary of pause conditions and pause text
    #     '''
    #     text_surface = font.render(text, True, (0, 0, 0), (1,1,1))  # (0,0,0) = black
    #     return text_surface, text_surface.get_rect()

    def intro(self):
        '''
        Runs the game intro screen (basically communicates the text)

        Parameters
        ----------
        self : self
        '''
        self.screen.blit(self.splash_page, (0, 0))
        pygame.display.update()
        while self.intro_complete is False:
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
          
    def end(self):
        self.screen.fill([255, 255, 255])
        self.screen.blit(self.end_page, (0, 0))
        pygame.display.flip()

    def write_text(self, string, colour=(0, 0, 0), background=None, size=22,
                   location_x=None, location_y=None):
        """
        Writes text to the screen, defaulting to the centre
        """
        if location_x is None:
            location_x = self.background.get_rect().centerx
        if location_y is None:
            location_y = self.SCREEN_HEIGHT / 2
        if self.UK:
            font_obj = pygame.font.SysFont("comicsansms", size)
        else:
            font_obj = pygame.font.Font("fonts/YuseiMagic-Regular.ttf", size)
        text = font_obj.render(string, True, colour, background)
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

    def check_events_rate(self, action):  # to be deprecated
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
                    self.pause_reason = action[1]
                elif event.key == pygame.K_q:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:
                        pygame.quit()
                        self.wam_logger.log_end()

    def check_rate_in_grid(self, mouse_pos):
        if (
            (mouse_pos[0] > self.TWO_X_TWO_LOC[0]) and
            (mouse_pos[0] < self.TWO_X_TWO_LOC[0] + self.TWO_X_TWO_LEN) and
            (mouse_pos[1] > self.TWO_X_TWO_LOC[1]) and
            (mouse_pos[1] < self.TWO_X_TWO_LOC[1] + self.TWO_X_TWO_LEN)
        ):
            return True
        else:
            return False

    def two_by_two_rate(self):
        """
        refactor check mouse event into two, i.e. mole hit check or 2x2
        then take xy coordinates, only unpause if the spot is given in the grid
        cast te confidence etc as part of the hit info into the logger
        """
        for event in pygame.event.get():
            if (
                event.type == pygame.MOUSEBUTTONDOWN and
                event.button == self.LEFT_MOUSE_BUTTON
            ):
                mouse_pos = pygame.mouse.get_pos()
                if self.check_rate_in_grid(mouse_pos):
                    self.wam_logger.log_2x2_rate(mouse_pos, self.TWO_X_TWO_LOC,
                                                 self.TWO_X_TWO_LEN)
                    self.sound_effect.play_select()
                    self.pause_reason = False
                    self.last_rate = mouse_pos

    def pause(self):
        while self.pause_reason:
            if self.pause_reason in ['standard', 'stage', 'demo']:
                if self.pause_reason == 'stage':
                    if self.mole_count == self.stage_pts[-1]:
                        self.end()
                    else:
                        self.write_text(
                                self.pause_reason_dict[self.pause_reason],
                                background=(255,255,255),
                                location_y=650,#self.SCREEN_HEIGHT + 40,
                                location_x=1150)#self.SCREEN_HEIGHT + 40)
                    self.check_key_event()
                elif self.pause_reason == 'standard':
                    self.write_text(self.pause_reason_dict[self.pause_reason],
                                    background=(255,255,255),
                                    location_y=650,#self.SCREEN_HEIGHT + 40,
                                    location_x=1150)
                    self.check_key_event()
                else:
                    self.write_text(self.pause_reason_dict[self.pause_reason],
                                    background=(255,255,255),
                                    location_y=650,#self.SCREEN_HEIGHT + 40,
                                    location_x=1150)
                    self.check_key_event()
            elif self.pause_reason == '2x2':
                    self.write_text(self.pause_reason_dict[self.pause_reason],
                                    background=(255,255,255),
                                    location_y=650,#self.SCREEN_HEIGHT + 40,
                                    location_x=1150)
                    self.two_by_two_rate()

    def set_player_stage(self):
        """
        Sets the game stage based upon the stage type and pause_reason
        """
        if self.stage_type == 'Standard':
            self.update()
            if (self.mole_count) in self.stage_pts:
                if self.demo:
                    self.misses = 0
                    self.mole_count = 0
                    self.score = 0
                    self.stage = 1
                    self.pause_reason = 'demo'
                    self.demo = False
                    self.check_condition_change(demo=True)
                    self.pause()
                else:
                    self.sound_effect.play_stage_up()
                    self.pause_reason = 'stage'
                    self.stage += 1
                    self.pause()

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

    def get_distance(self, xy, frame_num):
        current_hole_x = self.hole_positions_centre[frame_num][0]
        current_hole_y = self.hole_positions_centre[frame_num][1]
        distance = ((xy[0] - current_hole_x)**2 +
                    (xy[1] - current_hole_y)**2)**0.5
        
        return distance

    def get_relative_loc(self, xy, frame_num):
        current_hole_x = self.hole_positions_centre[frame_num][0]
        current_hole_y = self.hole_positions_centre[frame_num][1]
        relative_loc = (xy[0] - current_hole_x, xy[1] - current_hole_y)
        return relative_loc

    def check_feedback(self):
        if self.feedback_count == self.feedback_limit:
            self.feedback_count = 0
            self.pause_reason = '2x2'
            self.pause()

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
        Updates the game's stage, score, misses, previous 2x2 rating on the gui
        """

        # # Update gui with player's stage
        # current_stage_string = "STAGE: " + str(self.stage) + "    "
        # self.write_text(current_stage_string, colour=(0, 0, 0), background=(255,255,255), size=22,
        #                 location_x=1050, location_y=100)
 
            # # Update gui with player's stage
        if self.demo:
            current_stage_string = "MOLES LEFT IN DEMO: " + str(self.demo_len- self.mole_count) + "    "
        else:
            current_stage_string = "MOLES LEFT: " + str(self.stages * self.stage_length - self.mole_count ) + "    "

        self.write_text(current_stage_string, colour=(0, 0, 0), background=(255,255,255), size=22,
                        location_x=1050, location_y=100)

        # Update gui with player's score
        current_score_string = "SCORE: " + str(int(self.score)) + "    "
        self.write_text(current_score_string, colour=(0, 0, 0), background=(255,255,255), size=22,
                   location_x=1050, location_y=250)
 

        # Update gui with player's misses
        current_misses_string = "MISSES: " + str(self.misses) + "    "
        self.write_text(current_misses_string, colour=(0, 0, 0), background=(255,255,255), size=22,
                   location_x=1050, location_y=400)
 
        
        last_score = "LAST SCORE: " + str(int(self.score_t0)) + "    "
        self.write_text(last_score, colour=(255, 0, 0), background=(255,255,255), size=22,
                   location_x=1050, location_y=550)

        # 2x2 rating persistence
        if self.last_rate:
            self.write_text('X',colour=(255, 0, 0), background=None, size=22,
                   location_x=self.last_rate[0], location_y=self.last_rate[1])

    def get_agent_mouse_pos(self, human=True):
        if human:
            pygame.mouse.get_pos()
        else:
            pass

    def mole_hit(self, ani_num, left, mole_is_down, interval, frame_num):
        ani_num = 3
        left = 14
        mole_is_down = False
        interval = 0
        self.score_t0 = self.scorer.get_score(self.distance,
                                              self.margin.drift_iter,
                                              self.skill_luck_rat)
        self.sound_effect.stop_pop()
        self.score += self.score_t0
        self.wam_logger.log_score(self.score_t0, self.score)
        self.mole_count += 1
        if self.FEEDBACK:
            self.sound_effect.play_hurt()
        return ani_num, left, mole_is_down, interval, frame_num
    
    def _displace_mouse(self):
        #xy_shift = [40,30,20,-20,-30,-40]
        #pyautogui.move(random.choice(xy_shift), random.choice(xy_shift))
        mouse_pos = pygame.mouse.get_pos()
        x_move = 405- mouse_pos[0] # middle of screen
        y_move = 280 - mouse_pos[1] # middle of screen
        pyautogui.move(x_move, y_move)


    def check_mouse_event(self, event, ani_num, left, mole_is_down,
                          interval, frame_num):
        """
        Checks whether a couse event has resulted in a mole hit
        """
        if (
            event.type == pygame.MOUSEBUTTONDOWN and
            event.button == self.LEFT_MOUSE_BUTTON
        ):
            self.distance = self.get_distance(pygame.mouse.get_pos(),
                                              frame_num)
            self.relative_loc = self.get_relative_loc(pygame.mouse.get_pos(),
                                                      frame_num)
            self.sound_effect.play_fire()
            self.result = self.hit_checker.check_mole_hit(
                                                    ani_num,
                                                    left,
                                                    self.distance,
                                                    self.margin.drift_iter)
            if self.result[0]:  # the hit feedback
                (ani_num,
                 left,
                 mole_is_down,
                 interval,
                 frame_num) = self.mole_hit(ani_num,
                                            left,
                                            mole_is_down,
                                            interval,
                                            frame_num)
                self._displace_mouse()                
                self.feedback_count += 1
                self.score_update_check()
                self.check_feedback()
                pygame.display.flip()
                self.skill_flip_counter += 1
                self.check_condition_change()
            else:
                self.misses += 1
                #self.mole_count += 1
                pygame.display.flip()

            self.wam_logger.log_hit_result(self.result,
                                           self.hole_positions[frame_num],
                                           self.distance, self.relative_loc)

            #self.score_update_check()
            self.set_player_stage()
        return ani_num, left, mole_is_down, interval, frame_num

    def check_condition_change(self, demo=False):
        print('check if donditions change', self.skill_flip_counter)
        if self.skill_flip_counter > self.skill_flip_floor:
            self.wam_logger.log_skill_change(self.skill_luck_rat)
            if np.random.binomial(1,0.2, 1)[0] == 1:
                self.skill_flip_counter = 0
                if self.skill_luck_rat == self.skill_ratio_master:
                    self.skill_luck_rat = 1-self.skill_ratio_master
                    print('luck!')
                else:
                    self.skill_luck_rat = self.skill_ratio_master
                    print('skill!')

        if demo:
            self.skill_luck_rat = random.choice([self.skill_ratio_master,1-self.skill_ratio_master])
            self.wam_logger.log_skill_change(self.skill_luck_rat)
            self.skill_flip_counter = 0

    def pop_mole(self, ani_num, mole_is_down, interval, frame_num):
        self.screen.blit(self.background, (0, 0))
        self.score_update_check()
        ani_num = 0
        mole_is_down = False
        interval = 0.5
        frame_num = random.randint(0, 8)
        self.wam_logger.log_mole_event(self.hole_positions[frame_num])
        return ani_num, mole_is_down, interval, frame_num

    def show_mole_frame(self, ani_num, frame_num, left):
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
        pic = self.mole[ani_num]
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(pic,
                         (self.hole_positions[frame_num][0] - left,
                          self.hole_positions[frame_num][1]))

    def animate_mole(self, ani_num, left, mole_is_down, interval,
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
        self.show_mole_frame(ani_num, frame_num, left)
        self.score_update_check()
        if mole_is_down is False:
            ani_num += 1
        else:
            ani_num -= 1
        if ani_num == 4:
            interval = self.post_whack_interval
        elif ani_num == 3:
            ani_num -= 1
            mole_is_down = True
            self.sound_effect.play_pop()
            interval = self.mole_pause_interval  # self.get_interval_by_stage(initial_interval)
        else:
            interval = self.animation_interval
        cycle_time = 0
        return (ani_num, left, mole_is_down,
                interval, frame_num, initial_interval,
                cycle_time, clock)

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
        ani_num = -1
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
                (ani_num,
                 left,
                 mole_is_down,
                 interval,
                 frame_num) = self.check_mouse_event(event,
                                                     ani_num,
                                                     left,
                                                     mole_is_down,
                                                     interval,
                                                     frame_num)

            # refreshes screen at the point of mole popping
            if ani_num > 5:       # 5
                self.screen.blit(self.background, (0, 0))
                self.score_update_check()
                ani_num = -1
                left = 0

            # pops the mole, if it's time
            if ani_num == -1:
                (ani_num,
                 mole_is_down,
                 interval,
                 frame_num) = self.pop_mole(ani_num,
                                            mole_is_down,
                                            interval,
                                            frame_num)

            # drops the mole, if it's time
            mil = clock.tick(self.FPS)
            sec = mil / 1000.0
            cycle_time += sec
            if cycle_time > interval:
                (ani_num,
                 left,
                 mole_is_down,
                 interval,
                 frame_num,
                 initial_interval,
                 cycle_time,
                 clock) = self.animate_mole(ani_num,
                                            left,
                                            mole_is_down,
                                            interval,
                                            frame_num,
                                            initial_interval,
                                            cycle_time,
                                            clock)
            # Update the display
            pygame.display.flip()
