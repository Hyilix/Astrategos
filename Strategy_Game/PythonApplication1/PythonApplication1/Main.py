import Menu
import random
import pygame
import Settings

pygame.init()

try:    #If no audio output is detected, skip initializing mixer.
    pygame.mixer.init()
except:
    Settings.has_audio_loaded = False

random.seed()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

#Aici se intra in meniu
Menu.menu_screen(WIN,WIDTH,HEIGHT,FPS)
