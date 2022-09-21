import pygame
import os 
import socket
import threading

from button import Button



def connection_screen (WIN,WIDTH,HEIGHT,FPS,Client) :
    
    pygame.init()
    pygame.scrap.init()
    pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

    Rect_Draw = []
    Buttons = []

    selected = None
    #SE creaza butoanele care vor aparea pe ecran in functie de rolul selectat (host/client)
    if Client :
        Rect_Draw.append(((WIDTH-510)/2,(HEIGHT - 85*3-50*2)/2,510,85))
        Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*3-50*2)/2 + 5,500,75),(224,224,224),None,**{"text": "Enter your name","font": pygame.font.Font(None, 50)})
        Buttons.append(Namebutton)

        Rect_Draw.append(((WIDTH-710)/2,(HEIGHT - 85*3-50*2)/2+85+50,710,85))
        Hostnamebutton =Button(((WIDTH-710)/2+5,(HEIGHT - 85*3-50*2)/2+85+50+5,700,75),(224,224,224),None,**{"text": "Host name/IP adress","font": pygame.font.Font(None, 50)})
        Buttons.append(Hostnamebutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2 +160+50,(HEIGHT - 85*3-50*2)/2+85*2+50*2,410,85) )
        Portbutton =Button(((WIDTH-410 - 160*2 - 50*2)/2 +160+50+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,400,75),(224,224,224),None,**{"text": "Server port","font": pygame.font.Font(None, 50)})
        Buttons.append(Portbutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2,(HEIGHT - 85*3-50*2)/2+85*2+50*2,160,85) )
        Connectbutton = Button(((WIDTH-410 - 160*2 - 50*2)/2 + 5,(HEIGHT - 85*3-50*2)/2+85*2+50*2 + 5,150,75),(224,224,224),None,**{"text": "Connect","font": pygame.font.Font(None, 50)})
        Buttons.append(Connectbutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2 + 160 + 410 + 50*2,(HEIGHT - 85*3-50*2)/2+85*2+50*2,160,85) )
        Backbutton = Button(((WIDTH-410 - 160*2 - 50*2)/2 + 160 + 410 + 50*2+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,150,75),(224,224,224),None,**{"text": "Back","font": pygame.font.Font(None, 50)})
        Buttons.append(Backbutton)
    else :
        Rect_Draw.append(((WIDTH-510)/2,(HEIGHT - 85*2-100)/2,510,85))
        Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*2-100)/2 + 5,500,75),(224,224,224),None,**{"text": "Enter your name","font": pygame.font.Font(None, 50)})
        Buttons.append(Namebutton)

        Rect_Draw.append(((WIDTH-260*2)/3,(HEIGHT - 85*2-100)/2+85+100,260,85))
        Hostbutton = Button(((WIDTH-260*2)/3+5,(HEIGHT - 85*2-100)/2+85+100+5,250,75),(224,224,224),None,**{"text": "Host","font": pygame.font.Font(None, 50)})
        Buttons.append(Hostbutton)

        Rect_Draw.append(((WIDTH-260*2)*2/3+260,(HEIGHT - 85*2-100)/2+85+100,260,85))
        Backbutton = Button(((WIDTH-260*2)*2/3+260+5,(HEIGHT - 85*2-100)/2+85+100+5,250,75),(224,224,224),None,**{"text": "Back","font": pygame.font.Font(None, 50)})
        Buttons.append(Backbutton)


    def draw_window () :
        WIN.fill((224,224,224))
        for i in Rect_Draw :
            pygame.draw.rect(WIN,(0,0,0),i)
        for button in Buttons :
            button.update(WIN)
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



