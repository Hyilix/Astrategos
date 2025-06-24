import pygame
import os 
import socket
import pyperclip

from button import Button
from Lobby_screen import lobby

DEBUG_DARK_MODE = True
White = (255,255,255)
B_color = (185, 186, 255)
Error_lifespan = 0

def connection_screen (WIN,WIDTH,HEIGHT,FPS,Role) :
    
    pygame.init()
    pygame.scrap.init()
    pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

    Rect_Draw = []
    Buttons = []
    Background = pygame.transform.scale(pygame.image.load('Assets/Menu_backg.jpg'),(WIDTH,HEIGHT))

    Font = pygame.font.Font("Assets/Fonts/zektonregular.otf", 30)
    ERROR_FONT = pygame.font.Font("Assets/Fonts/zektonregular.otf", 60)
    Error_text = ERROR_FONT.render("Ceva nu a mers bine",True,(255,0,0))
    text_rect = Error_text.get_rect()
    Error_text = (Error_text,text_rect)
    global Error_lifespan
    Error_lifespan = 0
    selected = -1
    #SE creaza butoanele care vor aparea pe ecran in functie de rolul selectat (host/client)
    if Role == "client" :
        Rect_Draw.append(((WIDTH-510)/2,(HEIGHT - 85*3-50*2)/2,510,85))
        Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*3-50*2)/2 + 5,500,75),B_color,None,**{"text": "Enter your name","font": Font})
        Buttons.append(Namebutton)

        Rect_Draw.append(((WIDTH-710)/2,(HEIGHT - 85*3-50*2)/2+85+50,710,85))
        Hostnamebutton =Button(((WIDTH-710)/2+5,(HEIGHT - 85*3-50*2)/2+85+50+5,700,75),B_color,None,**{"text": "Host name/IP adress","font": Font})
        Buttons.append(Hostnamebutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2 +160+50,(HEIGHT - 85*3-50*2)/2+85*2+50*2,410,85) )
        Portbutton =Button(((WIDTH-410 - 160*2 - 50*2)/2 +160+50+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,400,75),B_color,None,**{"text": "Server port","font": Font})
        Buttons.append(Portbutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2,(HEIGHT - 85*3-50*2)/2+85*2+50*2,160,85) )
        Connectbutton = Button(((WIDTH-410 - 160*2 - 50*2)/2 + 5,(HEIGHT - 85*3-50*2)/2+85*2+50*2 + 5,150,75),B_color,None,**{"text": "Connect","font": Font})
        Buttons.append(Connectbutton)

        Rect_Draw.append(((WIDTH-410 - 160*2 - 50*2)/2 + 160 + 410 + 50*2,(HEIGHT - 85*3-50*2)/2+85*2+50*2,160,85) )
        Backbutton = Button(((WIDTH-410 - 160*2 - 50*2)/2 + 160 + 410 + 50*2+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,150,75),B_color,None,**{"text": "Back","font": Font})
        Buttons.append(Backbutton)

        #seteaza unde va aparea eroarea cand nu se conecteaza
        Error_text[1].center = (WIDTH/2,(HEIGHT - 85*3-50*2)/2+85*3+50*2  + 150)

    else :
        Rect_Draw.append(((WIDTH-510)/2,(HEIGHT - 85*3-50*2)/2,510,85))
        Namebutton = Button(((WIDTH-510)/2 + 5,(HEIGHT - 85*3-50*2)/2 + 5,500,75),B_color,None,**{"text": "Enter your name","font": Font})
        Buttons.append(Namebutton)

        Rect_Draw.append(((WIDTH-710)/2,(HEIGHT - 85*3-50*2)/2+85+50,710,85))
        Hostnamebutton =Button(((WIDTH-710)/2+5,(HEIGHT - 85*3-50*2)/2+85+50+5,700,75),B_color,None,**{"text": "Host name/IP adress","font": Font})
        Buttons.append(Hostnamebutton)

        Rect_Draw.append(((WIDTH-260*2)/3,(HEIGHT - 85*3-50*2)/2+85*2+50*2,260,85))
        Hostbutton = Button(((WIDTH-260*2)/3+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,250,75),B_color,None,**{"text": "Host","font": Font})
        Buttons.append(Hostbutton)

        Rect_Draw.append(((WIDTH-260*2)*2/3+260,(HEIGHT - 85*3-50*2)/2+85*2+50*2,260,85))
        Backbutton = Button(((WIDTH-260*2)*2/3+260+5,(HEIGHT - 85*3-50*2)/2+85*2+50*2+5,250,75),B_color,None,**{"text": "Back","font": Font})
        Buttons.append(Backbutton)

        #seteaza unde va aparea eroarea cand nu se conecteaza
        Error_text[1].center = (WIDTH/2,(HEIGHT - 85*3-50*2)/2+85*3+50*2+5 + 150)

    def draw_window () :
        global Error_lifespan
        WIN.blit(Background,(0,0))
        for i in range(len(Rect_Draw)) :
            if selected == i :
                pygame.draw.rect(WIN,(0, 255, 0),Rect_Draw[i])
            else :
                pygame.draw.rect(WIN,(0,0,0),Rect_Draw[i])
        for button in Buttons :
            button.update(WIN)
        if Error_lifespan > 0 :
            Error_lifespan -= 1 
            WIN.blit(Error_text[0],Error_text[1])
        pygame.display.update()

    #informatile care pot fi colectate de la player 1.nume si daca e client 2.hostname 3.port 
    info = ["","",""]
    #limita de caractere pentru fiecare informatie
    char_limit = [10,25,5]
    
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
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER  :
                    selected = -1
                elif event.key == pygame.K_BACKSPACE  :
                    info[selected] = info[selected][:-1]
                    Buttons[selected].text = info[selected]
                    Buttons[selected].render_text()
                elif event.key == pygame.K_DELETE :
                    Buttons[selected].text = ""
                    Buttons[selected].render_text()
                elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL :
                    pyperclip.copy(info[selected])
                elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL :
                    clip_board = pyperclip.paste()
                    info[selected] += clip_board[:char_limit[selected]-len(info[selected])]
                    Buttons[selected].text = info[selected]
                    Buttons[selected].render_text()
                elif len(info[selected]) < char_limit[selected] and (event.mod & pygame.KMOD_CTRL)==0 :
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
                    run= False
                except :
                    #va afisa o eroare pentru 4 secunde
                    Error_lifespan = 240
                    next_stage = False
                if run == False :
                    lobby(WIN,WIDTH,HEIGHT,FPS,Role,info[0], client,int(info[2]))
            else :
                PORT = 65432
                HOSTNAME = info[1]

                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                verified = 0
                while PORT < 65434 :
                    #aceasta conditie ar trebui sa de-a fail doar daca portul este folosit, daca este folosit va mari nr. portului cu 1
                    try :
                        server.bind((HOSTNAME,PORT))
                        #se da enter la next stage
                        Continue = True
                        run = False
                        break
                    except :
                        if verified == 0:
                            try :
                                socket.gethostbyname(HOSTNAME)
                                verified = 1
                            except :
                                break
                        if verified == 1 :
                            PORT = PORT + 1 
                #Daca a dat eroare
                if run == True :
                    Error_lifespan = 240
                    next_stage = False
                else :

                    lobby(WIN,WIDTH,HEIGHT,FPS,Role,info[0],server,PORT)



