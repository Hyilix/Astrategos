import pygame 
import os 
import socket
import pickle
import threading
import math
import time

from Map_select_screen import Map_select

DEBUG_DARK_MODE = True

pygame.init()
#Culori
White = (255,255,255)
Gri = (225, 223, 240)
Red = (255, 0, 0)
Blue =(0, 0, 255)
Green =(0, 150, 0)
Yellow = (255,255,0)
Orange = (255, 150, 0)
Purple = (150, 0, 255)
Pink = (255, 0, 255)
Cyan = (60, 160, 255)
Light_Green = (0, 255, 0)
Player_Colors = [White,Blue,Red,Green,Yellow,Orange,Purple,Pink,Cyan]
Selected_Colors = [0,0,0,0,0,0,0,0]

identifier_color = (255, 181, 0)

#variabile globale
nr_clients = 0
cod_client = 0

Pozitie = None
#Structura unui player 0 = numele , 1 = nr_culorii, 2 = Daca e ready sau nu
playeri = []
Text_draw = []

HEADERSIZE = 10
SPACE = "          "

Next_stage_cooldown = 3*60

Confirmation = False
Confirmatii = 0

Font = pygame.font.Font(None, 40)
FontR = pygame.font.Font(None, 80)
Exit_text = Font.render("Press Esc twice in a row to exit", True, (0,0,0))

sufixe = [".JR",".III",".IV"]

run = True

def lobby(WIN,WIDTH,HEIGHT,FPS,Role,name,Connection , Port = None) :

    global playeri
    global Selected_Colors
    global Text_draw
    playeri = []
    Cerc_draw = []
    Text_draw = []
    Selected_Colors = [0,0,0,0,0,0,0,0]

    exit_cooldown = -1

    Exit_rect = Exit_text.get_rect()
    Exit_rect.center = (WIDTH/2, HEIGHT -HEIGHT/25 - 30)

    global run 

    #coordonatele pentru cercuri
    y = HEIGHT/2
    diametru = (WIDTH - 50*3)/6
    for i in range(1,5) :
        x = diametru*i + diametru/2 + 50 *(i-1)
        Cerc_draw.append((x,y))
    #dreptunchiul de costumizare 
    Costumization_rect = ((WIDTH-101*8-25*9)/2,HEIGHT/2 - diametru/2 - 75 - 151,101*8+25*9,151)

    #Threadul care se ocupa cu primirea informatiilor de la server
    def reciev_thread_from_server(server,new) :
        global playeri
        global Pozitie
        global Selected_Colors
        global Confirmation
        global run
        global Text_draw
        if new :
            #Clientul isi trimite numele la server
            data_send = ((SPACE + str(len(name)))[-HEADERSIZE:] + name)
            server.send(bytes(data_send,"utf-8"))
            #serveru va trimite la client toata lumea din vector
            header = server.recv(10)
            header = header.decode("utf-8")
            data_recv = server.recv(int(header))
            playeri = pickle.loads(data_recv)
            #serveru va trimite pozitia clientului printre playeri

            header = server.recv(10)
            header = header.decode("utf-8")
            data_recv = server.recv(int(header))
            Pozitie = pickle.loads(data_recv)

        for i in range(len(playeri)) :
            #Formateaza si pregateste pentru afisare toate numele playerilor
            if i != Pozitie :
                text = Font.render(playeri[i][0], True, (0,0,0))
            else :
                text = Font.render(playeri[i][0], True, identifier_color)
            text_rect = text.get_rect()
            text_rect.center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
            Text_draw.append((text,text_rect))
            #vede daca au o culoare selectata
            if playeri[i][1] != 0 :
                Selected_Colors[playeri[i][1]-1] = 1

        #The recieve loop
        try :
            while True :
                header = server.recv(10)
                header = header.decode("utf-8")

                if len(header) != 0 :
                    data_recv = server.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "enter_next_stage" :
                        data_send = pickle.dumps(("enter_next_stage",None))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        server.send(data_send)
                        Confirmation = True
                        break
                    elif data_recv[0] == "I_died...Fuck_off" or data_recv[0] == "Fuck_off":
                        server.close()
                        run = False
                        break
                    else :
                        Changes_from_server.append(data_recv)
                else :
                    server.close()
                    run = False
                    break
        except :
            server.close()
            run = False

    #Threadul care se ocupa cu primirea informatiilor spre un client
    def reciev_thread_from_client(client,cod,new) :
        global playeri
        global Selected_Colors 
        global Confirmatii
        global Text_draw
        if new :
            #Primeste numele clientului
            header = client.recv(10)
            header = header.decode("utf-8")
            data_recv = client.recv(int(header))
            data_recv = data_recv.decode("utf-8")
            #se verifica  daca numele lui este deja luat
            samename = -1
            for i in range(len(playeri)) :
                if playeri[i][0] == data_recv or playeri[i][0] == data_recv + ".Jr" or playeri[i][0] == data_recv +".III" or playeri[i][0] == data_recv + ".IV" :
                    samename += 1
            if samename >= 0 :
                data_recv = data_recv + sufixe[samename]
            #se decide ce culoare ii dam
            for i in range(len(Selected_Colors)) :
                if Selected_Colors[i]==0 :
                    p_color = i
                    Selected_Colors[i] = 1
                    break
            #Formateaza numele si il pregateste de afisare
            text = Font.render(data_recv, True, (0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (diametru*(Coduri_pozitie_client[cod]+1) + 50*Coduri_pozitie_client[cod] + diametru/2,HEIGHT/2 - diametru/2-30)
            Text_draw.append((text,text_rect))
            #il pune in vectorul de playeri
            playeri.append((data_recv,p_color+1,0))
            P = len(playeri)-1
            Transmit_to_all.append((("newplayer",playeri[len(playeri)-1]),cod))
            #Trimite tot vectorul de playeri clientului
            data_send = pickle.dumps(playeri)
            data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
            client.send(data_send)
            print(P)
            data_send = pickle.dumps(P)
            data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
            client.send(data_send)

        #The recieve loop
        try :
            while True :
                header = client.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "want_change_color" :
                        if Selected_Colors[data_recv[1]] == 0 :
                            Selected_Colors[data_recv[1]] = 1
                            if playeri[Coduri_pozitie_client[cod]+1][1] != 0 :
                                    Selected_Colors[playeri[Coduri_pozitie_client[cod]+1][1]-1] = 0
                            playeri[Coduri_pozitie_client[cod]+1] = (playeri[Coduri_pozitie_client[cod]+1][0],data_recv[1]+1,playeri[Coduri_pozitie_client[cod]+1][2])
                            Transmit_to_all.append((("player_changed_color",Coduri_pozitie_client[cod]+1,data_recv[1]),None))
                    
                    elif data_recv[0] == "ready_state_change" :
                        if playeri[data_recv[1]][2] == 0 :
                            playeri[data_recv[1]] = (playeri[data_recv[1]][0],playeri[data_recv[1]][1],1)
                        else :
                            playeri[data_recv[1]] = (playeri[data_recv[1]][0],playeri[data_recv[1]][1],0)
                        Transmit_to_all.append((data_recv,cod))
                    elif data_recv[0] == "enter_next_stage" :
                        Confirmatii += 1 
                        break
                else :
                    client.close()
                    Killed_Clients.append(cod)
                    break
        except :
            client.close()
            Killed_Clients.append(cod)


    #Threadul care va asculta pentru si va acepta clienti
    def host_listen_thread() :
        global Listening
        global nr_clients
        global cod_client
        #al catelea client de la inceputul serverului
        try :
            while nr_clients < 3 and In_next_stage == False  :
                    client, address = Connection.accept()
                    if In_next_stage == False :
                        Coduri_pozitie_client[cod_client] = nr_clients 
                        nr_clients += 1
                        CLIENTS.append((client,cod_client))
                        newthread = threading.Thread(target = reciev_thread_from_client , args =(client,cod_client,1))
                        cod_client += 1 
                        Client_THREADS.append(newthread)
                        Client_THREADS[len(Client_THREADS)-1].start()
        except :
            print("daca nu a iesit hostul din lobby si vezi asta, avem o problema")
        Listening = False



    def draw_window () :
        global Selected_Colors
        if DEBUG_DARK_MODE == True:
            WIN.fill((128,128,128))
        else:
            WIN.fill((255,255,255))
        WIN.blit(Port_text,(25,25))
        WIN.blit(Exit_text,Exit_rect)
        WIN.blit(FPS_text,(25,25+40))
        #deseneaza cercurile si info-urile playerilor
        for i in range( len(Cerc_draw)) :
            pygame.draw.circle(WIN,Gri,Cerc_draw[i],diametru/2)
            if len(playeri) > i :
                pygame.draw.circle(WIN,Player_Colors[playeri[i][1]],Cerc_draw[i],diametru/2 - 10)
                Text_draw[i][1].center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
                WIN.blit(Text_draw[i][0],Text_draw[i][1])
                #Desenarea butoanelor de ready
                pygame.draw.rect(WIN,(0,0,0),(Cerc_draw[i][0]-diametru/2,Cerc_draw[i][1]+diametru/2 + 25,diametru,100))
                pygame.draw.rect(WIN,(255,255,255),(Cerc_draw[i][0]-diametru/2 + 5,Cerc_draw[i][1]+diametru/2 + 25 + 5,diametru -10,90))
                if playeri[i][2] == 1 :
                    pygame.draw.rect(WIN,Light_Green,(Cerc_draw[i][0]-diametru/2,Cerc_draw[i][1]+diametru/2 + 25,diametru,100))
                    text = FontR.render("Ready", True, Light_Green)
                else :
                    pygame.draw.rect(WIN,(0,0,0),(Cerc_draw[i][0]-diametru/2,Cerc_draw[i][1]+diametru/2 + 25,diametru,100))
                    text = FontR.render("Ready", True, (0,0,0))
                text_rect = text.get_rect()
                text_rect.center = (Cerc_draw[i][0]-diametru/2 + 5 +(diametru-10)/2 , Cerc_draw[i][1]+diametru/2 + 25 + 5 + 45)
                pygame.draw.rect(WIN,(255,255,255),(Cerc_draw[i][0]-diametru/2 + 5,Cerc_draw[i][1]+diametru/2 + 25 + 5,diametru -10,90))
                WIN.blit(text,text_rect)
                #desenarea butoanelor de kick
                if Role == "host" and i != 0 :
                    pygame.draw.rect(WIN,(0,0,0),(Cerc_draw[i][0]-diametru/2,Cerc_draw[i][1]+diametru/2 + 150,diametru,100))
                    pygame.draw.rect(WIN,(255,255,255),(Cerc_draw[i][0]-diametru/2 + 5,Cerc_draw[i][1]+diametru/2 + 150 + 5,diametru -10,90))
                    text = FontR.render("Kick", True, (0,0,0))
                    text_rect = text.get_rect()
                    text_rect.center = (Cerc_draw[i][0]-diametru/2 + 5 +(diametru-10)/2 , Cerc_draw[i][1]+diametru/2 + 150 + 5 + 45)
                    WIN.blit(text,text_rect)

        #deseneaza costumization rectul si tot ce e pe el
        if Costumization_Tab == True :
            pygame.draw.rect(WIN,Gri,Costumization_rect)
            for i in range(1,9) :
                x_cerc = Costumization_rect[0] + 25 * i + 101 *(i-1) + 40
                y_cerc = Costumization_rect[1] + Costumization_rect[3]/2
                if Selected_Colors[i-1] == 1 :
                    pygame.draw.circle(WIN,Light_Green,(x_cerc,y_cerc),50)
                pygame.draw.circle(WIN,(0,0,0),(x_cerc,y_cerc),42)
                pygame.draw.circle(WIN,Player_Colors[i],(x_cerc,y_cerc),40)
        #next_stage bar
        if started_cooldown == True :
            pygame.draw.rect(WIN, (230, 0, 0), pygame.Rect(0, HEIGHT - HEIGHT/25 , cooldown*WIDTH/Next_stage_cooldown,HEIGHT/25 ))

        pygame.display.update()
    
    #variabilele necesare chiar pentru ambele roluri
    global Pozitie
    Costumization_Tab = False
    All_Readied = False
    started_cooldown = False
    cooldown = -1

    #Se creaza toate variabilele de care are nevoie Hostul
    if Role == "host" :
        Pozitie = 0
        global nr_clients
        global cod_client
        global Confirmatii
        nr_clients = 0
        cod_client = 0
        playeri.append((name,1,0))
        Selected_Colors[0]=1
        #crearea textului de afisat al Portului
        Port_text = Font.render("Port: " + str(Port), True, Light_Green)
        #crearea textului de afisat al numelui
        text = Font.render(playeri[0][0], True, identifier_color)
        text_rect = text.get_rect()
        text_rect.center = (diametru + diametru/2,HEIGHT/2 - diametru/2-30)
        Text_draw.append((text,text_rect))
        CLIENTS = []
        Client_THREADS = []
        #threaduri care trebe reunite cu mainul
        Killed_Clients = []
        Coduri_pozitie_client = {}
        #inceperea ascultari pentru clienti
        In_next_stage = False
        Connection.listen(3)
        Listening_thread = threading.Thread(target = host_listen_thread)
        Listening_thread.start()
        Listening = True
        alive_thread = True
        #Lucrurile pe care trebe sa le trimita tuturor
        Transmit_to_all = []
        #daca a intrat in urmatoru stage
        #numarul de confirmari de la ceilalti plaieri (reprezinta daca clienti au terminat loading baru si au trecut mai departe)
        Confirmatii = 0
        sent_reaquest =False
    else :
        global Confirmation
        Confirmation = False
        #INCEPE Comunicarea intre client si server
        recv_from_server = threading.Thread(target = reciev_thread_from_server, args = (Connection,1))
        recv_from_server.start()

        Port_text = Font.render("Port: " + str(Port), True, Light_Green)

        Changes_from_server = []



    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)
        #Creaza textul pe care il afiseaza pentru FPS-uri
        FPS_text = Font.render("FPS: " + str(math.ceil(clock.get_fps())),True,Light_Green)

        #Daca lobiul este plin inchide threadul care asculta pentru noi clienti
        if Role == "host":
            if Listening == False and alive_thread == True:
                Listening_thread.join()
                alive_thread = False
            #Daca lobiul nu mai asculta pentru clienti si are mai putini clienti decat incap incepe din nou sa asculte
            elif nr_clients < 3 and Listening == False :
                Listening_thread = threading.Thread(target = host_listen_thread)
                Listening_thread.start()
                alive_thread = True
                Listening == True
            #Verifica daca sunt clients care trebe purged
            while len(Killed_Clients) > 0 :
                nr_clients -= 1
                Transmit_to_all.append((("leftplayer",Coduri_pozitie_client[Killed_Clients[0]] + 1),None))
                CLIENTS.pop(Coduri_pozitie_client[Killed_Clients[0]])
                Text_draw.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1)
                if playeri[Coduri_pozitie_client[Killed_Clients[0]] + 1][1] != 0 :
                    Selected_Colors[playeri[Coduri_pozitie_client[Killed_Clients[0]] + 1][1] - 1] = 0
                playeri.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1)
                Client_THREADS[Coduri_pozitie_client[Killed_Clients[0]]].join()
                Client_THREADS.pop(Coduri_pozitie_client[Killed_Clients[0]])
                Coduri_pozitie_client.pop(Killed_Clients[0])
                #reactualizare in dictionarul clientilor si pozitiile lor
                for i in Coduri_pozitie_client :
                    if Coduri_pozitie_client[i] > Killed_Clients[0] :
                        Coduri_pozitie_client[i] -= 1 
                        Text_draw[Coduri_pozitie_client[i]+1][1].center = (diametru*(Coduri_pozitie_client[i] + 2) + 50*(Coduri_pozitie_client[i] + 1) + diametru/2,HEIGHT/2 - diametru/2-30)
                Killed_Clients.pop(0)
            #Transmiterea schimbarilor clientilor
            while len(Transmit_to_all) > 0 :
                data_send = pickle.dumps(Transmit_to_all[0][0])
                data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                for i in range(len(CLIENTS)) :
                    if Transmit_to_all[0][1] == None or Coduri_pozitie_client[Transmit_to_all[0][1]] != i  :
                        CLIENTS[i][0].send(data_send)
                Transmit_to_all.pop(0)
        #Daca este client executa ce schimbari a facut serveru
        else :
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "newplayer" :
                    playeri.append(Changes_from_server[0][1])
                    Selected_Colors[playeri[len(playeri)-1][1]-1] = 1
                    text = Font.render(Changes_from_server[0][1][0], True, (0,0,0))
                    text_rect = text.get_rect()
                    text_rect.center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
                    Text_draw.append((text,text_rect))
                elif Changes_from_server[0][0] == "leftplayer" :
                    if playeri[Changes_from_server[0][1]][1] != 0 :
                        Selected_Colors[playeri[Changes_from_server[0][1]][1] - 1] = 0
                    playeri.pop(Changes_from_server[0][1])
                    Text_draw.pop(Changes_from_server[0][1])
                    if Changes_from_server[0][1] < Pozitie :
                        Pozitie -= 1 
                elif Changes_from_server[0][0] == "player_changed_color" :
                    if playeri[Changes_from_server[0][1]][1] != 0 :
                          Selected_Colors[playeri[Changes_from_server[0][1]][1]-1] = 0
                    playeri[Changes_from_server[0][1]] = (playeri[Changes_from_server[0][1]][0],Changes_from_server[0][2]+1,playeri[Changes_from_server[0][1]][2])
                    Selected_Colors[Changes_from_server[0][2]] = 1
                elif Changes_from_server[0][0] == "ready_state_change" :
                    if playeri[Changes_from_server[0][1]][2] == 0 :
                        playeri[Changes_from_server[0][1]] = (playeri[Changes_from_server[0][1]][0],playeri[Changes_from_server[0][1]][1],1)
                    else :
                        playeri[Changes_from_server[0][1]] = (playeri[Changes_from_server[0][1]][0],playeri[Changes_from_server[0][1]][1],0)
                Changes_from_server.pop(0)

        #Si clientul si serverul verifica daca toata lumea din Lobby este ready ca sa porneasca la urmatorul stage
        #verifica daca playeru vrea sa iasa din acest stage
        if exit_cooldown >= 0 :
            exit_cooldown -= 1
        #verificarea Ready stateurilor tuturor ca sa treaca la urmatoru stage
        if len(playeri) >= 1 :
            All_Readied = True
            for i in range(len(playeri)) :
                if playeri[i][2] == 0 :
                    All_Readied = False
                    break
            if All_Readied == True and started_cooldown == False :
                #Incepe timerul pentru intrarea in urmatorul stage
                started_cooldown = True
                cooldown = Next_stage_cooldown
            elif All_Readied == True and started_cooldown == True and cooldown > 0 :
                cooldown -= 1
            elif All_Readied == False and started_cooldown == True :
                started_cooldown = False
            if  cooldown == 0 and  started_cooldown == True:
                if Role == "host" :
                    if sent_reaquest == False :
                        In_next_stage = True
                        #trimite tuturor playerilor ca am trecut la urmatoru stage
                        data_send = pickle.dumps(("enter_next_stage",None))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        for i in range(len(CLIENTS)) :
                            CLIENTS[i][0].send(data_send)
                        sent_reaquest = True
                    elif Confirmatii == nr_clients :  
                        while len(Client_THREADS) > 0 :
                            Client_THREADS[0].join()
                            Client_THREADS.pop(0)
                        nr = len(playeri)
                        #Enter next stage
                        playeri, CLIENTS, Coduri_pozitie_client = Map_select(WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client)
                        #Return and reset the necesary variables
                        Confirmatii = 0
                        In_next_stage = False
                        if nr != len(playeri) :
                            nr_clients = len(playeri) -1
                            # se reseteaza culorile selectate si draw_text
                            Selected_Colors = [0,0,0,0,0,0,0,0]
                            Text_draw = []
                            for i in range(len(playeri)) :
                                Selected_Colors[playeri[i][1]-1] = 1
                                if i != Pozitie :
                                    text = Font.render(playeri[i][0], True, (0,0,0))
                                else :
                                    text = Font.render(playeri[i][0], True, identifier_color)
                                text_rect = text.get_rect()
                                text_rect.center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
                                Text_draw.append((text,text_rect))

                        #incepe ascultarea clientilor prezenti
                        for i in range(len(CLIENTS)) :
                            newthread = threading.Thread(target = reciev_thread_from_client , args =(CLIENTS[i][0],CLIENTS[i][1],0))
                            Client_THREADS.append(newthread)
                            Client_THREADS[len(Client_THREADS)-1].start() 
                        for i in range(len(playeri)) :
                             playeri[i] = (playeri[i][0],playeri[i][1],0)
                        started_cooldown = False
                else :
                    if Confirmation == True :
                        recv_from_server.join()
                        nr = len(playeri)
                        #Next Stage
                        playeri, Pozitie =Map_select(WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,None,None)
                        #Return and reset the necesary variables
                        Confirmation = False
                        #verifica daca au iesit playeri in proces
                        if nr != len(playeri) :
                            # se reseteaza culorile selectate si draw_text
                            Selected_Colors = [0,0,0,0,0,0,0,0]
                            Text_draw = []
                            for i in range(len(playeri)) :
                                Selected_Colors[playeri[i][1]-1] = 1
                                if i != Pozitie :
                                    text = Font.render(playeri[i][0], True, (0,0,0))
                                else :
                                    text = Font.render(playeri[i][0], True, identifier_color)
                                text_rect = text.get_rect()
                                text_rect.center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
                                Text_draw.append((text,text_rect))
                        recv_from_server = threading.Thread(target = reciev_thread_from_server, args = (Connection,0))
                        recv_from_server.start()
                        for i in range(len(playeri)) :
                                playeri[i] = (playeri[i][0],playeri[i][1],0)
                        started_cooldown = False


        draw_window()
        Button_rect = pygame.Rect((Cerc_draw[Pozitie][0]-diametru/2 + 5,Cerc_draw[Pozitie][1]+diametru/2 + 25 + 5,diametru -10,90))
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 :
                press_coordonaits = event.pos
                #se verifica daca playeru isi apasa imaginea sa
                distanta = math.sqrt(abs(Cerc_draw[Pozitie][0] - press_coordonaits[0])**2 + abs(Cerc_draw[Pozitie][1] - press_coordonaits[1])**2)
                if distanta <= diametru/2 :
                    if Costumization_Tab == True :
                        Costumization_Tab = False
                    else :
                        Costumization_Tab = True
                #verifica daca a apasat ceva in costumization tab
                elif Costumization_Tab == True and press_coordonaits[1] > Costumization_rect[1] and press_coordonaits[1] < Costumization_rect[1] + Costumization_rect[3] :
                    for i in range(8) :
                        y_cerc = Costumization_rect[1] + Costumization_rect[3]/2
                        if Selected_Colors[i] == 0 :
                            x_cerc = Costumization_rect[0] + 25 * (i+1) + 101 *i + 40
                            distanta = math.sqrt(abs(x_cerc - press_coordonaits[0])**2 + abs(y_cerc - press_coordonaits[1])**2)
                            if distanta <= 40 :
                                if Role == "host" :
                                    if playeri[Pozitie][1] != 0 :
                                        Selected_Colors[playeri[Pozitie][1]-1] = 0
                                    playeri[Pozitie] = (playeri[Pozitie][0],i+1,playeri[Pozitie][2])
                                    Selected_Colors[i] = 1
                                    #transmite clientilor faptu ca s-a schimbat culoarea unui player
                                    Transmit_to_all.append((("player_changed_color",Pozitie,i),None))
                                else :
                                    data_send = pickle.dumps(("want_change_color",i))
                                    data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                                    Connection.send(data_send)
                                break
                #verifica daca apasa ready buttonul 
                elif Button_rect.collidepoint(press_coordonaits) :
                    if playeri[Pozitie][2] == 0 :
                        playeri[Pozitie] = (playeri[Pozitie][0],playeri[Pozitie][1],1)  
                    else :
                        playeri[Pozitie] = (playeri[Pozitie][0],playeri[Pozitie][1],0)
                    #Transimiterea schimbari de stare la toti 
                    if Role == "host" :
                        Transmit_to_all.append((("ready_state_change",Pozitie),None)) 
                    else :
                        data_send = pickle.dumps(("ready_state_change",Pozitie))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        Connection.send(data_send)

                elif Role == "host" :
                    for i in range(len(playeri)-1) :
                        button_rect = pygame.Rect((Cerc_draw[i+1][0]-diametru/2 + 5,Cerc_draw[i+1][1]+diametru/2 + 150 + 5,diametru -10,90))
                        if button_rect.collidepoint(press_coordonaits) :
                            data_send = pickle.dumps(("Fuck_off",None))
                            data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                            CLIENTS[i][0].send(data_send)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE :
                if exit_cooldown == -1 :
                    exit_cooldown = 120
                elif exit_cooldown > 0 :
                    run= False
                    if Role == "host" :
                        data_send = pickle.dumps(("I_died...Fuck_off",None))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        for i in range(len(CLIENTS)) :
                            CLIENTS[i][0].send(data_send)
                            CLIENTS[i][0].close()
                    Connection.close()
                    break
                    


