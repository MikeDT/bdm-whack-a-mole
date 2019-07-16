import pygame

pygame.init()

display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('BDM Lab - Whack A Mole')

black = (0, 0, 0)
white = (255, 255, 255)

clock = pygame.time.Clock()
crashed = False
back_img = pygame.image.load('images/bg.png')


def background(x, y):
    gameDisplay.blit(back_img, (0, 0))

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

    gameDisplay.fill(white)
    background(0, 0)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()