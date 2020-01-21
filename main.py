from game import GameManager
import pygame

# Initialize the game
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()

# Run the main loop
my_game = GameManager()
my_game.start()
# Exit the game if the main loop ends
pygame.quit()


#consideratios

# how to handle a miss because you're late?
# confidence in hit vs precision of hit?
# use same finger to make it harder?
# bigger board (fill screen)?
# tendency to chose 1 score for everything (maybe add a letter grade to shift people away, with only 2 scores asked)
# confidence in score feels like it would make more sense for instant feedback (otherwise confidence is anchored to just one)
# provide feedback on what you hit for 7

# confidence in target
# degree of luck

# hit but don't do properly?

# add the 2x2 on the right hand screen, confidence in score vs precision of hit pr some such
# scoring constant at bottom
# expand screen out perhaps (for final task)
#read the BdM papers