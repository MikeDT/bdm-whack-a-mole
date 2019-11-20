import pygame
import random
import numpy as np
from pygame import *
from sound import SoundEffect
from debug import Debugger
from logger import WamLogger


class GameManager:
    def __init__(self):
        # Define constants
        self.feedback = True
        self.SCREEN_WIDTH = 800
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
        self.stage_time_change = False
        # Initialize player's score, number of missed hits and stage
        self.score = 0
        self.misses = 0
        self.stage = 1
        self.stage_type = 'Standard'  # Standard or Attempts
        self.feedback_count = 0 
        self.feedback_limit = 2
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, 
                                               self.SCREEN_HEIGHT + 100))
        pygame.display.set_caption(self.GAME_TITLE)
        self.background = pygame.image.load("images/bg.png")
        # Font object for displaying text
        self.font_obj = pygame.font.SysFont("comicsansms", 20)
        # Initialize the mole's sprite sheet
        # 6 different states
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
        self.paused = False
        self.pause_list = [False, 'standard', 'rate_conf', 'rate_skill', 'rate_env']

    @staticmethod
    def text_objects(text, font):
        text_surface = font.render(text, True, (50, 50, 50))  # (0,0,0) = black
        return text_surface, text_surface.get_rect()

#    def write_message(self, message, loc_x, loc_y):
#        text = self.font_obj.render(message, True, (255, 255, 255))
#        text_pos = text.get_rect()
#        text_pos.centerx = loc_x
#        text_pos.centery = loc_y
#        self.screen.blit(text, text_pos)
#        pygame.display.update()

    def intro(self):
        while self.intro_complete is False:
            self.write_text('Welcome to the Brain Decision Modelling Lab' + 
                            'Whack-A-Mole Game!',
                            location_y= self.SCREEN_HEIGHT/2 - 80)
            self.write_text('Using the touch screen your task is to whack ' +
                            '(touch on screen) as many moles as possible',
                            location_y= self.SCREEN_HEIGHT / 2 - 40)
            self.write_text('You will score points for each mole you hit, ' +
                            'the more accurate the more points',
                            location_y= self.SCREEN_HEIGHT / 2)
            self.write_text("But sometimes the environment doesn't behave...",
                            location_y= self.SCREEN_HEIGHT / 2 + 40)
            self.write_text('... and you will score more or less than you ' 
                            'deserve',
                            location_y= self.SCREEN_HEIGHT / 2 + 80)
            self.write_text("To continue press 'c', to quit press 'q'",
                            location_y= self.SCREEN_HEIGHT / 2 + 120)
            self.write_text("If you need to pause while playing press 'p'",
                            location_y= self.SCREEN_HEIGHT / 2 + 180)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.wam_logger.log_end()
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.intro_complete = True
                    elif event.key == pygame.K_q:
                        self.wam_logger.log_end()
                        pygame.quit()
                        quit()

    def write_text(self, string, colour = (255, 255, 255),
                   location_x = None, location_y = None):
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
    
    def rate(self,action): 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.wam_logger.log_end()
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, 
                                 pygame.K_2, 
                                 pygame.K_3, 
                                 pygame.K_4, 
                                 pygame.K_5, 
                                 pygame.K_6, 
                                 pygame.K_7]:
                    self.wam_logger.log_it("<Event(7-Rate {'" +
                                           "': " + action[0] +
                                           str(event.key) + " })>")
                    self.paused = action[1]    
                elif event.key == pygame.K_q:
                    self.wam_logger.log_end()
                    pygame.quit()
                    quit()
        
    def pause(self):
        self.wam_logger.log_it("<Event(8-Pause {'reason': " + 
                               str(self.pause) + " })>")
        while self.paused != False:
            if self.paused == 'pause':
                self.write_text('Game Paused! Press "c" to continue, or "q" ' +
                                'to quit')
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.wam_logger.log_end()
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                            self.intro_complete = True
                        elif event.key == pygame.K_q:
                            self.wam_logger.log_end()
                            pygame.quit()
                            quit()

            elif self.paused == 'hit_conf':
                self.write_text('Please rate your confidence in a hit between 1 (lowest) and 7 (highest)',
                                location_y = self.SCREEN_HEIGHT/2 - 80)
                self.rate(('hit_conf','reward_conf'))
            elif self.paused == 'reward_conf':
                self.write_text('Please rate your confidence in a reward between 1 (lowest) and 7 (highest)',
                                location_y = self.SCREEN_HEIGHT/2 - 40)
                self.rate(('reward_conf','player_skill'))                 
            elif self.paused == 'player_skill': 
                self.write_text('Please rate your skill in the game between 1 (lowest) and 7 (highest)',
                                location_y = self.SCREEN_HEIGHT/2)
                self.rate(('player_skill',False))    

                
    # Calculate the player stage according to his current score &
    # the STAGE_SCORE_GAP constant
    def get_player_stage(self):
        if self.stage_type == 'Standard':
            new_stage = 1 + int(self.score / self.STAGE_SCORE_GAP)
            if new_stage != self.stage:
                # if player get a new stage play this sound
                self.soundEffect.play_stage_up()
                self.paused = 'hit_conf'
                self.pause(pause_reason = 'feedback')
            return 1 + int(self.score / self.STAGE_SCORE_GAP)
        elif self.stage_type == 'Time':
            if (self.misses + self.score) % 25 == 0:
                return 1 + self.stage
            else:
                return self.stage


    # Get the new duration between the time the mole pop up and down the holes
    # It's in inverse ratio to the player's current stage
    def get_interval_by_stage(self, initial_interval):
        if self.stage_time_change:
            new_interval = initial_interval - self.stage * 0.15
            if new_interval > 0:
                return new_interval
            else:
                return 0.05
        else:
            return 1.0

    # Check whether the mouse click hit the mole or not
    def is_mole_hit(self, mouse_position, current_hole_position):
        mouse_x = mouse_position[0]
        mouse_y = mouse_position[1]
        current_hole_x = current_hole_position[0]
        current_hole_y = current_hole_position[1]
        self.feedback_count +=1
        if self.feedback_count == self.feedback_limit:
            self.feedback_count = 0
            self.paused = 'hit_conf'
            self.pause()
            if ((mouse_x > current_hole_x) and
                    (mouse_x < current_hole_x + self.MOLE_WIDTH) and
                    (mouse_y > current_hole_y) and
                    (mouse_y < current_hole_y + self.MOLE_HEIGHT)):
                    if (np.random.binomial(1, 0.5, 1)[0]) > 0:
                        self.wam_logger.log_it("<Event(9.1-True Hit {'pos': (" +
                                               str(mouse_x) + "," + 
                                               str(mouse_y) +
                                               "), 'window': None})>")
                        return True
                    else:
                        self.wam_logger.log_it("<Event(9.2-Fake Miss {'pos': (" +
                                               str(mouse_x)
                                               + "," + str(mouse_y) + 
                                               "), 'window': None})>")
                        return False
            else:
                if (np.random.binomial(1, 0.5, 1)[0]) > 0:
                    self.wam_logger.log_it("<Event(9.3-Fake Hit {'pos': (" + 
                                           str(mouse_x) +
                                           "," + str(mouse_y) +
                                           "), 'window': None})>")
                    return True
                self.wam_logger.log_it("<Event(9.4-True Miss {'pos': (" +
                                       str(mouse_x) + "," + 
                                       str(mouse_y) + "), 'window': None})>")
                return False



    # Update the game states, re-calculate the player's score, misses, stage
    def update(self):
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

    # Start the game's main loop
    # Contains some logic for handling animations, mole hit events, etc..
    def start(self):
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

        for i in range(len(self.mole)):
            self.mole[i].set_colorkey((0, 0, 0))
            self.mole[i] = self.mole[i].convert_alpha()
        while loop:
            for event in pygame.event.get():
                self.wam_logger.log_it(event)
                if self.intro_complete is False:
                    self.intro()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = 'pause'
                        self.pause()
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()
                if event.type == pygame.QUIT:
                    loop = False
                if (event.type == pygame.MOUSEBUTTONDOWN and
                    event.button == self.LEFT_MOUSE_BUTTON):
                    self.soundEffect.play_fire()
                    if (self.is_mole_hit(pygame.mouse.get_pos(),
                                        self.hole_positions[frame_num]) and
                                        num > 0 and left == 0):
                        num = 3
                        left = 14
                        is_down = False
                        interval = 0
                        self.score += 1  
                        self.stage = self.get_player_stage()
                        # Stop popping sound effect
                        self.soundEffect.stop_pop()
                        # Play hurt sound
                        if self.feedback:
                           self.soundEffect.play_hurt()
                        self.update()
                    else:
                        self.misses += 1
                        self.update()

            if num > 5:
                self.screen.blit(self.background, (0, 0))
                self.update()
                num = -1
                left = 0

            if num == -1:
                self.screen.blit(self.background, (0, 0))
                self.update()
                num = 0
                is_down = False
                interval = 0.5
                frame_num = random.randint(0, 8)

            mil = clock.tick(self.FPS)
            sec = mil / 1000.0
            cycle_time += sec
            if cycle_time > interval:
                pic = self.mole[num]
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(pic,(self.hole_positions[frame_num][0] - left,
                                      self.hole_positions[frame_num][1]))
                self.update()
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
            # Update the display
            pygame.display.flip()
