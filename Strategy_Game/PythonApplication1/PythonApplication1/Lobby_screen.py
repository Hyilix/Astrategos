import pygame 
import os 
import socket
import pickle
import threading

White = (255,255,255)
nr_clients = 0

def lobby(WIN,WIDTH,HEIGHT,FPS,Role,name,Connection) :
    pygame.init()


    playeri = []
    Font = pygame.font.Font(None, 40)
    Cerc_draw = []
    Text_draw = []
    Threads = []

    #coordonatele pentru cercuri
    y = HEIGHT/2
    diametru = (WIDTH - 50*3)/6
    for i in range(1,5) :
        x = diametru*i + diametru/2 + 50 *(i-1)
        Cerc_draw.append((x,y))

    #Threadul care se ocupa cu primirea si trimiterea informatiilor spre un client
    def reciev_thread(client,cod) :
        while True :
             msg = client.recv(1024)
             print(msg)
             client.send(msg)
    #Threadul care va asculta pentru si va acepta clienti
    def host_listen_thread() :
        global nr_clients
        #al catelea client de la inceputul serverului
        cod_client = 0
        while True :
            while nr_clients < 3 :
                    client, address = Connection.accept()
                    nr_clients += 1
                    CLIENTS.append((client))
                    newthread = threading.Thread(target = reciev_thread , args =(client,cod_client))
                    Coduri_pozitie_client[cod_client] = nr_clients - 1
                    cod_client += 1 
                    Client_THREADS.append(newthread)
                    Client_THREADS[len(Client_THREADS)-1].start()


    def draw_window () :
        WIN.fill((255,255,255))
        for i in range( len(Cerc_draw)) :
            pygame.draw.circle(WIN,(225, 223, 240),Cerc_draw[i],diametru/2)
            if len(playeri) > i :
                pygame.draw.circle(WIN,White,Cerc_draw[i],diametru/2 - 10)
                WIN.blit(Text_draw[i][0],Text_draw[i][1])

        pygame.display.update()
        


    if Role == "host" :
        global nr_clients
        playeri.append((name,0))
        text = Font.render(playeri[0][0], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (diametru + diametru/2,HEIGHT/2 - diametru/2-30)
        Text_draw.append((text,text_rect))
        CLIENTS = []
        Client_THREADS = []
        Coduri_pozitie_client = {}

        Connection.listen()
        Listening_thread = threading.Thread(target = host_listen_thread)
        Listening_thread.start()



    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)
        
        draw_window()

        #print (Coduri_pozitie_client)
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)