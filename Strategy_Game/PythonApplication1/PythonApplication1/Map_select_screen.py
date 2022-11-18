import pygame 
import os 
import socket
import pickle
import threading

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

identifier_color = (255, 181, 0)

Font = pygame.font.Font(None, 40)

HEADERSIZE = 10
SPACE = "          "

run = False

def Map_select(WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client) :
    global run
    WIN.fill((255,255,255))
    pygame.display.update()

    diametru = (HEIGHT - 400)/4
    Map_part = WIDTH - diametru - 150
    if(Map_part < (WIDTH-150)*4/5) :
        Map_part = (WIDTH-150)*4/5
        diametru = (WIDTH-150)/5

    scroll = 0
    latura = (Map_part-25*7)/6
    limita_scroll =  150 + 10 *latura + 10 *25 - HEIGHT
    if limita_scroll <0 :
        limita_scroll = 0
    def draw_window () :
        #afisarea hartilor
        pygame.draw.rect(WIN,(80, 82, 81),(50,50,Map_part,HEIGHT-100))
        for i in range(10) :
            y_rand = 75 + i*latura + i*25 -scroll
            if y_rand+latura >50 :
                for j in range(6) :
                    x_coloana = 75 + j*latura + j*25
                    pygame.draw.rect(WIN,Gri,(x_coloana,y_rand,latura,latura))
        for i in range(len(Voturi)) :
            if  Voturi[i] != None :
                y_rand = 75 + Voturi[i][0]*latura + Voturi[i][0]*25 -scroll
                if y_rand +latura > 50 and y_rand < HEIGHT - 50 - latura/2 :
                    x_coloana = 75 + Voturi[i][1]*latura + Voturi[i][1]*25
                    #afiseaza votul
                    x = x_coloana + latura/8 + i*latura/4
                    if latura/8 > 25 :
                        y = y_rand + latura +25 - latura/8
                    else :
                        y = y_rand+latura
                    pygame.draw.circle(WIN,(225, 223, 240),(x,y),latura/8)
                    pygame.draw.circle(WIN,Player_Colors[playeri[i][1]],(x,y),latura/8 - (latura/8)/10)
        pygame.display.update((50,50,Map_part,HEIGHT-100))
        #Afisarea playerilor in dreapta
        pygame.draw.rect(WIN,(255, 255, 255),(50 + Map_part,50,diametru + 100,HEIGHT-50))
        for i in range(len(playeri)) :
            y = 50 + diametru/2 + ((HEIGHT -100- diametru*4)/3)*i + diametru*i
            pygame.draw.circle(WIN,(225, 223, 240),(WIDTH-diametru/2-50,y),diametru/2)
            pygame.draw.circle(WIN,Player_Colors[playeri[i][1]],(WIDTH-diametru/2-50,y),diametru/2 - 10)
            if i == Pozitie :
                text = Font.render(playeri[i][0], True, identifier_color)
            else :
                text = Font.render(playeri[i][0], True, (0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (WIDTH-diametru/2-50,y+diametru/2+25)
            WIN.blit(text,text_rect)
        pygame.display.update((50 + Map_part,50,diametru + 100,HEIGHT-50))

    def reciev_thread_from_client(client,cod) :
        try :
            while True :
                header = client.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                else :
                    client.close()
                    Killed_Clients.append(cod)
                    break
        except :
            client.close()
            Killed_Clients.append(cod)
    
    def reciev_thread_from_server(server) :
        global run
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

    if Role == "host" :
        Client_THREADS = []
        Killed_Clients = []
        Transmit_to_all = []
        #restart listening threads
        for i in range(len(CLIENTS)) :
            newthread = threading.Thread(target = reciev_thread_from_client , args =(CLIENTS[i][0],CLIENTS[i][1]))
            Client_THREADS.append(newthread)
            Client_THREADS[len(Client_THREADS)-1].start() 
    else :
        #restart listenig to the server
        recv_from_server = threading.Thread(target = reciev_thread_from_server, args = (Connection,))
        recv_from_server.start()
        Changes_from_server = []
    #variabile de care au nevoie amandoi 
    Voturi = [None,None,None,None]

    clock = pygame.time.Clock()
    run=True
    while run==True :
        clock.tick(FPS)
        draw_window()

        if Role == "host":
            while len(Killed_Clients) > 0 :
                Transmit_to_all.append((("leftplayer",Coduri_pozitie_client[Killed_Clients[0]] + 1),None))
                CLIENTS.pop(Coduri_pozitie_client[Killed_Clients[0]])
                playeri.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1)
                Client_THREADS[Coduri_pozitie_client[Killed_Clients[0]]].join()
                Client_THREADS.pop(Coduri_pozitie_client[Killed_Clients[0]])
                Coduri_pozitie_client.pop(Killed_Clients[0])
                #reactualizare in dictionarul clientilor si pozitiile lor
                for i in Coduri_pozitie_client :
                    if Coduri_pozitie_client[i] > Killed_Clients[0] :
                        Coduri_pozitie_client[i] -= 1 
                Killed_Clients.pop(0)
            while len(Transmit_to_all) > 0 :
                data_send = pickle.dumps(Transmit_to_all[0][0])
                data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                for i in range(len(CLIENTS)) :
                    if Transmit_to_all[0][1] == None or Coduri_pozitie_client[Transmit_to_all[0][1]] != i  :
                        CLIENTS[i][0].send(data_send)
                Transmit_to_all.pop(0)
        else :
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "leftplayer" :
                    playeri.pop(Changes_from_server[0][1])
                    if Changes_from_server[0][1] < Pozitie :
                        Pozitie -= 1 
                elif Changes_from_server[0][0] == "sa_votat" :
                    Voturi[Changes_from_server[0][3]]=(Changes_from_server[0][1],Changes_from_server[0][2])
                Changes_from_server.pop(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN :
                if event.button == 4 :
                    scroll = scroll - 50
                    if scroll<0 :
                        scroll = 0
                elif event.button == 5 :
                    scroll = scroll + 50
                    if scroll > limita_scroll :
                        scroll = limita_scroll
                elif event.button == 1  : 
                     press_coordonaits =  event.pos 
                     # se vede daca a apasat pe partea cu harti
                     if press_coordonaits[0]>50 and press_coordonaits[0]< 50 + Map_part and press_coordonaits[1]>50 and press_coordonaits[1]< HEIGHT - 50 :
                         # se determina ce rand si conoala se afla harta apasata
                         for i in range(10) :
                             y_rand = 75 + i*latura +i*25 - scroll
                             if y_rand +latura >50 :
                                 if press_coordonaits[1] >= y_rand and press_coordonaits[1] <= y_rand+latura :
                                     for j in range(6) :
                                         x_coloana = 75 + j*latura + j*25
                                         if press_coordonaits[0] >= x_coloana and press_coordonaits[0] <= x_coloana + latura :
                                             print(i," ",j)
                                             #voteaza harta
                                             if Role == "host" :
                                                 Voturi[Pozitie]=(i,j)
                                                 Transmit_to_all.append((("sa_votat",i,j,Pozitie),None))
                                             break
                                     break

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE :
                run =False

    #Returnarea variabilelor necesare care s-ar fi putut schimba si motivul intoarceri in lobby
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        return playeri,Pozitie 
