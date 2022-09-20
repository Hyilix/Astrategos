import pygame
import os 
import socket

def connection_screen (WIN,WIDTH,HEIGHT,FPS) :
    
    pygame.init()
    
    def draw_window () :
        WIN.fill((224,224,224))
        #chenar nume 
        pygame.draw.rect(WIN,(0,0,0),((WIDTH-510)/2,(HEIGHT - 85*4-50*3)/2,510,85))
        pygame.draw.rect(WIN,(225,224,224),((WIDTH-510)/2 + 5,(HEIGHT - 85*4-50*3)/2 + 5,500,75))
        pygame.display.update()

    
    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)

        draw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)

