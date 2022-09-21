import pygame
import os 
import socket
import threading

from button import Button



def connection_screen (WIN,WIDTH,HEIGHT,FPS,Client) :
    
    pygame.init()
    pygame.scrap.init()
    pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

    selected = None

    Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*4-50*3)/2 + 5,500,75),(224,224,224),None,**{"text": "Enter your name","font": pygame.font.Font(None, 50)})
   
    def draw_window () :
        WIN.fill((224,224,224))
        #namebutton
        pygame.draw.rect(WIN,(0,0,0),((WIDTH-510)/2,(HEIGHT - 85*4-50*3)/2,510,85))
        Namebutton.update(WIN)
        pygame.display.update()

    

    name = ""
    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)

        draw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1  :
                selected = 0
                if Namebutton.on_click(event) :
                    selected = 1
            elif selected != 0 and event.type == pygame.KEYDOWN and event.key != pygame.K_TAB :
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN :
                    selected = 0
                elif event.key == pygame.K_BACKSPACE  :
                    name = name[:-1]
                    Namebutton.text = name
                    Namebutton.render_text()
                elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL :
                    print((pygame.scrap.get(pygame.SCRAP_TEXT)).decode())
                    name += (pygame.scrap.get(pygame.SCRAP_TEXT)).decode()[:-1]
                    Namebutton.text = name
                    Namebutton.render_text()
                elif len(name) < 15 :
                    name += event.unicode
                    Namebutton.text = name
                    Namebutton.render_text()



