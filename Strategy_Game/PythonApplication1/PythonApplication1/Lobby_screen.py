import pygame 
import os 
import socket
import pickle
import threading
import math

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

#variabile globale
nr_clients = 0
cod_client = 0

Pozitie = None
#Structura unui player 0 = numele , 1 = nr_culorii, 2 = Daca e ready sau nu
playeri = []
Text_draw = []

HEADERSIZE = 10
SPACE = "          "

def lobby(WIN,WIDTH,HEIGHT,FPS,Role,name,Connection , Port = None) :
    pygame.init()

    global playeri
    playeri = []
    Font = pygame.font.Font(None, 40)
    FontR = pygame.font.Font(None, 80)
    Cerc_draw = []
    Text_draw = []

    #coordonatele pentru cercuri
    y = HEIGHT/2
    diametru = (WIDTH - 50*3)/6
    for i in range(1,5) :
        x = diametru*i + diametru/2 + 50 *(i-1)
        Cerc_draw.append((x,y))
    #dreptunchiul de costumizare 
    Costumization_rect = ((WIDTH-101*8-25*9)/2,HEIGHT/2 - diametru/2 - 75 - 151,101*8+25*9,151)

    #Threadul care se ocupa cu primirea informatiilor de la server
    def reciev_thread_from_server(server) :
        global playeri
        global Pozitie
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
        #Formateaza si pregateste pentru afisare toate numele playerilor
        for i in range(len(playeri)) :
            text = Font.render(playeri[i][0], True, (0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
            Text_draw.append((text,text_rect))

        #The recieve loop
        try :
            while True :
                header = server.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = server.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    Changes_from_server.append(data_recv)
                else :
                    server.close()
                    run = False
                    break
        except :
            server.close()
            run = False

    #Threadul care se ocupa cu primirea informatiilor spre un client
    def reciev_thread_from_client(client,cod) :
        #Primeste numele clientului
        header = client.recv(10)
        header = header.decode("utf-8")
        data_recv = client.recv(int(header))
        playeri.append((data_recv.decode("utf-8"),0,0))
        Pozitie = len(playeri)-1
        Transmit_to_all.append((("newplayer",playeri[len(playeri)-1]),cod))
        #Trimite tot vectorul de playeri clientului
        data_send = pickle.dumps(playeri)
        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
        client.send(data_send)
        data_send = pickle.dumps(Pozitie)
        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
        client.send(data_send)
        #Formateaza numele si il pregateste de afisare
        text = Font.render(playeri[len(playeri)-1][0], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (diametru*(Coduri_pozitie_client[cod]+1) + 50*Coduri_pozitie_client[cod] + diametru/2,HEIGHT/2 - diametru/2-30)
        Text_draw.append((text,text_rect))
        #The recieve loop
        try :
            while True :
                header = server.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = server.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "want_change_color" :
                        if Selected_Colors[data_recv[1]] == 0 :
                            Selected_Colors[data_recv[1]] = 1
                            if playeri[Coduri_pozitie_client[cod]+1][1] != 0 :
                                    Selected_Colors[playeri[Coduri_pozitie_client[cod]+1][1]-1] = 0
                            playeri[Coduri_pozitie_client[cod]+1] = (playeri[Coduri_pozitie_client[cod]+1][0],data_recv[1]+1,playeri[Coduri_pozitie_client[cod]+1][2])
                            Transmit_to_all.append((("player_changed_color",Coduri_pozitie_client[cod]+1,data_recv[1]),None))
                    
                    elif data_recv[0] == "ready_state_change" :
                        Transmit_to_all.append((data_recv,cod))

                else :
                    client.close()
                    Killed_Clients.append(cod)
                    break
        except :
            client.close()
            Killed_Clients.append(cod)


    #Threadul care va asculta pentru si va acepta clienti
    def host_listen_thread() :
        global nr_clients
        global cod_client
        #al catelea client de la inceputul serverului
        while nr_clients < 3 :
                client, address = Connection.accept()
                Coduri_pozitie_client[cod_client] = nr_clients 
                nr_clients += 1
                CLIENTS.append(client)
                newthread = threading.Thread(target = reciev_thread_from_client , args =(client,cod_client))
                cod_client += 1 
                Client_THREADS.append(newthread)
                Client_THREADS[len(Client_THREADS)-1].start()


    def draw_window () :
        WIN.fill((255,255,255))
        WIN.blit(Port_text,(25,25))
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



        pygame.display.update()
    
    #variabilele necesare chiar pentru ambele roluri
    global Pozitie
    Costumization_Tab = False
    #Se creaza toate variabilele de care are nevoie Hostul
    if Role == "host" :
        Pozitie = 0
        global nr_clients
        global cod_client
        nr_clients = 0
        cod_client = 0
        playeri.append((name,0,0))
        #crearea textului de afisat al Portului
        Port_text = Font.render("Port: " + str(Port), True, Light_Green)
        #crearea textului de afisat al numelui
        text = Font.render(playeri[0][0], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (diametru + diametru/2,HEIGHT/2 - diametru/2-30)
        Text_draw.append((text,text_rect))
        CLIENTS = []
        Client_THREADS = []
        #threaduri care trebe reunite cu mainul
        Killed_Clients = []
        Coduri_pozitie_client = {}
        #inceperea ascultari pentru clienti`
        Connection.listen(3)
        Listening_thread = threading.Thread(target = host_listen_thread)
        Listening_thread.start()
        Listening = True

        #Lucrurile pe care trebe sa le trimita tuturor
        Transmit_to_all = []
    else :
        #INCEPE Comunicarea intre client si server
        recv_from_server = threading.Thread(target = reciev_thread_from_server, args = (Connection,))
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
            if nr_clients == 3 and Listening == True :
                Listening_thread.join()
                Listening = False
            #Daca lobiul nu mai asculta pentru clienti si are mai putini clienti decat incap incepe din nou sa asculte
            elif nr_clients < 3 and Listening == False :
                Listening_thread = threading.Thread(target = host_listen_thread)
                Listening_thread.start()
                Listening = True
            #Verifica daca sunt clients care trebe purged
            while len(Killed_Clients) > 0 :
                nr_clients -= 1
                Transmit_to_all.append((("leftplayer",Coduri_pozitie_client[Killed_Clients[0]] + 1),None))
                CLIENTS.pop(Coduri_pozitie_client[Killed_Clients[0]])
                Text_draw.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1)
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
                        client.send(data_send)
                Transmit_to_all.pop(0)
        else :
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "newplayer" :
                    if name != Changes_from_server[0][1][0] :
                        playeri.append(Changes_from_server[0][1])
                        text = Font.render(Changes_from_server[0][1][0], True, (0,0,0))
                        text_rect = text.get_rect()
                        text_rect.center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
                        Text_draw.append((text,text_rect))
                elif Changes_from_server[0][0] == "leftplayer" :
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



        draw_window()

        Button_rect = pygame.Rect((Cerc_draw[Pozitie][0]-diametru/2 + 5,Cerc_draw[Pozitie][1]+diametru/2 + 25 + 5,diametru -10,90))
        #print (Coduri_pozitie_client)
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
                #verifica daca apasa ready buttonul sau
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

                    


