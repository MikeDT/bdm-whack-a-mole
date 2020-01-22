import pygame
import random
import numpy as np
from sound import SoundEffect
from debug import Debugger
from logger import WamLogger
from scorer import Scorer


class GameManager:
    def __init__(self):

        # Define constants
        self.feedback = True
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
        self.wam_logger = WamLogger()
        self.intro_complete = False
        self.stage_time_change = True
        self.demo_len = 5

        # Initialize player's score, number of missed hits and stage data
        self.score = 0
        self.misses = 0
        self.stage = 'Demo'
        self.stage_type = 'Standard'  # Standard or Attempts
        self.feedback_count = 0
        self.feedback_limit = 1
        self.update_count = 0
        self.update_delay = 0
        self.stage_length = 10
        self.mole_count = 0
        self.stages = range(self.demo_len,
                            100 + self.demo_len,
                            self.stage_length)
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,
                                               self.SCREEN_HEIGHT + 100))
        pygame.display.set_caption(self.GAME_TITLE)
        if self.SCREEN_WIDTH == 1600:
            self.background = pygame.image.load("images/bg 1600x1300.png")
        else:
            self.background = pygame.image.load("images/bg_2x2_1424x700.png")

        # Font object for displaying text
        self.font_obj = pygame.font.SysFont("comicsansms", 20)

        # Initialize the mole's sprite sheet (6 different states)
        sprite_sheet = pygame.image.load("images/mole.png")
        self.mole = []
        self.mole.append(sprite_sheet.subsurface(169, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(309, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(449, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(575, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(717, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(853, 0, 116, 81))

        # Positions of the holes in background
        self.hole_positions = []
        self.hole_positions.append((381, 295))
        self.hole_positions.append((119, 366))
        self.hole_positions.append((179, 169))
        self.hole_positions.append((404, 479))
        self.hole_positions.append((636, 366))
        self.hole_positions.append((658, 232))
        self.hole_positions.append((464, 119))
        self.hole_positions.append((95, 43))
        self.hole_positions.append((603, 11))

        # Init debugger
        self.debugger = Debugger("debug")

        # Sound effects
        self.soundEffect = SoundEffect()
        self.pause_reason = False
        self.pause_list = [False, 'standard', 'hit_conf',
                           'rate_skill', 'rate_env', 'stage']
        self.demo = True
        self.event_key_dict = {'49': '1', '50': '2', '51': '3', '52': '4',
                               '53': '5', '54': '6', '55': '7', '56': '8',
                               '57': '9'}

        # Initialise the score adjustment functions and data
        self.scorer = Scorer(self.hole_positions)
        self.margin = 10
        self.score_type = 'lin_dist_skill'  # 'boolean' or 'nonlin_dist_skill'
        self.adj_type = 'random_walk_neg' # random_walk_neg, random_walk_pos, static, designed
        self.hit_type = 'Margin'

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
            self.write_text('Welcome to the Brain Decision Modelling Lab' +
                            'Whack-A-Mole Game!',
                            location_y=self.SCREEN_HEIGHT/2 - 80)
            self.write_text('Using the touch screen your task is to whack ' +
                            '(touch on screen) as many moles as possible',
                            location_y=self.SCREEN_HEIGHT / 2 - 40)
            self.write_text('You will score between 0 and 10 points, ' +
                            'the more accurate the hit the more points',
                            location_y=self.SCREEN_HEIGHT / 2)
            self.write_text("But sometimes the environment doesn't behave...",
                            location_y=self.SCREEN_HEIGHT / 2 + 40)
            self.write_text('... and you will score more or less than you' +
                            '"deserve"',
                            location_y=self.SCREEN_HEIGHT / 2 + 80)
            self.write_text("To continue press 'c', to quit press 'ctrl q'",
                            location_y=self.SCREEN_HEIGHT / 2 + 120)
            self.write_text("If you need to pause while playing press 'p'",
                            location_y=self.SCREEN_HEIGHT / 2 + 180)

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
                    self.demo = False
                    self.pause_reason = False
                elif self.current_event.key == pygame.K_p:
                    self.pause_reason = 'pause'
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
                    self.wam_logger.log_it("<Event(7-Rate {'" +
                                           action[0] + "': " +
                                           event_act + " })>")
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
        """
        HAndles pause events, needs to be abstracted into more functions
        """
        self.wam_logger.log_it("<Event(8-Pause {'reason': " +
                               str(self.pause_reason) + " })>")
        while self.pause_reason:
            if self.pause_reason in ['pause', 'stage', 'demo']:
                if self.pause_reason == 'stage':
                    self.update()
                    self.write_text('Stage Complete! Press "c" to continue, ' +
                                    'or "ctrl q" to quit',
                                    location_y=self.SCREEN_HEIGHT/2 + 40)
                    self.check_key_event()
                elif self.pause_reason == 'paused':
                    self.write_text('Game Paused! Press "c" to continue, or ' +
                                    '"ctrl q" to quit')
                    self.check_key_event()
                else:
                    self.write_text('Demo Complete! Press "c" to start the ' +
                                    'real game, or "ctrl q" to quit',
                                    location_y=self.SCREEN_HEIGHT/2 + 40)
                    self.scorer.reset()
                    self.check_key_event()

            elif self.pause_reason == 'hit_conf':
                self.write_text('Please rate your confidence in making a hit ' +
                                'between 1 (lowest) and 7 (highest)',
                                location_y=self.SCREEN_HEIGHT/2 - 80)
                self.check_events_rate(('hit_conf', 'reward_conf'))
            elif self.pause_reason == 'reward_conf':
                self.write_text('Please rate your confidence in a reward ' +
                                'between 1 (lowest) and 7 (highest)',
                                location_y=self.SCREEN_HEIGHT/2 - 40)
                self.check_events_rate(('reward_conf', 'player_skill'))
            elif self.pause_reason == 'player_skill':
                self.write_text('Please rate your skill in the game between ' +
                                '1 (lowest) and 7 (highest)',
                                location_y=self.SCREEN_HEIGHT/2)
                self.check_events_rate(('player_skill', False))

    def set_player_stage(self):
        """
        Sets the game stage based upon the stage type and pause_reason
        """
        if self.stage_type == 'Standard':
            if (self.mole_count) in self.stages:
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
  
    def check_mole_hit(self, mouse_position, current_hole_position):
        """
        Checks whether a mole was hit, able to call a variety of methods
        dependent on the type of mole hit that is modelled for in the game at
        a given point in time (e.g. standard, with additional margin, binomial
        etc.
        """
        self.mouse_x = mouse_position[0]
        self.mouse_y = mouse_position[1]
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
        self.log_hit_result()
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

    def log_hit_result(self):
        """
        Logs the hit result based on the current mole hit criteria
        """
        log_string = ("{'pos': (" +
                      str(self.mouse_x) + "," +
                      str(self.mouse_y) + ")," +
                      "'distance: " + str(self.distance) + "," +
                      "'relative_loc: " + str(self.relative_loc) + "," +
                      "'window': None})>")
        if self.result == (True, True):
            self.wam_logger.log_it("<Event(9.1-TrueHit " + log_string)
        elif self.result == (False, True):
            self.wam_logger.log_it("<Event(9.2-FakeMiss " + log_string)
        elif self.result == (True, False):
            self.wam_logger.log_it("<Event(9.3-FakeHit " + log_string)
        else:
            self.wam_logger.log_it("<Event(9.4-TrueMiss " + log_string)

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
        Updates the game's states recalcualtes the player's score, misses,
        stage etc.
        """
        # Update the player's score
        current_score_string = "SCORE: " + str(self.score)
        score_text = self.font_obj.render(current_score_string,
                                          True, (1, 1, 1))
        score_text_pos = score_text.get_rect()
        score_text_pos.centerx = self.background.get_rect().centerx
        score_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(score_text, score_text_pos)
        # Update the player's misses
        current_misses_string = "MISSES: " + str(self.misses)
        misses_text = self.font_obj.render(current_misses_string,
                                           True, (1, 1, 1))
        misses_text_pos = misses_text.get_rect()
        misses_text_pos.centerx = self.SCREEN_WIDTH / 5 * 4
        misses_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(misses_text, misses_text_pos)
        # Update the player's stage
        current_stage_string = "STAGE: " + str(self.stage)
        stage_text = self.font_obj.render(current_stage_string,
                                          True, (1, 1, 1))
        stage_text_pos = stage_text.get_rect()
        stage_text_pos.centerx = self.SCREEN_WIDTH / 5 * 1
        stage_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(stage_text, stage_text_pos)
            
    def check_mouse_event(self, event, num, left, is_down, interval, frame_num):
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
                is_down = False
                interval = 0
                mouse_pos = pygame.mouse.get_pos()
                score_inc = self.scorer.get_score(mouse_pos,
                                                  frame_num,
                                                  self.score_type,
                                                  self.adj_type)
                self.score += score_inc
                score_str = ("score_inc: " + str(score_inc) + "," +
                               "score: " + str(self.score) + "})>")
                self.wam_logger.log_it("<Event(11-Score {" + score_str)

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

        return num, left, is_down, interval, frame_num
    
    def pop_mole(self, num, is_down, interval, frame_num):
        self.screen.blit(self.background, (0, 0))
        self.score_update_check()
        num = 0
        is_down = False
        #interval = 0.5
        frame_num = random.randint(0, 8)
        log_string = (
                      "{'loc': (" +
                      str(self.hole_positions[frame_num][0]) + "," +
                      str(self.hole_positions[frame_num][1]) + ")})>"
                      )
        self.wam_logger.log_it("<Event(10-MoleUp) " + log_string)
        return num, is_down, interval, frame_num

    def drop_mole(self, num, left, is_down, interval, frame_num, initial_interval, cycle_time, clock):
        pic = self.mole[num]
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(pic,
                         (self.hole_positions[frame_num][0] - left,
                          self.hole_positions[frame_num][1]))
        self.score_update_check()
        if is_down is False:
            num += 1
        else:
            num -= 1
        if num == 4:
            interval = 0.3
        elif num == 3:
            num -= 1
            is_down = True
            self.soundEffect.play_pop()
            interval = self.get_interval_by_stage(initial_interval)
        else:
            interval = 0.1
        cycle_time = 0
        return num, left, is_down, interval, frame_num, initial_interval, cycle_time, clock

    def create_moles(self):
        """
        Creates a set of moles
        """
        for i in range(len(self.mole)):
            self.mole[i].set_colorkey((0, 0, 0))
            self.mole[i] = self.mole[i].convert_alpha()

    # Start the game's main loop
    # Contains some logic for handling animations, mole hit events, etc..
    def play_game(self):
        """
        Play the whack a mole game
        """
        cycle_time = 0
        num = -1
        loop = True
        is_down = False
        interval = 0.1
        initial_interval = 1
        frame_num = 0
        left = 0
        # Time control variables
        clock = pygame.time.Clock()
        self.create_moles()
        while loop:

            # log game events, and check whether key or mouse
            # events have occurred (and react appropriately)
            for event in pygame.event.get():
                self.wam_logger.log_it(event)
                if self.intro_complete is False:
                    self.intro()
                if event.type == pygame.QUIT:
                    loop = False
                self.check_key_event(event)
                num, left, is_down, interval, frame_num = self.check_mouse_event(event, num, left, is_down, interval, frame_num)

            # refreshes screen at the point of mole popping
            if num > 5:
                self.screen.blit(self.background, (0, 0))
                self.score_update_check()
                num = -1
                left = 0

            # pops the mole, if it's time
            if num == -1:
                num, is_down, interval, frame_num = self.pop_mole(num, is_down, interval, frame_num)

            # drops the mole, if it's time
            mil = clock.tick(self.FPS)
            sec = mil / 1000.0
            cycle_time += sec
            if cycle_time > interval:
                num, left, is_down, interval, frame_num, initial_interval, cycle_time, clock = self.drop_mole(num, left, is_down, interval, frame_num, initial_interval, cycle_time, clock)

            # Update the display
            pygame.display.flip()
