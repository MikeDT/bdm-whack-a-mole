# -*- coding: utf-8 -*-
"""
sound module
============

This module contains the SoundEffect class for the pygame Whack a Mole game

Attributes:
    handled within the SoundEffect class

Todo:
    * sort out volumes

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: miketaylor
"""

import pygame


class SoundEffect:
    """
    Imports all the sound effects for the whack a mole game, with methods to
    play them during the game

    Attributes
    ----------
    main_track_loc: string (file location)
        the file location for the music soundtrack for the game
    fire_sound_loc: string (file location)
        the file location for the fire/strike sound for the game
    hurt_sound: string (file location)
        the file location for the hurt sound for the game
    pop_sound: string (file location)
        the file location for the mole popping sound for the game
    level_sound: string (file location)
        the file location for the level up sound for the game
    sound_volume: float
        the sound effects volume
    music_volume: float
        the music volume for the game

    Methods
    -------
    set_sounds(file_sound_loc generic locations )
        Imports the file sounds into the SoundEffect class
    play_****()
        plays the **** sound
    stop_****()
        stops the **** sound
    """
    def __init__(self):
        self.main_track_loc = "sounds/themesong.wav"
        self.fire_sound_loc = "sounds/fire.wav"
        self.pop_sound = "sounds/pop.wav"
        self.hurt_sound = "sounds/hurt.wav"
        self.level_sound = "sounds/point.wav"
        self.sound_volume = 1.0
        self.music_volume = 0.2
        self.import_sounds()
        self.play_music()

    def import_sounds(self):
        '''
        Sets the sounds for the game, loading from the sounds folder

        Parameters
        ----------
        self : self

        Raises
        ------
        OSError
            raised if the file imports failed

        Returns
        -------
        na
        '''
        try:
            self.main_track = pygame.mixer.music.load(self.main_track_loc)
            self.fire_sound = pygame.mixer.Sound(self.fire_sound_loc)
            self.pop_sound = pygame.mixer.Sound(self.pop_sound)
            self.hurt_sound = pygame.mixer.Sound(self.hurt_sound)
            self.level_sound = pygame.mixer.Sound(self.level_sound)
        except OSError:
            print('At least one of the sound files failed to load')
#        self.main_track.set_volume(self.music_volume)
#        self.fire_sound.set_volume(self.sound_volume)
#        self.pop_sound.set_volume(self.sound_volume)
#        self.hurt_sound.set_volume(self.sound_volume)
#        self.level_sound.set_volume(self.sound_volume)

    def play_music(self):
        '''
        Plays the theme tune for the game

        Parameters
        ----------
        self : self


        Returns
        -------
        na
            plays the music
        '''
        pygame.mixer.music.play(-1)

    def stop_music(self):
        '''
        Stops the theme tune for the game

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            stops the music
        '''
        pygame.mixer.music.play(-1)

    def play_fire(self):
        '''
        Plays the 'fire' sound when you attempt to hit a mole

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            plays the firesound
        '''
        self.fire_sound.play()

    def stop_fire(self):
        '''
        Stops the 'fire' sound when you attempt to hit a mole

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            Silence...
        '''
        self.fire_sound.stop()

    def play_pop(self):
        '''
        Plays the 'popping up' sound when a mole emerges from its hole

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            mole pop sound
        '''
        self.pop_sound.play()

    def stop_pop(self):
        '''
        Stops the 'mole popping' sound when a mole has completely popped

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            Silence...
        '''
        self.pop_sound.stop()

    def play_hurt(self):
        '''
        Plays the 'hurt' sound when a mole is succesfully hit

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            mole hit/hurt sound
        '''
        self.hurt_sound.play()

    def stop_hurt(self):
        '''
        Stops the 'hurt' sound when you have sucesfully hit a mole

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            Silence...
        '''
        self.hurt_sound.stop()

    def play_stage_up(self):
        '''
        Plays the 'stage up' sound when a new stage is reached

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            Stage level up sound
        '''
        self.level_sound.play()

    def stop_stage_up(self):
        '''
        Stops the 'stage up' sound when a stage refresh is complete

        Parameters
        ----------
        self : self

        Returns
        -------
        na
            Silence...
        '''
        self.level_sound.stop()
