import pygame 
import os 
import Connection_Screen

from button import Button

pygame.init()

#Numele jocului
gamename = "NUMELE"
FontR = pygame.font.Font(None, 80)
Titlu = FontR.render(gamename,True,(0,0,0))
Titlu_rect = Titlu.get_rect()
#butoanele si dreptunghiurile lor
Rect_draw = []
Buttons = []



def menu_screen(WIN,WIDTH,HEIGHT,FPS) :

    #initializarea butoanelor si toate cele dupa marimile ecranului

    Titlu_rect.center = (WIDTH/2,(HEIGHT-110*3-50*3-80)/2 + 40)

    Rect_draw.append(((WIDTH-260)/2-5,(HEIGHT-110*3-50*3-80)/2-5 + 80 + 50,260,110))
    Buton = Button(((WIDTH-260)/2,(HEIGHT-110*3-50*3-80)/2 + 80 +50,250,100),(255,255,255),None,**{"text": "Host","font": FontR})
    Buttons.append(Buton)

    Rect_draw.append(((WIDTH-260)/2-5,(HEIGHT-110*3-50*3-80)/2 + 80 +50 +160 - 5,260,110))
    Buton = Button(((WIDTH-260)/2,(HEIGHT-110*3-50*3-80)/2 +50 +80 + 160 ,250,100),(255,255,255),None,**{"text": "Join","font": FontR})
    Buttons.append(Buton)

    Rect_draw.append(((WIDTH-260)/2-5,(HEIGHT-110*3-50*3-80)/2 + 50 +80 + 160*2 -5,260,110))
    Buton = Button(((WIDTH-260)/2,(HEIGHT-110*3-50*3-80)/2 + 50 + 80  + 160*2,250,100),(255,255,255),None,**{"text": "QUIT","font": FontR})
    Buttons.append(Buton)


    def draw_window() :
        WIN.fill((255,255,255))
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
                        elif i == 2:
                            run = False
                            pygame.quit()
                            os._exit(0)
