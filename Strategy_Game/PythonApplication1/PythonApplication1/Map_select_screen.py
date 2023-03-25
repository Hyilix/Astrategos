import pygame 
import os 
import socket
import pickle
import threading
import math
import time
import random
from PIL import Image

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


resized = False
THE_MAP = -1
Map_Locations = []

def Map_select(WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client) :
    global run
    global MAPS
    global resized
    global THE_MAP
    global Map_Locations 
    global map_names

    THE_MAP = -1
    nr_harti = 0
    Map_Locations = []
    MAPS = []
    map_names = []

    Loaded_maps = False
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
    latura = 320
    pe_rand = 6
    while (pe_rand >4) and (Map_part-50-latura*pe_rand)/(pe_rand-1)<20 :
        pe_rand -= 1
    while (Map_part-50-latura*pe_rand)/(pe_rand-1)<20 and latura >200 :
        latura -= 32
    spatiu_intre = (Map_part-50-latura*pe_rand)/(pe_rand-1)

    limita_scroll =  100  + HEIGHT/25 + math.ceil(nr_harti/pe_rand) *latura + math.ceil(nr_harti/pe_rand) *25 - HEIGHT
    if limita_scroll <0 :
        limita_scroll = 0

    Map_load_action = ""
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
        if Loaded_maps == True :
            #desenarea barii de cooldown 
            pygame.draw.rect(WIN, (255, 255, 255), pygame.Rect(0, HEIGHT - HEIGHT/25 , WIDTH,HEIGHT/25 ))
            pygame.draw.rect(WIN, (230, 0, 0), pygame.Rect(0, HEIGHT - HEIGHT/25 , cooldown*WIDTH/Next_stage_cooldown,HEIGHT/25 ))
            pygame.display.update(0,HEIGHT-HEIGHT/25,WIDTH,HEIGHT/25)
        else :
            #afiseaza ce actiune se face la loading maps
            text = Font.render(Map_load_action,True,(0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (WIDTH/2, HEIGHT - HEIGHT/50 -12)
            pygame.draw.rect(WIN, (255, 255, 255), text_rect)
            WIN.blit(text,text_rect)
            pygame.display.update(text_rect[0],text_rect[1],text_rect[2],text_rect[3])

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
        nonlocal mapload_related_stuff
        try :
            while True :
                header = client.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    while len(data_recv) != int(header) :
                        data_recv += client.recv(int(header) - len(data_recv))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "sa_votat" :
                        Voturi[data_recv[3]]=(data_recv[1],data_recv[2])
                        Transmit_to_all.append((("sa_votat",data_recv[1],data_recv[2],data_recv[3]),cod))
                    elif data_recv[0] == "I_have_it" :
                        mapload_related_stuff.append(data_recv)
                    elif data_recv[0] == "I_don't_have_it" :
                        data_recv = (data_recv[0], cod)
                        mapload_related_stuff.append(data_recv)
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
                    while len(data_recv) != int(header) :
                        data_recv += server.recv(int(header) - len(data_recv))
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
                    elif data_recv[0] == "verify_map" or data_recv[0] == "new_line" or data_recv[0] == "end_info_stream" or data_recv[0] == "Map_image_part" or data_recv[0] == "Map_image_stream_end" or data_recv[0] == "End_of_map_sync" :
                        mapload_related_stuff.append(data_recv)
                    else :
                        Changes_from_server.append(data_recv)
                else :
                    server.close()
                    run = False
                    break
        except :
            server.close()
            run = False

    cooldown = Next_stage_cooldown

    def timer_thread ():
        nonlocal cooldown
        while cooldown > 0 :
            time.sleep(0.1)
            if cooldown > 0 and Loaded_maps == True :
                if All_voted :
                    cooldown -=0.3
                else :
                    cooldown -=0.1

    mapload_related_stuff = []
    #declararea variabilelor rolurilor specifice
    if Role == "host" :
        global Confirmatii
        Confirmatii=0
        sent_reaquest = False
        Client_THREADS = []
        Killed_Clients = []
        Transmit_to_all = []
        Transmit_to_specific = []
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

    def sync_maps() :
        nonlocal Loaded_maps
        nonlocal Map_load_action
        nonlocal mapload_related_stuff
        global MAPS
        global map_names
        #incepe procesul de sincronizare a hartilor
        Map_load_action = "Loading maps : start"
        if Role == "host" :
            nonlocal Transmit_to_all
            nonlocal Transmit_to_specific
            directory = "Maps\images"
            for filename in os.listdir(directory):
                #load map in folder
                adres=os.path.join(directory, filename)
                Map_load_action = "Loading maps : load " + adres[12:-4] + " map"
                MAPS.append(pygame.image.load(adres))
                map_names.append(adres[12:-4])
                #send verifications to clients
                Map_load_action = "Loading maps : send verification for " + adres[12:-4] + " map"
                Transmit_to_all.append((("verify_map",adres[12:-4]),None))
                verified = 0
                Map_load_action = "Loading maps : waiting for the others"
                #wait for confirmation/errors
                while verified != len(playeri) -1 :
                    time.sleep(0.1)
                    while len(mapload_related_stuff) > 0 :
                        if mapload_related_stuff[0][0] == "I_have_it" :
                            verified += 1
                        elif mapload_related_stuff[0][0] == "I_don't_have_it" :
                            Map_load_action = "Loading maps : send map_info of " + adres[12:-4] + " map to the Client nr. " + str(Coduri_pozitie_client[mapload_related_stuff[0][1]]) 
                            #incepe sa trimita map_info
                            map_info = open("Maps/info/"  + adres[12:-4] + ".txt","rb")
                            map_info = map_info.readlines()
                            #trimite fiecare linie din map_info clientilor care nu au harta
                            for line in map_info :
                                Transmit_to_specific.append((("new_line",line),mapload_related_stuff[0][1]))
                            #trimite ca sa terminat fisierul
                            Transmit_to_specific.append((("end_info_stream",None),mapload_related_stuff[0][1]))
                            #incepe sa trimita poza hartii
                            Map_load_action = "Loading maps : send map_image of " + adres[12:-4] + " map to the Client nr. " + str(Coduri_pozitie_client[mapload_related_stuff[0][1]]) 
                            image = pickle.dumps(Image.open(adres))
                            while len(image) > 0 :
                                Transmit_to_specific.append((("Map_image_part",image[:min(2048,len(image))]),mapload_related_stuff[0][1]))
                                image = image[min(2048,len(image)):]
                            Transmit_to_specific.append((("Map_image_stream_end",None),mapload_related_stuff[0][1]))
                            del image
                            Map_load_action = "Loading maps : waiting for the others"
                        mapload_related_stuff.pop(0)
            Transmit_to_all.append((("End_of_map_sync",None),None))
        else :
            r = True
            while r :
                time.sleep(0.1)
                while len(mapload_related_stuff) > 0 :

                    if mapload_related_stuff[0][0] == "verify_map" :
                        directory = "Maps\images"
                        the_name = mapload_related_stuff[0][1]
                        try :
                            adres = os.path.join(directory, mapload_related_stuff[0][1] + ".jpg")
                            #da load la harta
                            Map_load_action = "Loading maps : load " + adres[12:-4] + " map"
                            MAPS.append(pygame.image.load(adres))
                            map_names.append(adres[12:-4])
                            data_send = pickle.dumps(("I_have_it",None))
                            data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                            Connection.send(data_send)
                            Map_load_action = "Loading maps : waiting for the others"
                        except :
                            directory = "Maps\Imported_Maps\images"
                            try:
                                adres = os.path.join(directory, mapload_related_stuff[0][1] + ".jpg")
                                #da load la harta
                                Map_load_action = "Loading maps : load " + adres[12:-4] + " map"
                                MAPS.append(pygame.image.load(adres))
                                map_names.append(adres[26:-4])
                                data_send = pickle.dumps(("I_have_it",None))
                                data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                                Connection.send(data_send)
                                Map_load_action = "Loading maps : waiting for the others"
                            except:
                                #creaza un nou txt unde va pune map_info-ul primit de la server
                                Map_load_action = "Loading maps : receiving map_info from the host"
                                new_adres = "Maps\Imported_Maps\info" +"\\" 
                                map_file = open(new_adres + mapload_related_stuff[0][1] + ".txt","wb")
                                image = b''
                                data_send = pickle.dumps(("I_don't_have_it",mapload_related_stuff[0][1]))
                                data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                                Connection.send(data_send)

                    elif mapload_related_stuff[0][0] == "new_line" :
                        #pune o noua linie in file
                        map_file.write(mapload_related_stuff[0][1])

                    elif mapload_related_stuff[0][0] == "end_info_stream" :
                        #inchide fisierul in care am salvat map_info
                        map_file.close()
                        Map_load_action = "Loading maps : receiving map_image from the host"

                    elif mapload_related_stuff[0][0] == "Map_image_part" :
                        #obtinerea imaginii
                        Map_load_action = "Loading maps : load " + the_name + " map"
                        image += mapload_related_stuff[0][1][0:len(mapload_related_stuff[0][1])]
                    elif mapload_related_stuff[0][0] == "Map_image_stream_end" :
                        new_adres = "Maps\Imported_Maps\images" +"\\" 
                        #da load la imagine
                        image = pickle.loads(image)
                        image = image.save(new_adres + the_name + ".jpg" )
                        del image
                        MAPS.append(pygame.image.load(new_adres+the_name+".jpg"))
                        map_names.append(the_name)
                        #trimiterea serverului ca acum are imaginea
                        data_send = pickle.dumps(("I_have_it",None))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        Connection.send(data_send)
                        Map_load_action = "Loading maps : waiting for the others"
                    elif mapload_related_stuff[0][0] == "End_of_map_sync" :
                        r = False
                    mapload_related_stuff.pop(0)

        Loaded_maps = True

    #variabile de care au nevoie amandoi 
    Voturi = [None,None,None,None]
    All_voted = False

    clock = pygame.time.Clock()
    run=True

    thread_smt_on = True
    sync_maps_thread = threading.Thread(target = sync_maps)
    sync_maps_thread.start()


    time_thread = threading.Thread(target = timer_thread)
    time_thread.start() 
    while run==True :
        clock.tick(FPS)
        draw_window()

        if thread_smt_on == True :
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

        #se verifica daca se poate inchide threadul de load maps
        if Loaded_maps == True and thread_smt_on == True :
            sync_maps_thread.join()
            thread_smt_on = False

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
                    if Transmit_to_all[0][1] == None or Coduri_pozitie_client[Transmit_to_all[0][1]] != i :
                        CLIENTS[i][0].send(data_send)
                Transmit_to_all.pop(0)
            while len(Transmit_to_specific) > 0 :
                for i in range(min(len(Transmit_to_specific),100)) :
                    data_send = pickle.dumps(Transmit_to_specific[0][0])
                    data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                    CLIENTS[Coduri_pozitie_client[Transmit_to_specific[0][1]]][0].send(data_send)
                    Transmit_to_specific.pop(0)
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

        if cooldown <= 0 :
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
            elif event.type == pygame.MOUSEBUTTONDOWN and Loaded_maps == True :
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


    #Returnarea variabilelor necesare care s-ar fi putut schimba si motivul intoarceri in lobby
    time_thread.join()
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        return playeri,Pozitie 
