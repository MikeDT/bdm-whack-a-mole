# -*- coding: utf-8 -*-
"""
main
====

Typical main.py functionality, initiates the pygame game and mixer,
starts the GameManager and spins up the game

Attributes:
    na

Todo:
    *na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole)

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


#consideratios

# confidence in hit vs precision of hit?
# confidence in score feels like it would make more sense for instant feedback (otherwise confidence is anchored to just one)

# confidence in target
# degree of luck

# hit but don't do properly?

#read the BdM papers

# if touch on playing screen and vice versa
# 