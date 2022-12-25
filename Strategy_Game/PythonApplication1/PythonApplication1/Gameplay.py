import pygame 
import os 
import socket
import pickle
import threading


pygame.init()

HEADERSIZE = 10
SPACE = "          "
Font = pygame.font.Font(None, 30)

run = True

#De stiut map_position este un nr de la 1 la 4 care reprezinta ce pozitie ii apartine acestei instante pe harta
def gameplay (WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client,map_name,map_position) :
    global run


    WIN.fill((255,255,255))
    pygame.display.update()

    #adresa pentru txt-ul hartii pe care se afla playeri
    map_adres = "Maps\info" + map_name + ".txt"


    def draw_window () :

        #desenarea Ui - ului 
        #Partea de sus
        pygame.draw.rect(WIN,(225, 223, 240),(0,0,WIDTH,HEIGHT/25))
        pygame.draw.rect(WIN,(0, 0, 0),(0,HEIGHT/25,WIDTH,5))
        #turn part
        pygame.draw.rect(WIN,(255, 0, 0),((WIDTH-260)/2,0,260,HEIGHT*2/25 + 5))
        pygame.draw.rect(WIN,(225, 223, 240),((WIDTH-250)/2,0,250,HEIGHT*2/25 ))
        text = Font.render(playeri[Whos_turn][0]+"'s TURN", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2,20)
        WIN.blit(text,text_rect)
        text = Font.render("Timer: "+("  "+str(timer))[-3:], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2,50)
        WIN.blit(text,text_rect)
        
        pygame.display.update()

    #Functia cu care serverul asculta pentru mesajele unui client
    def reciev_thread_from_client(client,cod) :
        try :
            while True :
                header = client.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    #se va proceseaza mesajul de la clinet
                else :
                    client.close()
                    Killed_Clients.append(cod)
                    break
        except :
            client.close()
            Killed_Clients.append(cod)

    #Functia clientului care asculta pentru mesaje de la server
    def reciev_thread_from_server(server) :
        global run
        try :
            while True :
                header = server.recv(10)
                header = header.decode("utf-8")

                if len(header) != 0 :
                    data_recv = server.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "I_died...Fuck_off":
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

    # Incarcarea variabilelor necesare rolurilor de host si client
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
    #variabilele necesare indiferent de rol
    Whos_turn = 0
    turn_time = 120
    timer = 120

    clock = pygame.time.Clock()
    run=True
    while run == True :
        clock.tick(FPS)
        #afiseaza totul
        draw_window()

        #se actualizeaza variabilele care au legatura cu comunicarea dintre server si client
        if Role == "host":
            # se verifica daca un player sa deconectat 
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
            #Se verifica daca este ceva de transmis la ceilalti playeri
            while len(Transmit_to_all) > 0 :
                data_send = pickle.dumps(Transmit_to_all[0][0])
                data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                for i in range(len(CLIENTS)) :
                    if Transmit_to_all[0][1] == None or Coduri_pozitie_client[Transmit_to_all[0][1]] != i  :
                        CLIENTS[i][0].send(data_send)
                Transmit_to_all.pop(0)
        else :
            #Se verifica daca serverul a trimis lucruri spre acest client
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "leftplayer" :
                    playeri.pop(Changes_from_server[0][1])
                    if Changes_from_server[0][1] < Pozitie :
                        Pozitie -= 1 
                Changes_from_server.pop(0)

        #The event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)

    #finalul functiei si returnarea variabilelor necesare care s-ar fi putut schimba
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        return playeri,Pozitie 

