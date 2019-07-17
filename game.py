import pygame
import random
import numpy as np
from pygame import *
from sound import SoundEffect
from debug import Debugger

class GameManager:
    def __init__(self):
        # Define constants
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        self.MOLE_WIDTH = 90
        self.MOLE_HEIGHT = 81
        self.FONT_SIZE = 18
        self.FONT_TOP_MARGIN = 26
        self.LEVEL_SCORE_GAP = 4
        self.LEFT_MOUSE_BUTTON = 1
        self.GAME_TITLE = "Whack A Mole - Game Programming - Assignment 1"
        # Initialize player's score, number of missed hits and level
        self.score = 0
        self.misses = 0
        self.level = 1
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(self.GAME_TITLE)
        self.background = pygame.image.load("images/bg.png")
        # Font object for displaying text
        self.font_obj = pygame.font.Font('./fonts/GROBOLD.ttf', self.FONT_SIZE)
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
        self.pause = False

    def text_objects(self, text, font):
        textSurface = font.render(text, True, (50,50,50))# (0,0,0) =  black
        return textSurface, textSurface.get_rect()

    def intro(self):
        while self.intro_complete:
            pause_string = "Welcome! Press 'c' to continue, or 'q' to quit"
            pause_text = self.font_obj.render(pause_string, True, (255, 255, 255))
            pause_text_pos = pause_text.get_rect()
            pause_text_pos.centerx = self.background.get_rect().centerx
            pause_text_pos.centery = self.SCREEN_HEIGHT/2
            self.screen.blit(pause_text, pause_text_pos)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.intro_complete = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()

    def write_message(self, message, loc_x, loc_y):
        text = self.font_obj.render(message, True, (255, 255, 255))
        text_pos = text.get_rect()
        text_pos.centerx = loc_x
        text_pos.centery = loc_y
        self.screen.blit(text, text_pos)
        pygame.display.update()

    def intro(self):
        while self.intro_complete:
            self.write_message("Welcome to the Brain Decision Modelling Lab Whack-A-Mole Game!",
                               self.background.get_rect().centerx,
                               self.SCREEN_HEIGHT/2-80 )
            self.write_message("Using the touch screen your task is to whack (touch) as many moles as possible",
                               self.background.get_rect().centerx,
                               self.SCREEN_HEIGHT/2 - 40)
            self.write_message("You will score points for each mole you hit, the more accurate the more points",
                               self.background.get_rect().centerx,
                               self.SCREEN_HEIGHT/2)
            self.write_message("But sometimes the environment doesn't behave...",
                               self.background.get_rect().centerx,
                               self.SCREEN_HEIGHT/2+ 40)
            self.write_message("... and you will score more or less than you deserve",
                               self.background.get_rect().centerx,
                               self.SCREEN_HEIGHT/2+ 80)
            self.write_message("To continue press 'c', to quit press 'q'",
                               self.background.get_rect().centerx,
                               self.SCREEN_HEIGHT/2 + 140)
            self.write_message("If you need to pause while playing press 'p'",
                               self.background.get_rect().centerx,
                               self.SCREEN_HEIGHT/2 + 220)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.intro_complete = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()

    def paused(self):
        while self.pause:
            pause_string = "Game Paused! Press 'c' to continue, or 'q' to quit"
            pause_text = self.font_obj.render(pause_string, True, (255, 255, 255))
            pause_text_pos = pause_text.get_rect()
            pause_text_pos.centerx = self.background.get_rect().centerx
            pause_text_pos.centery = self.SCREEN_HEIGHT/2
            self.screen.blit(pause_text, pause_text_pos)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.pause = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()

    # Calculate the player level according to his current score & the LEVEL_SCORE_GAP constant
    def get_player_level(self):
        newLevel = 1 + int(self.score / self.LEVEL_SCORE_GAP)
        if newLevel != self.level:
            # if player get a new level play this sound
            self.soundEffect.playLevelUp()
        return 1 + int(self.score / self.LEVEL_SCORE_GAP)

    # Get the new duration between the time the mole pop up and down the holes
    # It's in inverse ratio to the player's current level
    def get_interval_by_level(self, initial_interval):
        new_interval = initial_interval - self.level * 0.15
        if new_interval > 0:
            return new_interval
        else:
            return 0.05

    # Check whether the mouse click hit the mole or not
    def is_mole_hit(self, mouse_position, current_hole_position):
        mouse_x = mouse_position[0]
        mouse_y = mouse_position[1]
        current_hole_x = current_hole_position[0]
        current_hole_y = current_hole_position[1]
        if (mouse_x > current_hole_x) and\
                (mouse_x < current_hole_x + self.MOLE_WIDTH) and\
                (mouse_y > current_hole_y) and\
                (mouse_y < current_hole_y + self.MOLE_HEIGHT and \
                (np.random.binomial(1, 0.5, 1)[0])>0):
            return True
        else:
            return False

    # Update the game states, re-calculate the player's score, misses, level
    def update(self):
        # Update the player's score
        current_score_string = "SCORE: " + str(self.score)
        score_text = self.font_obj.render(current_score_string, True, (255, 255, 255))
        score_text_pos = score_text.get_rect()
        score_text_pos.centerx = self.background.get_rect().centerx
        score_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(score_text, score_text_pos)
        # Update the player's misses
        current_misses_string = "MISSES: " + str(self.misses)
        misses_text = self.font_obj.render(current_misses_string, True, (255, 255, 255))
        misses_text_pos = misses_text.get_rect()
        misses_text_pos.centerx = self.SCREEN_WIDTH / 5 * 4
        misses_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(misses_text, misses_text_pos)
        # Update the player's level
        current_level_string = "LEVEL: " + str(self.level)
        level_text = self.font_obj.render(current_level_string, True, (255, 255, 255))
        level_text_pos = level_text.get_rect()
        level_text_pos.centerx = self.SCREEN_WIDTH / 5 * 1
        level_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(level_text, level_text_pos)

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
        self.intro_complete = True
        while loop:
            for event in pygame.event.get():
                if self.intro_complete == True:
                    self.intro()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.pause = True
                        self.paused()
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == MOUSEBUTTONDOWN and event.button == self.LEFT_MOUSE_BUTTON:
                    self.soundEffect.playFire()
                    if self.is_mole_hit(mouse.get_pos(), self.hole_positions[frame_num]) and num > 0 and left == 0:
                        num = 3
                        left = 14
                        is_down = False
                        interval = 0
                        self.score += 1  # Increase player's score
                        self.level = self.get_player_level()  # Calculate player's level
                        # Stop popping sound effect
                        self.soundEffect.stopPop()
                        # Play hurt sound
                        self.soundEffect.playHurt()
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
                self.screen.blit(pic, (self.hole_positions[frame_num][0] - left, self.hole_positions[frame_num][1]))
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
                    self.soundEffect.playPop()
                    interval = self.get_interval_by_level(initial_interval)  # get the newly decreased interval value
                else:
                    interval = 0.1
                cycle_time = 0
            # Update the display
            pygame.display.flip()