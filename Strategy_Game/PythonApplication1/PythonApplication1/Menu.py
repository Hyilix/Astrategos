import pygame 
import os 
import Connection_Screen
import Editor

import Gameplay

from button import Button

pygame.init()

DEBUG_DARK_MODE = True

#Numele jocului
gamename = "Astrategos"
FontR = pygame.font.Font(None, 60)
Titlu = FontR.render(gamename,True,(0,0,0))
Titlu_rect = Titlu.get_rect()
#butoanele si dreptunghiurile lor
Rect_draw = []
Buttons = []


def menu_screen(WIN,WIDTH,HEIGHT,FPS) :

    #initializarea butoanelor si toate cele dupa marimile ecranului
    pygame.display.set_caption(gamename)
    Titlu_rect.center = (WIDTH/2,(HEIGHT-90*4-50*4-60)/2 + 40)

    Rect_draw.append(((WIDTH-260)/2-5,(HEIGHT-90*4-50*4-60)/2-5 + 60 + 50,260,90))
    Buton = Button(((WIDTH-260)/2,(HEIGHT-90*4-50*4-60)/2 + 60 +50,250,80),(255,255,255),None,**{"text": "Host","font": FontR})
    Buttons.append(Buton)

    Rect_draw.append(((WIDTH-260)/2-5,(HEIGHT-90*4-50*4-60)/2 + 60 +50*2 +90 - 5,260,90))
    Buton = Button(((WIDTH-260)/2,(HEIGHT-90*4-50*4-60)/2 +60 +50*2 + 90 ,250,80),(255,255,255),None,**{"text": "Join","font": FontR})
    Buttons.append(Buton)

    Rect_draw.append(((WIDTH-260)/2-5,(HEIGHT-90*4-50*4-60)/2 + 50*3 +60 + 90*2 -5,260,90))
    Buton = Button(((WIDTH-260)/2,(HEIGHT-90*4-50*4-60)/2 + 50*3 + 60  + 90*2,250,80),(255,255,255),None,**{"text": "Map Editor","font": FontR})
    Buttons.append(Buton)

    Rect_draw.append(((WIDTH-260)/2-5,(HEIGHT-90*4-50*4-60)/2 + 50*4 +60 + 90*3 -5,260,90))
    Buton = Button(((WIDTH-260)/2,(HEIGHT-90*4-50*4-60)/2 + 50*4 + 60  + 90*3,250,80),(255,255,255),None,**{"text": "QUIT","font": FontR})
    Buttons.append(Buton)


    def draw_window() :
        if DEBUG_DARK_MODE == True:
            WIN.fill((128,128,128))
        else: WIN.fill(255,255,255)
        WIN.blit(Titlu,Titlu_rect)
        for i in range(len(Rect_draw)) :
            pygame.draw.rect(WIN,(0,0,0),Rect_draw[i])
            Buttons[i].update(WIN)
        pygame.display.update()

    run = True
    clock = pygame.time.Clock()

    while run == True :
        clock.tick(FPS)

        draw_window()

        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1  :
                for i in range(len(Buttons)) :
                    if Buttons[i].on_click(event) :
                        if i == 0 :
                            Connection_Screen.connection_screen(WIN,WIDTH,HEIGHT,FPS,"host")
                        elif i == 1 :
                            Connection_Screen.connection_screen(WIN,WIDTH,HEIGHT,FPS,"client")
                        elif i == 2 :
                            Editor.editor(WIN,WIDTH,HEIGHT,FPS)
                        elif i == 3:
                            run = False
                            pygame.quit()
                            os._exit(0)

                        elif i == 4:
                            Gameplay.gameplay(WIN, WIDTH, HEIGHT, FPS, "Test_10x10")
