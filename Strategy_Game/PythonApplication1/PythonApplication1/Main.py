import Menu

import pygame
import pickle

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

print(HEIGHT/25)
#Aici se intra in meniu
Menu.menu_screen(WIN,WIDTH,HEIGHT,FPS)
