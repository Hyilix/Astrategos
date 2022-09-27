import pygame
import os 
import socket

from button import Button
from Lobby_screen import lobby

White = (255,255,255)

def connection_screen (WIN,WIDTH,HEIGHT,FPS,Role) :
    
    pygame.init()
    pygame.scrap.init()
    pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

    Rect_Draw = []
    Buttons = []

    selected = -1
    #SE creaza butoanele care vor aparea pe ecran in functie de rolul selectat (host/client)
    if Role == "client" :
        Rect_Draw.append(((WIDTH-510)/2,(HEIGHT - 85*3-50*2)/2,510,85))
        Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*3-50*2)/2 + 5,500,75),White,None,**{"text": "Enter your name","font": pygame.font.Font(None, 50)})
        Buttons.append(Namebutton)

        Rect_Draw.append(((WIDTH-710)/2,(HEIGHT - 85*3-50*2)/2+85+50,710,85))
        Hostnamebutton =Button(((WIDTH-710)/2+5,(HEIGHT - 85*3-50*2)/2+85+50+5,700,75),White,None,**{"text": "Host name/IP adress","font": pygame.font.Font(None, 50)})
        Buttons.append(Hostnamebutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2 +160+50,(HEIGHT - 85*3-50*2)/2+85*2+50*2,410,85) )
        Portbutton =Button(((WIDTH-410 - 160*2 - 50*2)/2 +160+50+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,400,75),White,None,**{"text": "Server port","font": pygame.font.Font(None, 50)})
        Buttons.append(Portbutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2,(HEIGHT - 85*3-50*2)/2+85*2+50*2,160,85) )
        Connectbutton = Button(((WIDTH-410 - 160*2 - 50*2)/2 + 5,(HEIGHT - 85*3-50*2)/2+85*2+50*2 + 5,150,75),White,None,**{"text": "Connect","font": pygame.font.Font(None, 50)})
        Buttons.append(Connectbutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2 + 160 + 410 + 50*2,(HEIGHT - 85*3-50*2)/2+85*2+50*2,160,85) )
        Backbutton = Button(((WIDTH-410 - 160*2 - 50*2)/2 + 160 + 410 + 50*2+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,150,75),White,None,**{"text": "Back","font": pygame.font.Font(None, 50)})
        Buttons.append(Backbutton)
    else :
        Rect_Draw.append(((WIDTH-510)/2,(HEIGHT - 85*3-50*2)/2,510,85))
        Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*3-50*2)/2 + 5,500,75),White,None,**{"text": "Enter your name","font": pygame.font.Font(None, 50)})
        Buttons.append(Namebutton)

        Rect_Draw.append(((WIDTH-710)/2,(HEIGHT - 85*3-50*2)/2+85+50,710,85))
        Hostnamebutton =Button(((WIDTH-710)/2+5,(HEIGHT - 85*3-50*2)/2+85+50+5,700,75),White,None,**{"text": "Host name/IP adress","font": pygame.font.Font(None, 50)})
        Buttons.append(Hostnamebutton)

        Rect_Draw.append(((WIDTH-260*2)/3,(HEIGHT - 85*3-50*2)/2+85*2+50*2,260,85))
        Hostbutton = Button(((WIDTH-260*2)/3+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,250,75),White,None,**{"text": "Host","font": pygame.font.Font(None, 50)})
        Buttons.append(Hostbutton)

        Rect_Draw.append(((WIDTH-260*2)*2/3+260,(HEIGHT - 85*3-50*2)/2+85*2+50*2,260,85))
        Backbutton = Button(((WIDTH-260*2)*2/3+260+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,250,75),White,None,**{"text": "Back","font": pygame.font.Font(None, 50)})
        Buttons.append(Backbutton)


    def draw_window () :
        WIN.fill(White)
        for i in Rect_Draw :
            pygame.draw.rect(WIN,(0,0,0),i)
        for button in Buttons :
            button.update(WIN)
        pygame.display.update()

    #informatile care pot fi colectate de la player 1.nume si daca e client 2.hostname 3.port 
    info = ["","",""]
    #limita de caractere pentru fiecare informatie
    char_limit = [15,25,5]
    
    clock = pygame.time.Clock()
    run = True
    next_stage = False
    while run :
        clock.tick(FPS)

        draw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1  :
                selected = -1
                if Role == "client" :
                    for i in range(len(Buttons)) :
                        if Buttons[i].on_click(event) :
                            if i <= 2  :
                                selected = i
                            elif i == 4 :
                                run = False
                                break
                            elif len(info[0]) > 0 and len(info[1]) > 0 and len(info[2]) == 5 :
                                next_stage = True
                else :
                    for i in range(len(Buttons)) :
                        if Buttons[i].on_click(event) :
                            if i <= 1 :
                                selected = i
                            elif i == 2 and len(info[0]) > 0 and len(info[1]) > 0 :
                                next_stage = True
                            else :
                                run = False 
                                break
            elif selected >= 0 and event.type == pygame.KEYDOWN and event.key != pygame.K_TAB :
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN :
                    selected = -1
                elif event.key == pygame.K_BACKSPACE  :
                    info[selected] = info[selected][:-1]
                    Buttons[selected].text = info[selected]
                    Buttons[selected].render_text()
                elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL :
                    info[selected] += ((pygame.scrap.get(pygame.SCRAP_TEXT)).decode()[:-1])[:char_limit[selected]-len(info[selected])]
                    Buttons[selected].text = info[selected]
                    Buttons[selected].render_text()
                elif len(info[selected]) < char_limit[selected] :
                    info[selected] += event.unicode
                    Buttons[selected].text = info[selected]
                    Buttons[selected].render_text()

        #Initializeaza actiunile necesare inaintarii la urmatorul stagiu
        if next_stage == True :
            if Role == "client" :

                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try : 
                    client.connect((info[1],int(info[2])))
                    #se da enter la next stage
                    lobby(WIN,WIDTH,HEIGHT,FPS,Role,client)
                    run= False
                except :
                    print("nu a mers dipshit")
                    #ceva eroare pe pygame window vedem...
            else :
                PORT = 65432
                HOSTNAME = info[1]

                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                while True :
                    #aceasta conditie ar trebui sa de-a fail doar daca portul este folosit, daca este folosit va mari nr. portului cu 1
                    try :
                        server.bind((HOSTNAME,PORT))
                        break
                    except :
                        PORT += 1 
                        print(PORT)
                #Aici se da enter la next stage
                lobby(WIN,WIDTH,HEIGHT,FPS,Role,info[0],server)
                run = False

