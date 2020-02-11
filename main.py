# -*- coding: utf-8 -*-
"""
main
====

Typical main.py functionality, initiates the pygame game and mixer,
starts the GameManager and spins up the game

Attributes:
    na

Todo:
    * binomial for hit (flex the params)
    * high low for both
    * use the the normal after for noise
    * luck and skill metadprime
    * gaussian noise
    * 2x2 on skilla nd luck (hgh  ghig, low low etc.)
    * explanations
    * shift th text
    * change the text
    * feedback where they hit
    * confidence l-r
    * luck high, skill btoom
    * hit or miss, how much credit to assign

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license
    
@author: miketaylor
"""

from game import GameManager
import pygame

if __name__ == "__main__":
    # Initialize the game
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.init()

    # Run the main loop
    my_game = GameManager()
    my_game.play_game()

    # Exit the game if the main loop ends
    pygame.quit()
