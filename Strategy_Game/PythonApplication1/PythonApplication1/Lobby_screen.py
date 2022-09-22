import pygame 
import os 
import socket
import pickle
import threading


def lobby(WIN,WIDTH,HEIGHT,FPS,Role,name,Connection) :
    pygame.init()

    playeri = [["",0],["",0],["",0],["",0]]

    Cerc_draw = []

    y = HEIGHT/2
    diametru = (WIDTH - 50*3)/6
    for i in range(1,5) :
        x = diametru*i + diametru/2 + 50 *(i-1)
        Cerc_draw.append((x,y))

    def draw_window () :
        WIN.fill((255,255,255))
        for cerc in Cerc_draw :
            pygame.draw.circle(WIN,(225, 223, 240),cerc,diametru/2)
        pygame.display.update()
        


    if Role == "host" :
        playeri[0][0] = name

    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)
        
        draw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)