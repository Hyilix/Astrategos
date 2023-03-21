import pygame 
import os 
import socket
import pickle
import threading
import math
import time
import random

from Gameplay import gameplay

DEBUG_START_NOW = False

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

Confirmation = False
Confirmatii = 0
Next_stage_cooldown = 15

MAPS = []
map_names =[]
directory = "Maps\images"


resized = False
THE_MAP = -1
Map_Locations = []

def Map_select(WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client) :
    global run
    global MAPS
    global resized
    global THE_MAP
    global Map_Locations 
    THE_MAP = -1
    Map_Locations = []

    print("Loading maps")
    for filename in os.listdir(directory):
        adres=os.path.join(directory, filename)
        print(adres)
        MAPS.append(pygame.image.load(adres))
        map_names.append(adres[12:-4])

    WIN.fill((255,255,255))
    pygame.display.update()


    # determinarea marimilor icon-urilor playerilor
    diametru = (HEIGHT - 5*50 - HEIGHT/25)/4
    Map_part = WIDTH - diametru - 150
    if(Map_part < (WIDTH-150)*4/5) :
        Map_part = (WIDTH-150)*4/5
        diametru = (WIDTH-150)/5

    #dimensiunea hartilor afisate
    scroll = 0
    latura = 300
    pe_rand = 6
    while (pe_rand >4) and (Map_part-50-latura*pe_rand)/(pe_rand-1)<20 :
        pe_rand -= 1
    while (Map_part-50-latura*pe_rand)/(pe_rand-1)<20 and latura >200 :
        latura -= 25
    spatiu_intre = (Map_part-50-latura*pe_rand)/(pe_rand-1)
    #incarcarea hartiilor
    nr_harti = len(MAPS)
    if resized == False :
        for i in range(nr_harti):
            MAPS[i] = pygame.transform.scale(MAPS[i], (latura, latura))
        resized = True

    #stabilirea limitei de scroll
    limita_scroll =  100  + HEIGHT/25 + math.ceil(nr_harti/pe_rand) *latura + math.ceil(nr_harti/pe_rand) *25 - HEIGHT
    if limita_scroll <0 :
        limita_scroll = 0
    def draw_window () :
        #afisarea hartilor
        pygame.draw.rect(WIN,(80, 82, 81),(50,75,Map_part,HEIGHT- 100 - HEIGHT/25))
        for i in range(math.ceil(nr_harti/pe_rand)) :
            y_rand = 75 + i*latura + i*25 -scroll
            if y_rand+latura >50 and y_rand < HEIGHT -50 - HEIGHT/25  :
                for j in range(min(nr_harti-i*pe_rand,pe_rand)) :
                    x_coloana = 75 + j*latura + j*spatiu_intre
                    #pygame.draw.rect(WIN,Gri,(x_coloana,y_rand,latura,latura))
                    WIN.blit(MAPS[i*pe_rand + j],(x_coloana,y_rand))

        for i in range(len(Voturi)) :
            if  Voturi[i] != None :
                y_rand = 75 + Voturi[i][0]*latura + Voturi[i][0]*25 -scroll
                if y_rand +latura > 50 and y_rand < HEIGHT - 75 - HEIGHT/25 - latura/2 :
                    x_coloana = 75 + Voturi[i][1]*latura + Voturi[i][1]*spatiu_intre
                    #afiseaza votul
                    x = x_coloana + latura/8 + i*latura/4
                    if latura/8 > 25 :
                        y = y_rand + latura +25 - latura/8
                    else :
                        y = y_rand+latura
                    pygame.draw.circle(WIN,(225, 223, 240),(x,y),latura/8)
                    pygame.draw.circle(WIN,Player_Colors[playeri[i][1]],(x,y),latura/8 - (latura/8)/10)
        pygame.draw.rect(WIN,(80, 82, 81),(50,50,Map_part,25))
        pygame.draw.rect(WIN,(80, 82, 81),(50,HEIGHT- 50 - HEIGHT/25,Map_part,25))

        pygame.display.update((50,50,Map_part,HEIGHT- 75 - HEIGHT/25))
        #Afisarea playerilor in dreapta
        pygame.draw.rect(WIN,(255, 255, 255),(50 + Map_part,50,diametru + 100,HEIGHT-50))
        for i in range(len(playeri)) :
            y = 50 + diametru/2 + ((HEIGHT -100-HEIGHT/25- diametru*4)/3)*i + diametru*i
            pygame.draw.circle(WIN,(225, 223, 240),(WIDTH-diametru/2-50,y),diametru/2)
            pygame.draw.circle(WIN,Player_Colors[playeri[i][1]],(WIDTH-diametru/2-50,y),diametru/2 - 10)
            if i == Pozitie :
                text = Font.render(playeri[i][0], True, identifier_color)
            else :
                text = Font.render(playeri[i][0], True, (0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (WIDTH-diametru/2-50,y+diametru/2+25)
            WIN.blit(text,text_rect)
        pygame.display.update((50 + Map_part,50,diametru + 100,HEIGHT-50 - HEIGHT/25))
        #desenarea barii de cooldown 
        pygame.draw.rect(WIN, (255, 255, 255), pygame.Rect(0, HEIGHT - HEIGHT/25 , WIDTH,HEIGHT/25 ))
        pygame.draw.rect(WIN, (230, 0, 0), pygame.Rect(0, HEIGHT - HEIGHT/25 , cooldown*WIDTH/Next_stage_cooldown,HEIGHT/25 ))
        pygame.display.update(0,HEIGHT-HEIGHT/25,WIDTH,HEIGHT/25)
    #functia care  determina ce harta castiga dupa vot
    def rezultat_voturi () :
        harti_voturi = {}
        nrmax = 0
        candidati = []
        for i in range (len(Voturi)) :
            if Voturi[i] != None :
                #transforma coordonata 2-dimensionala in ce uni-dimensionala
                hart_nr = Voturi[i][0]*pe_rand + Voturi[i][1]
                try :
                    harti_voturi[hart_nr] += 1
                except :
                    harti_voturi[hart_nr] = 1
        for map in harti_voturi :
            if harti_voturi[map] > nrmax :
                candidati = []
                candidati.append(map)
            elif harti_voturi[map] == nrmax :
                candidati.append(map)
        #daca nu a fost nici una votata atunci alege una random
        if len(candidati) == 0 :
            return random.randint(0,nr_harti-1)
        else :
            return candidati[random.randint(0,len(candidati)-1)]

    def reciev_thread_from_client(client,cod) :
        global Confirmatii
        try :
            while True :
                header = client.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "sa_votat" :
                        Voturi[data_recv[3]]=(data_recv[1],data_recv[2])
                        Transmit_to_all.append((("sa_votat",data_recv[1],data_recv[2],data_recv[3]),cod))
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
    
    def reciev_thread_from_server(server) :
        global Confirmation
        global run
        global THE_MAP
        global Map_Locations
        try :
            while True :
                header = server.recv(10)
                header = header.decode("utf-8")

                if len(header) != 0 :
                    data_recv = server.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "enter_next_stage" :
                        THE_MAP = data_recv[1]
                        Map_Locations = data_recv[2]
                        data_send = pickle.dumps(("enter_next_stage",None))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        server.send(data_send)
                        Confirmation = True
                        break
                    elif data_recv[0] == "I_died...Fuck_off":
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

    def timer_thread ():
        nonlocal cooldown
        while True :
            time.sleep(0.1)
            if cooldown > 0 :
                if All_voted :
                    cooldown -=0.3
                else :
                    cooldown -=0.1
                if cooldown < 0 :
                    cooldown = 0
    #declararea variabilelor rolurilor specifice
    if Role == "host" :
        global Confirmatii
        Confirmatii=0
        sent_reaquest = False
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
    All_voted = False

    clock = pygame.time.Clock()
    run=True
    cooldown = Next_stage_cooldown
    time_thread = threading.Thread(target = timer_thread)
    time_thread.start() 
    while run==True :
        clock.tick(FPS)
        draw_window()

        if Role == "host":
            while len(Killed_Clients) > 0 :
                #actualizarea voturiilor
                for i in range(Coduri_pozitie_client[Killed_Clients[0]] + 1,3) :
                    Voturi[i] = Voturi[i+1]
                Voturi [3] = None 
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
                    for i in range(Changes_from_server[0][1],3) :
                        Voturi[i] = Voturi[i+1]
                    Voturi [3] = None 
                elif Changes_from_server[0][0] == "sa_votat" :
                    Voturi[Changes_from_server[0][3]]=(Changes_from_server[0][1],Changes_from_server[0][2])
                Changes_from_server.pop(0)

        # se verifica daca toti au votat si se modifica timerul in functie de asta
        if All_voted == False :
            if len(playeri) == 1 :
                if Voturi[0] !=None :
                    All_voted = True
            elif len(playeri) == 2  :
                if Voturi[0] !=None and Voturi[1] != None :
                    All_voted = True
            elif len(playeri) == 3  :
                if Voturi[0] !=None and Voturi[1] != None and Voturi[2] != None :
                    All_voted = True
            else :
                if Voturi[0] !=None and Voturi[1] != None and Voturi[2] != None and Voturi[3] != None :
                    All_voted = True

        elif  DEBUG_START_NOW == True :
            cooldown = 0

        if cooldown == 0 :
            if Role == "host" :
                if sent_reaquest == False :
                    #DETERMINA CARE ESTE HARTA CARE A CASTIGAT VOTUL 
                    THE_MAP = rezultat_voturi()
                    # De asemenea se determina pe ce pozitii vor di playeri
                    nr_pozitii = [1,2,3,4]
                    for i in range(len(playeri)) :
                        rand_pos = random.randint(0,len(nr_pozitii)-1)
                        Map_Locations.append(nr_pozitii[rand_pos])
                        nr_pozitii.pop(rand_pos)
                    #trimite tuturor playerilor ca am trecut la urmatoru stage dar le trimite si harta aleasa
                    for i in range(len(CLIENTS)) :
                        data_send = pickle.dumps(("enter_next_stage",THE_MAP,Map_Locations))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        CLIENTS[i][0].send(data_send)
                    sent_reaquest = True
                elif Confirmatii == len(playeri)-1 : 
                    while len(Client_THREADS) > 0 :
                        Client_THREADS[0].join()
                        Client_THREADS.pop(0)
                    #Enter next stage
                    playeri, CLIENTS, Coduri_pozitie_client = gameplay(WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client,map_names[THE_MAP],Map_Locations)
                    #Se iese si din map_select
                    run = False

            elif Confirmation ==  True :
                recv_from_server.join()
                #Enter next stage
                playeri, Pozitie = gameplay(WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,None,None,map_names[THE_MAP],Map_Locations)
                #Se iese si din map_select
                run = False
            
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
                         # se determina ce rand si coloana se afla harta apasata
                         for i in range(math.ceil(nr_harti/pe_rand)) :
                             y_rand = 75 + i*latura +i*25 - scroll
                             if y_rand +latura >50 :
                                 if press_coordonaits[1] >= y_rand and press_coordonaits[1] <= y_rand+latura :
                                     for j in range(min(pe_rand,nr_harti-i*pe_rand)) :
                                         x_coloana = 50 + j*latura + j*spatiu_intre
                                         if press_coordonaits[0] >= x_coloana and press_coordonaits[0] <= x_coloana + latura :
                                             Voturi[Pozitie]=(i,j)
                                             #voteaza harta
                                             if Role == "host" :
                                                 Transmit_to_all.append((("sa_votat",i,j,Pozitie),None))
                                             else :
                                                 data_send = pickle.dumps(("sa_votat",i,j,Pozitie))
                                                 data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                                                 Connection.send(data_send)
                                             break
                                     break

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE :
                run =False

    #Returnarea variabilelor necesare care s-ar fi putut schimba si motivul intoarceri in lobby
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        return playeri,Pozitie 
