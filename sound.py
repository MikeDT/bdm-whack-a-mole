from pygame import *
import pygame


class SoundEffect:
    def __init__(self):
        self.mainTrack = pygame.mixer.music.load("sounds/themesong.wav")
        self.fireSound = pygame.mixer.Sound("sounds/fire.wav")
        self.fireSound.set_volume(1.0)
        self.popSound = pygame.mixer.Sound("sounds/pop.wav")
        self.hurtSound = pygame.mixer.Sound("sounds/hurt.wav")
        self.levelSound = pygame.mixer.Sound("sounds/point.wav")
        pygame.mixer.music.play(-1)

    def play_fire(self):
        self.fireSound.play()

    def stop_fire(self):
        self.fireSound.sop()

    def play_pop(self):
        self.popSound.play()

    def stop_pop(self):
        self.popSound.stop()

    def play_hurt(self):
        self.hurtSound.play()

    def stop_hurt(self):
        self.hurtSound.stop()

    def play_level_up(self):
        self.levelSound.play()

    def stop_level_up(self):
        self.levelSound.stop()
