import pygame
import os 
import socket
import threading

from button import Button



def connection_screen (WIN,WIDTH,HEIGHT,FPS,Host) :
    
    pygame.init()
   
    def draw_window () :
        WIN.fill((224,224,224))
        #chenar nume 
        pygame.draw.rect(WIN,(0,0,0),((WIDTH-510)/2,(HEIGHT - 85*4-50*3)/2,510,85))
        Namebutton.update(WIN)
        pygame.display.update()

    

    name = ""
    selected = None
    Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*4-50*3)/2 + 5,500,75),(224,224,224),None,**{"text": "yeet" ,  "font": pygame.font.Font(None, 50)})

    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)

        draw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            Namebutton.check_event(event)


