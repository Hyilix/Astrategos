import pygame 
import os 
import socket
import pickle
import threading
import time
import math

import TileClass
import Structures
import Units
import Ores

pygame.init()

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

colorTable = {  #Table for assigning each controller with a color. If "None", then don't draw
    0 : (64,64,64),
    1 : None,
    2 : None,
    3 : None,
    4 : None
    }

HEADERSIZE = 10
SPACE = "          "
Font = pygame.font.Font(None, 30)
FontT = pygame.font.Font(None, 50)

run = True
timer = 120

Confirmatii_timer = 0
chat_notification = False

screen = pygame.display.Info()

rows = 40
tiles_per_row = 40

tiles = []

controllables_vec = []  #Vector containing units and tiles.

visible_tiles = []
partially_visible_tiles = []
path_tiles = [] #Tiles that a selected unit can move to

def draw_star(length, y, x):    #Determine what tiles the player currently sees.
    First = True
    visited_vec = []
    queued_tiles = [(y,x)]

    directions = [
        (-1,0),
        (1,0),
        (0,1),
        (0,-1)
    ]

    checks = 0
    tries = 0

    isDone = False

    while not isDone:
        if length < 0: break
        new_tiles = []

        for myTile in queued_tiles:
            tries += 1

            x = myTile[1]
            y = myTile[0]
            stop = False
            try:
                stop = myTile[2]
            except:
                print("WELP")

            if (y, x) not in visited_vec:
                if x >= 0 and y >= 0 and y < rows and x < tiles_per_row and (stop == False or First == True):
                    checks += 1
                    visited_vec.append((y, x))
                    if (x, y) not in visible_tiles: visible_tiles.append((x, y))
                    if (x, y) not in partially_visible_tiles: partially_visible_tiles.append((x, y))

                    for direction in directions:
                        in_x = direction[0]
                        in_y = direction[1]
                        if (y + in_y, x + in_x) not in visited_vec:
                            if tiles[y][x].collidable == False:
                                new_tiles.append((y + in_y, x + in_x))
                            
                            elif tiles[y][x].collidable == True and y + in_y >= 0 and x + in_x >= 0 and y + in_y < rows and x + in_x < tiles_per_row and tiles[y + in_y][x + in_x].collidable == False:
                                if First == False:
                                    new_tiles.append((y + in_y, x + in_x, True))
                                else:
                                    new_tiles.append((y + in_y, x + in_x))
                                    First = False

        queued_tiles.clear()

        if len(new_tiles) == 0: isDone = True

        queued_tiles += new_tiles
        length -= 1

    visited_vec.clear()
    queued_tiles.clear()

def determine_visible_tiles():
    if TileClass.full_bright == False:
        visible_tiles.clear()
        for obj in controllables_vec:
            draw_star(obj.fog_range, obj.position[1], obj.position[0])

selected_controllable = None
enlighted_surface = None

#De stiut map_locations este un vector de aceasi lungime cu vectorul de playeri care contine locatia de pe hart a fiecaruia reprezentata printr-un nr de la 1 la 4
def gameplay (WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client,map_name,map_locations) :
    TileClass.show_walls = False
    global run
    global timer 
    global Confirmatii_timer
    global chat_notification
    global colorTable
    global selected_controllable
    global enlighted_surface

    def draw_path_star(length, y, x):
        visited_vec = []
        queued_tiles = [(y,x)]

        directions = [
            (-1,0),
            (1,0),
            (0,1),
            (0,-1)
        ]

        checks = 0
        tries = 0

        isDone = False

        while not isDone:
            if length < 0: break
            new_tiles = []

            for myTile in queued_tiles:
                tries += 1

                x = myTile[1]
                y = myTile[0]

                if (y, x) not in visited_vec and (x, y) in visible_tiles and (x, y) in partially_visible_tiles:
                    if x >= 0 and y >= 0 and y < rows and x < tiles_per_row:
                        checks += 1
                        visited_vec.append((y, x))
                        if (x, y) not in path_tiles and tiles[y][x].unit == None: path_tiles.append((x, y))
                        for direction in directions:
                            in_x = direction[0]
                            in_y = direction[1]
                            if (y + in_y, x + in_x) not in visited_vec:
                                Y = y + in_y
                                X = x + in_x
                                if Y >= 0 and X >= 0 and Y < rows and X < tiles_per_row:
                                    if tiles[Y][X].collidable == False and (tiles[Y][X].structure == None or (tiles[Y][X].structure.owner == map_locations[Pozitie] and tiles[Y][X].structure.canShareSpace == True)) and tiles[Y][X].ore == None:
                                        new_tiles.append((y + in_y, x + in_x))

            queued_tiles.clear()

            if len(new_tiles) == 0: isDone = True

            queued_tiles += new_tiles
            length -= 1

        visited_vec.clear()
        queued_tiles.clear()

    def determine_enlighted_tiles():
        path_tiles.clear()
        draw_path_star(selected_controllable.move_range, selected_controllable.position[1], selected_controllable.position[0])

    colorTable = {  #Remake the dictionary
    0 : (64,64,64),
    1 : None,
    2 : None,
    3 : None,
    4 : None
    }

    TileClass.full_bright = False  #if full_bright == True, player can see the whole map at any time, like in editor.

    index = 0
    for player in playeri:  #assign colors to structures and units. Any structure/unit with 
        colorTable[map_locations[index]] = Player_Colors[player[1]]
        index += 1
    TileClass.colorTable = colorTable
    del index

    WIN.fill((255,255,255))
    pygame.display.update()

    if TileClass.full_bright == True:
        for y in range(rows):
            for x in range(tiles_per_row):
                visible_tiles.append((x,y))
                partially_visible_tiles.append((x,y))

    chat_icon = pygame.transform.scale(pygame.image.load('Assets/Gameplay_UI/chatbox-icon.png'),(60,60))
    mithril_icon = pygame.transform.scale(pygame.image.load('Assets/Gameplay_UI/mars-mithril-bar-1.png'),(32,32))
    flerovium_icon = pygame.transform.scale(pygame.image.load('Assets/Gameplay_UI/mars-flerovium-crystal-1.png'),(32,32))
    man_power_icon = pygame.transform.scale(pygame.image.load('Assets/Units/Marine.png'),(32,32))

    # incaracarea imaginilor structurilor si unitatilor care le poate produce playeru, cu culoarea specifica.
    grosime_outline = 5
    spatiu_intre = (HEIGHT/3 - 5 - 70*3)/3
    C_menu_scroll = 0
    Element_selectat = None
    large_img_element_afisat = None
    structures = []

    directory = "Assets\Structures"
    for filename in os.listdir(directory):
        adres=os.path.join(directory, filename)
        structures.append(pygame.transform.scale(pygame.image.load(adres),(64,64)))
    #colorarea structurilor cu culoarea playerului
    for structure in structures :
        for i in range(structure.get_width()):
            for j in range(structure.get_height()):
                if structure.get_at((i,j)) == (1,1,1):
                    structure.set_at((i,j), Player_Colors[playeri[Pozitie][1]])

    units = []
    directory = "Assets" + '\\' + "Units"
    for filename in os.listdir(directory):
        adres=os.path.join(directory, filename)
        units.append(pygame.transform.scale(pygame.image.load(adres),(64,64)))
    #colorarea unitatilor cu culoarea playerului
    for unit in units :
        for i in range(unit.get_width()):
            for j in range(unit.get_height()):
                if unit.get_at((i,j)) == (1,1,1):
                    unit.set_at((i,j), Player_Colors[playeri[Pozitie][1]])


    def draw_window () :
        WIN.fill((255,255,255))

        #Draw map
        tempSurface = pygame.Surface((WIDTH, HEIGHT))
        tempSurface.blit(mapSurface, (0, 0), (CurrentCamera.x, CurrentCamera.y, WIDTH, HEIGHT))

        if enlighted_surface != None:
            tempSurface.blit(enlighted_surface, (0, 0), (CurrentCamera.x, CurrentCamera.y, WIDTH, HEIGHT))

        WIN.blit(tempSurface, (0, 0)) 

        #draw selected tile outline
        if selected_tile[0] != None : 
            x_tile=selected_tile[0]* current_tile_length - CurrentCamera.x
            y_tile = selected_tile[1]* current_tile_length - CurrentCamera.y
            pygame.draw.rect(WIN,Light_Green,(x_tile,y_tile,current_tile_length,math.ceil(grosime_outline*CurrentCamera.zoom)))
            pygame.draw.rect(WIN,Light_Green,(x_tile,y_tile,math.ceil(grosime_outline*CurrentCamera.zoom),current_tile_length))
            pygame.draw.rect(WIN,Light_Green,(x_tile,y_tile+current_tile_length-math.ceil(grosime_outline*CurrentCamera.zoom),current_tile_length,math.ceil(grosime_outline*CurrentCamera.zoom)))
            pygame.draw.rect(WIN,Light_Green,(x_tile+current_tile_length-math.ceil(grosime_outline*CurrentCamera.zoom),y_tile,math.ceil(grosime_outline*CurrentCamera.zoom),current_tile_length))

        #desenarea Ui - ului 
        #chat windowul daca este deschis
        if Chat_window :
            pygame.draw.rect(WIN,(25,25,25),((WIDTH-260)/2 + 260,0,5,HEIGHT))
            pygame.draw.rect(WIN,(225, 223, 240),((WIDTH-260)/2 + 260 + 5,0,(WIDTH-260)/2-5,HEIGHT))
            #writing box
            if writing_in_chat == False :
                pygame.draw.rect(WIN,(25,25,25),((WIDTH-260)/2 + 265,HEIGHT -55,(WIDTH-260)/2 - 5,5))
            else :
                pygame.draw.rect(WIN,Light_Green,((WIDTH-260)/2 + 265,HEIGHT -55,(WIDTH-260)/2 - 5,5))
                pygame.draw.rect(WIN,Light_Green,((WIDTH-260)/2 + 260,HEIGHT-55,5,55))
            #mesajul care se scrie 
            litere_afisate = 70
            text = Font.render(message[-litere_afisate:],True,Player_Colors[playeri[Pozitie][1]])
            text_rect = text.get_rect()
            while text_rect[2] > (WIDTH-260)/2 -15 :
                litere_afisate -= 1
                text = Font.render(message[-litere_afisate:],True,Player_Colors[playeri[Pozitie][1]])
                text_rect = text.get_rect()

            WIN.blit(text,((WIDTH-260)/2 + 270,HEIGHT-35))
            #mesajele scrise pana acum
            x = (WIDTH-260)/2 + 270
            y = HEIGHT - 90
            for i in range(len(chat_archive)-1 - chat_scroll,-1,-1) :
                WIN.blit(chat_archive[i][0],(x,y))
                if chat_archive[i][1] == 0 :
                    y  -= 20
                else :
                    y -= 30
                if  y < HEIGHT/25 + 5 - 10 :
                    break
                
        #Partea de sus
        pygame.draw.rect(WIN,(225, 223, 240),(0,0,WIDTH,HEIGHT/25))
        pygame.draw.rect(WIN,(25,25,25),(0,HEIGHT/25,WIDTH,5))
        #Afisarea resurselor detinute
        WIN.blit(mithril_icon,(5,(HEIGHT/25-32)/2))
        mit_count = Font.render(str(Mithril),True,(75, 91, 248))
        mit_rect = mit_count.get_rect()
        WIN.blit(mit_count,(15 + 32,(HEIGHT/25-mit_rect[3])/2))
        fle_count = Font.render(str(Flerovium),True,(152, 65, 182))
        fle_rect = fle_count.get_rect()
        WIN.blit(flerovium_icon,(15+32+60+10,(HEIGHT/25-32)/2))
        WIN.blit(fle_count,(15+64+60+20,(HEIGHT/25-fle_rect[3])/2))
        man_power_count = Font.render(("  " + str(Man_power_used))[-3:]+' / '+ str(Max_Man_power),True,(0,0,0))
        man_rect = man_power_count.get_rect()
        WIN.blit(man_power_icon,(15+32*2+60*2+10*3,(HEIGHT/25-32)/2))
        WIN.blit(man_power_count,(15+32*3+60*2+10*4,(HEIGHT/25-man_rect[3])/2))
        #turn part
        pygame.draw.rect(WIN,Player_Colors[playeri[Whos_turn][1]],((WIDTH-260)/2,0,260,HEIGHT*2/25 + 5))
        pygame.draw.rect(WIN,(225, 223, 240),((WIDTH-250)/2,0,250,HEIGHT*2/25 ))
        text = Font.render(playeri[Whos_turn][0]+"'s TURN", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2,20)
        WIN.blit(text,text_rect)
        text = Font.render("Timer: "+("  "+str(timer))[-3:], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2,60)
        WIN.blit(text,text_rect)
        #butonul de end Turn
        if Whos_turn == Pozitie :
            pygame.draw.rect(WIN,Player_Colors[playeri[Whos_turn][1]],((WIDTH-260)/2,HEIGHT*2/25 + 5,260,35))
            pygame.draw.rect(WIN,(225, 223, 240),((WIDTH-250)/2,HEIGHT*2/25 + 5,250,30))
            text = Font.render("End Turn", True, (150,0,0))
            text_rect = text.get_rect()
            text_rect.center = (WIDTH/2,HEIGHT*2/25 + 20)
            WIN.blit(text,text_rect)
        #butonul de chat din dreapta sus
        pygame.draw.rect(WIN,(25,25,25),(WIDTH-80,0,80,80))
        pygame.draw.rect(WIN,(225, 223, 240),(WIDTH-75,0,75,75))
        WIN.blit(chat_icon,(WIDTH - 68,8))
        if chat_notification == True :
            pygame.draw.circle(WIN,Red,(WIDTH-10,20),8)
        #Partea de jos a UI-ului
        # draw mini_map part
        pygame.draw.rect(WIN,(25,25,25),(0,HEIGHT-HEIGHT/3,HEIGHT/3,HEIGHT/3))
        #desenarea chenarului su informatiile despre ce este selectat
        if selected_tile[0] !=None :
            if tile_empty == True :
                pygame.draw.rect(WIN,(25,25,25),(HEIGHT/3,HEIGHT*4/5-5 , WIDTH - HEIGHT*2/3,5))
                pygame.draw.rect(WIN,(225, 223, 240),(HEIGHT/3,HEIGHT*4/5 , WIDTH - HEIGHT*2/3,HEIGHT/5))
                #se afiseaza meniul de constructie daca tile-ul este empty
                pygame.draw.rect(WIN,(25,25,25),(WIDTH- HEIGHT/3, HEIGHT - HEIGHT/3 -55,5,HEIGHT/3 + 55))
                pygame.draw.rect(WIN,(25,25,25),(WIDTH- HEIGHT/3, HEIGHT - HEIGHT/3 -5,HEIGHT/3,5))
                pygame.draw.rect(WIN,(25,25,25),(WIDTH- HEIGHT/3, HEIGHT - HEIGHT/3 -60,HEIGHT/3,5))
                pygame.draw.rect(WIN,(225, 223, 240),(WIDTH- HEIGHT/3 +5, HEIGHT - HEIGHT/3,HEIGHT/3-5,HEIGHT/3))
                pygame.draw.rect(WIN,(225, 223, 240),(WIDTH- HEIGHT/3 +5, HEIGHT - HEIGHT/3-55,HEIGHT/3-5,50))
                #draw the name of the menu
                text = FontT.render(construction_tab,True,(0,0,0))
                text_rect = text.get_rect()
                text_rect.center = (WIDTH - (HEIGHT/3 -5)/2,HEIGHT*2/3 - 30)
                WIN.blit(text,text_rect)
                # afisarea lucrurilor din meniul de constructii
                if construction_tab == "Structures" :
                    elements = len(structures)
                elif construction_tab == "Units" :
                    elements = len(units)
                else :
                    elements = 0
                for i in range(construction_tab_scroll,math.ceil(elements/3)) :
                    y_rand = HEIGHT*2/3 +10 + i*70 + i*10 - C_menu_scroll
                    if y_rand+35 > HEIGHT*2/3 and y_rand < HEIGHT  :
                        for j in range(min(elements-i*3,3)) :
                            x_coloana = WIDTH-HEIGHT/3+5 + j*70 + (j+0.5)*spatiu_intre
                            if  Element_selectat != i*3 + j :
                                pygame.draw.rect(WIN,(57, 56, 57),(x_coloana,y_rand,70,70))
                            else :
                                pygame.draw.rect(WIN,Light_Green,(x_coloana,y_rand,70,70))
                            pygame.draw.rect(WIN,Gri,(x_coloana+2,y_rand+2,66,66))
                            if construction_tab == "Structures" :
                                WIN.blit(structures[i*3+j],(x_coloana+3,y_rand+3))
                            elif construction_tab == "Units" :
                                WIN.blit(units[i*3+j],(x_coloana+3,y_rand+3))
                #Afisarea imaginii si informatiilor elementului selectat din meniul de structuri
                if Element_selectat != None :
                    #desenare chenarul in care sa se incadreze imaginea
                    pygame.draw.rect(WIN,(25,25,25),(HEIGHT/3+20,HEIGHT*4/5+20,large_img_element_afisat.get_width()+10,large_img_element_afisat.get_width()+10))
                    pygame.draw.rect(WIN,Gri,(HEIGHT/3+25,HEIGHT*4/5+25,large_img_element_afisat.get_width(),large_img_element_afisat.get_width()))
                    WIN.blit(large_img_element_afisat,(HEIGHT/3+25,HEIGHT*4/5+25))
            else :
                pygame.draw.rect(WIN,(25,25,25),(HEIGHT/3,HEIGHT*4/5-5 , WIDTH - HEIGHT/3,5))
                pygame.draw.rect(WIN,(225, 223, 240),(HEIGHT/3,HEIGHT*4/5, WIDTH - HEIGHT/3,HEIGHT/5))
                #daca este selectata o unitate sau cladire o afiseaza :
                if tile_empty == False and (tiles[selected_tile[1]][selected_tile[0]].structure != None or tiles[selected_tile[1]][selected_tile[0]].unit != None) :
                    pygame.draw.rect(WIN,(25,25,25),(HEIGHT/3+20,HEIGHT*4/5+20,large_img_element_afisat.get_width()+10,large_img_element_afisat.get_width()+10))
                    pygame.draw.rect(WIN,Gri,(HEIGHT/3+25,HEIGHT*4/5+25,large_img_element_afisat.get_width(),large_img_element_afisat.get_width()))
                    WIN.blit(large_img_element_afisat,(HEIGHT/3+25,HEIGHT*4/5+25))

        pygame.display.update()

    #Functia cu care serverul asculta pentru mesajele unui client
    def reciev_thread_from_client(client,cod) :
        global Confirmatii_timer
        try :
            while True :
                header = client.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    #se va proceseaza mesajul de la clinet
                    if data_recv[0] == "timer is zero" :
                        Confirmatii_timer = Confirmatii_timer + 1
                    elif data_recv[0] == "new_message" :
                        Changes_from_clients.append(data_recv)
                        Transmit_to_all.append((data_recv,None))
                    elif data_recv[0] == "Force_end_turn" :
                        Changes_from_clients.append(data_recv)
                        Transmit_to_all.append((("Force_end_turn",None),cod))
                    else :
                        Changes_from_clients.append(data_recv)
                        Transmit_to_all.append((data_recv,cod))
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

    #Un thread care va functiona la host care are rolul sa tina cont de cat timp trece in timpul jocului
    def timer_thread ():
        global timer
        while True :
            time.sleep(1)
            if timer > 0 :
                timer = timer - 1
                Transmit_to_all.append((("a second passed",None),None))

    #functia care prelucreaza un mesaj(indiferent de lung) in randuri pe care sa le puna in mesajes
    def archive_message (mesaj,name,color) :
        global chat_notification
        chat_archive.append((Font.render("<"+ name + ">",True,color),1))
        if Chat_window == False :
            chat_notification = True
        cuvinte = mesaj.split()
        rand = ""

        index = 0
        while index < len(cuvinte) :
            if len(rand) != 0 :
                rand_aux = rand +" "+ cuvinte[index]
            else :
                rand_aux = cuvinte[index]
            text = Font.render(rand_aux,True,color)
            text_rect = text.get_rect()
            if text_rect[2] > (WIDTH-260)/2 -15 :
                if rand != "" :
                    chat_archive.append((Font.render(rand,True,color),0))
                    rand = ""
                else :
                    fin = 0
                    while text_rect[2] > (WIDTH-260)/2 -15 :
                        fin -= 1
                        text = Font.render(rand_aux[:fin],True,Player_Colors[playeri[Pozitie][1]])
                        text_rect = text.get_rect()
                    chat_archive.append((text,0))
                    rand = rand_aux[fin:]
                    index += 1 
            else :
                rand = rand_aux
                index += 1
        if len(rand) > 0 :
            chat_archive.append((Font.render(rand,True,color),0))

    def reverse_action (Action) :
        #reverse unit movement
        if Action[0] == "move_unit" :
            tiles[Action[1][1]][Action[1][0]].unit = tiles[Action[2][1]][Action[2][0]].unit
            tiles[Action[1][1]][Action[1][0]].unit.position = tiles[Action[1][1]][Action[1][0]].position

            del tiles[Action[2][1]][Action[2][0]].unit
            tiles[Action[2][1]][Action[2][0]].unit = None

            refresh_map([Action[1], Action[2]])

            tiles[Action[1][1]][Action[1][0]].unit.canAction = True

    #variabilele necesare indiferent de rol
    Whos_turn = 0
    turn_time = 30
    timer = turn_time
    Chat_window = False
    writing_in_chat = False
    message = ""
    chat_scroll = 0
    chat_notification = False
    #in acest vector vor fi pastrate randurile de pe chat
    chat_archive = []
    #tile_ul care este examinat de player
    selected_tile = [None,None]
    tile_empty = True
    construction_tab = "Structures"
    construction_tab_scroll = 0
    #Resursele playerului 
    Mithril = 5555
    Flerovium = 5555
    Man_power_used = 0
    Max_Man_power = 100
    #Vectorul care detine actiunile playerului din tura lui
    Turn_Actions = []
    Ctrl_zeed = False
    # Incarcarea variabilelor necesare rolurilor de host si client
    if Role == "host" :
        Confirmatii_timer = 0
        Client_THREADS = []
        Killed_Clients = []
        Transmit_to_all = []
        Changes_from_clients = []
        #restart listening threads
        for i in range(len(CLIENTS)) :
            newthread = threading.Thread(target = reciev_thread_from_client , args =(CLIENTS[i][0],CLIENTS[i][1]))
            Client_THREADS.append(newthread)
            Client_THREADS[len(Client_THREADS)-1].start() 
        time_thread = threading.Thread(target = timer_thread)
        time_thread.start() 
    else :
        #restart listenig to the server
        recv_from_server = threading.Thread(target = reciev_thread_from_server, args = (Connection,))
        recv_from_server.start()
        Changes_from_server = []
        timer_notification_sent = False
        next_turn = False

    #Camera, texture resizing and load function
    class Camera:
        def __init__(self, position, zoom, max_zoom, min_zoom):
            self.x = position[0]
            self.y = position[1]
            self.zoom = zoom
            self.max_zoom = max_zoom
            self.min_zoom = min_zoom
        
            self.camera_movement = 15

            #make sure the zoom is insde [min_zoom, max_zoom]
            if min_zoom > zoom:
                self.zoom = self.min_zoom

            if zoom > max_zoom:
                self.zoom = self.max_zoom

        def Update_Camera_Zoom_Level(self):     #Make sure the camera zoom is within [min_zoom, max_zoom]
            if self.min_zoom > self.zoom:
                self.zoom = self.min_zoom

            if self.zoom > self.max_zoom:
                self.zoom = self.max_zoom

        def Check_Camera_Boundaries(self):     #Check if camera is within the boundaries of the map. If not, bring it there
            if self.x - self.camera_movement < - WIDTH // 2:
                self.x  = 0 - WIDTH // 2
            if self.y - self.camera_movement < - HEIGHT // 2:
                self.y = 0 - HEIGHT // 2
            if self.x + self.camera_movement + WIDTH // 2 > tiles_per_row * current_tile_length:
                self.x = tiles_per_row * current_tile_length - WIDTH // 2
            if self.y + self.camera_movement + HEIGHT // 2 > rows * current_tile_length:
                self.y = rows * current_tile_length - HEIGHT // 2

        def Calculate_After_Zoom_Position(self, last_map_size_x, map_size_x, last_map_size_y, map_size_y):  #Make the camera stay in the middle when zooming in/out
            self.x = int((self.x + WIDTH // 2) / last_map_size_x * map_size_x) - WIDTH // 2
            self.y = int((self.y + HEIGHT // 2) / last_map_size_y * map_size_y) - HEIGHT // 2

    CurrentCamera = Camera((0,0), 1, 1.4, 0.4)

    normal_tile_length = TileClass.base_texture_length    #the length of a tile when the zoom is 1
    current_tile_length = normal_tile_length * CurrentCamera.zoom

    TileClass.resize_textures(current_tile_length)
    Structures.resize_textures(current_tile_length)
    Units.resize_textures(current_tile_length)
    Ores.resize_textures(current_tile_length)

    #The base surface of the map. Zooming in/out will use this surface.
    mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))

    def load_map(map_name):
        try:
            with open("Maps/info/" + map_name + ".txt", "rb") as infile:
                print("STARTED")
                tiles.clear()
                global rows
                global tiles_per_row
                rows = pickle.load(infile)
                tiles_per_row = pickle.load(infile)
                nonlocal mapSurfaceNormal 
                mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))
                for x in range(rows):
                    new_vec = []
                    for y in range(tiles_per_row):        
                        loaded_object = pickle.load(infile)
                        new_unit, new_structure, new_ore = None, None, None
                        if loaded_object["Unit"]:  
                            new_unit = Units.Unit(loaded_object["Unit"]["Name"],
                                                    loaded_object["Unit"]["Position"],
                                                    loaded_object["Unit"]["Owner"]
                                                    )

                        if loaded_object["Structure"]:
                            new_structure = Structures.Structure(loaded_object["Structure"]["Name"],
                                                    loaded_object["Structure"]["Position"],
                                                    loaded_object["Structure"]["Owner"]
                                                    )

                        if loaded_object["Ore"]:
                            new_ore = Ores.Ore(loaded_object["Ore"]["Position"],
                                                    loaded_object["Ore"]["Name"],
                                                    loaded_object["Ore"]["Tier"]
                                                    )

                        new_tile = TileClass.Tile(loaded_object["Position"],
                                                    loaded_object["Collidable"],
                                                    loaded_object["Image_name"],
                                                    new_ore,
                                                    new_unit,
                                                    new_structure
                                                    )

                        #Save controlling units and structures
                        if new_tile.structure != None: 
                            #Center camera to player's Kernel at the start of the game.
                            if new_tile.structure.name == "Kernel" and new_tile.structure.owner == map_locations[Pozitie]:
                                CurrentCamera.x = new_tile.structure.position[0] * current_tile_length - WIDTH // 2
                                CurrentCamera.y = new_tile.structure.position[1] * current_tile_length - HEIGHT // 2
                                CurrentCamera.Check_Camera_Boundaries()

                            if new_tile.structure.owner == map_locations[Pozitie]:
                                controllables_vec.append(new_tile.structure)

                        if new_tile.unit != None:
                            if new_tile.unit.owner == map_locations[Pozitie]:
                                controllables_vec.append(new_tile.unit)

                        new_vec.append(new_tile)
                    tiles.append(new_vec)

            determine_visible_tiles()

            for x in range(rows):  #Redraw the whole map
                for y in range(tiles_per_row):
                    tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length), False, (visible_tiles, partially_visible_tiles))
                #tiles.append(newLine)

            nonlocal mapSurface
            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

        except:
            print("No such file exists")

    #functia asta face refresh la harta 
    def refresh_map(specific_vector = None):
        nonlocal mapSurface

        if specific_vector != None:    #If an array is given to the function, update only the tiles inside said function. The positions are (x,y)
            for pos in specific_vector:
                tiles[pos[1]][pos[0]].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length), False, (visible_tiles, partially_visible_tiles))
            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))
            return

        if TileClass.full_bright == True : 
            for x in range(rows):  #Redraw the whole map
                for y in range(tiles_per_row):
                    tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length), False, (visible_tiles, partially_visible_tiles))

        else:
            for pos in partially_visible_tiles:
                tiles[pos[1]][pos[0]].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length), False, (visible_tiles, partially_visible_tiles))

        mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

    def draw_enlighted_tiles(create = False):
        if create == False:
            enlighted_surface = None
            return enlighted_surface

        enlighted_surface = pygame.Surface((int(tiles_per_row * current_tile_length), int(rows * current_tile_length))).convert_alpha()
        enlighted_surface.fill((0,0,0,0))

        light_percent = .20 #Percentage of full white to use on movable tiles

        light = pygame.Surface((current_tile_length, current_tile_length)).convert_alpha()
        light.fill((0,204,0, light_percent * 255))

        for pos in path_tiles:
            enlighted_surface.blit(light, (pos[0] * current_tile_length, pos[1] * current_tile_length))
        return enlighted_surface

    load_map(map_name)
    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

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
                #modifecarea pozitiilor de pe harta si stergerea cladirilor
                colorTable[map_locations[Coduri_pozitie_client[Killed_Clients[0]] + 1]] = None
                TileClass.colorTable = colorTable
                refresh_map()
                map_locations.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1 )
                #modificarea turelor
                if Whos_turn == Coduri_pozitie_client[Killed_Clients[0]] + 1 :
                    timer = turn_time
                    if Whos_turn >= len(playeri) :
                        Whos_turn = 0
                elif Whos_turn > Whos_turn == Coduri_pozitie_client[Killed_Clients[0]] + 1 :
                    Whos_turn -= 1
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
            #In celelalte stagii (lobby, map_select) nu a fost nevoie de acest vector care are scopul sa se ocupe de schimbarile care provin de la clienti care trebe 
            #sa fie executate consecutiv ca sa nu interfereze intre ele
            while len(Changes_from_clients) > 0 :
                if Changes_from_clients[0][0] == "new_message" :
                    archive_message(Changes_from_clients[0][1],Changes_from_clients[0][2],Changes_from_clients[0][3])
                elif Changes_from_clients[0][0] == "Force_end_turn" :
                    timer = 0
                elif Changes_from_clients[0][0] == "move_unit" :
                    tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit = tiles[Changes_from_clients[0][1][1]][Changes_from_clients[0][1][0]].unit
                    tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit.position = tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].position

                    del tiles[Changes_from_clients[0][1][1]][Changes_from_clients[0][1][0]].unit
                    tiles[Changes_from_clients[0][1][1]][Changes_from_clients[0][1][0]].unit = None

                    refresh_map([Changes_from_clients[0][1], Changes_from_clients[0][2]])
                Changes_from_clients.pop(0)
        else :
            #Se verifica daca serverul a trimis lucruri spre acest client
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "leftplayer" :
                    playeri.pop(Changes_from_server[0][1])
                    #modifecarea pozitiilor de pe harta si stergerea cladirilor
                    colorTable[map_locations[Changes_from_server[0][1]]] = None
                    TileClass.colorTable = colorTable
                    refresh_map()
                    map_locations.pop(Changes_from_server[0][1] )
                    #modificarea turelor
                    if Whos_turn == Changes_from_server[0][1] :
                        timer = turn_time
                        if Whos_turn >= len(playeri) :
                            Whos_turn = 0
                    elif  Whos_turn >= Changes_from_server[0][1] :
                        Whos_turn -= 1
                    if Changes_from_server[0][1] < Pozitie :
                        Pozitie -= 1 
                elif Changes_from_server[0][0] == "a second passed" :
                    timer = timer - 1
                elif Changes_from_server[0][0] == "next_turn" :
                    next_turn = True
                elif Changes_from_server[0][0] == "new_message" :
                    archive_message(Changes_from_server[0][1],Changes_from_server[0][2],Changes_from_server[0][3])
                elif Changes_from_server[0][0] == "Force_end_turn" :
                    timer = 0
                elif Changes_from_server[0][0] == "move_unit" :
                    tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit = tiles[Changes_from_server[0][1][1]][Changes_from_server[0][1][0]].unit
                    tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit.position = tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].position

                    del tiles[Changes_from_server[0][1][1]][Changes_from_server[0][1][0]].unit
                    tiles[Changes_from_server[0][1][1]][Changes_from_server[0][1][0]].unit = None

                    refresh_map([Changes_from_server[0][1], Changes_from_server[0][2]])

                Changes_from_server.pop(0)

        if timer == 0 :
            determine_visible_tiles()

            for unit in controllables_vec:  #Allow each unit to make an action
                if tiles[unit.position[1]][unit.position[0]].unit == unit:
                    unit.canMove = True
                    unit.canAttack = True

            if Role == "host" :
                if Confirmatii_timer == len(CLIENTS) :
                    #daca e tura hostului,trimite toate schimbarile facute.
                    if Whos_turn == Pozitie :
                        if Whos_turn == Pozitie :
                            for i in range(len(Turn_Actions)) :
                                Transmit_to_all.append((Turn_Actions[i],None))
                            Turn_Actions = []
                    #transmite la toti ca se schimba tura
                    Transmit_to_all.append((("next_turn",None),None))
                    #se schimba cel care joaca
                    Whos_turn += 1 
                    if Whos_turn == len(playeri) :
                        Whos_turn = 0
                    timer = turn_time
                    Confirmatii_timer = 0
                    if TileClass.full_bright == False :
                        refresh_map()
            else :
                if timer_notification_sent == False :
                    #Daca era tura clientului se trimit schimbarile
                    if Whos_turn == Pozitie :
                        for i in range(len(Turn_Actions)) :
                            data_send = pickle.dumps(Turn_Actions[i])
                            data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                            Connection.send(data_send)
                        Turn_Actions = []
                    #Se trimite confirmarea ca a ajuns timerul la zero
                    data_send = pickle.dumps(("timer is zero",None))
                    data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                    Connection.send(data_send)
                    timer_notification_sent = True
                elif next_turn == True :
                    #se schimba cel care joaca
                    Whos_turn += 1 
                    if Whos_turn == len(playeri) :
                        Whos_turn = 0
                    timer = turn_time
                    timer_notification_sent = False
                    next_turn = False
                    if TileClass.full_bright == False :
                        refresh_map()


        #The event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN  :
                press_coordonaits = event.pos 
                #daca apesi click stanga
                if event.button == 1 :
                    #Se verifica daca apasa butonul de chat
                    if press_coordonaits[1] <= 75  and press_coordonaits[0] >= WIDTH -75 :
                        if Chat_window == False :
                            Chat_window = True
                            chat_notification = False
                            selected_tile = [None,None]
                            tile_empty = False
                        else :
                            Chat_window = False
                            writing_in_chat = False
                            message = ""
                            chat_scroll = 0
                    #se verifica daca interactioneaza cu chat boxul
                    if Chat_window == True :
                        if press_coordonaits[0] < (WIDTH-260)/2 + 265 :
                            Chat_window = False
                            writing_in_chat = False
                            message = ""
                            chat_scroll = 0
                        elif press_coordonaits[1] >= HEIGHT - 50 and press_coordonaits[0] >= (WIDTH-260)/2 + 265 :
                            writing_in_chat = True
                        else :
                            writing_in_chat = False
                    #Detecteaza daca a apapasat butonul de End Turn
                    pygame.draw.rect(WIN,Player_Colors[playeri[Whos_turn][1]],((WIDTH-260)/2,HEIGHT*2/25 + 5,260,35))
                    if Whos_turn == Pozitie and press_coordonaits[0]>(WIDTH-260)/2 and press_coordonaits[0]<(WIDTH-260)/2 +260 and press_coordonaits[1]>HEIGHT*2/25 and press_coordonaits[1]<HEIGHT*2/25 + 40 :
                        timer = 0 
                        if Role == "host" :
                            Transmit_to_all.append((("Force_end_turn",None),None))
                        else :
                            data_send = pickle.dumps(("Force_end_turn",None))
                            data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                            Connection.send(data_send)
                    #detecteaza daca playeru apasa un tile vizibil
                    if (press_coordonaits[1] > HEIGHT/25 and (press_coordonaits[1] > HEIGHT*2/3 and press_coordonaits[0] < HEIGHT/3)==0) and ((press_coordonaits[0]<(WIDTH-260)/2 + 260 and Chat_window == True) or Chat_window == False) and( selected_tile[0]==None or (press_coordonaits[1] < HEIGHT*4/5-5 and (tile_empty==False or (press_coordonaits[0]>WIDTH-HEIGHT/3 and press_coordonaits[1]>HEIGHT*2/3-60)==0 ))) :
                        x_layer = (press_coordonaits[0] + CurrentCamera.x) // current_tile_length 
                        y_layer = (press_coordonaits[1] + CurrentCamera.y) // current_tile_length
                        if x_layer >= 0 and x_layer < tiles_per_row:
                            if y_layer >= 0 and y_layer < rows:
                                enlighted_surface = draw_enlighted_tiles()
                                if selected_tile[0] == None or (selected_tile[0] == x_layer and selected_tile[1] == y_layer)==0 : 
                                    selected_tile = [x_layer,y_layer]
                                    if tiles[y_layer][x_layer].structure == None and tiles[y_layer][x_layer].unit == None and tiles[y_layer][x_layer].collidable == False :
                                        if tile_empty != True :
                                            tile_empty = True
                                            Element_selectat = None
                                        if tiles[y_layer][x_layer].ore != None :
                                            construction_tab = "Mines"
                                        else :
                                            construction_tab = "Structures"
                                    else : 
                                        tile_empty=False
                                        #daca tile_ul are o strucutra sau unitate ii salveaza imaginea pentru afisare
                                        if tiles[selected_tile[1]][selected_tile[0]].unit != None :
                                            unit =  tiles[selected_tile[1]][selected_tile[0]].unit
                                            large_img_element_afisat = pygame.image.load('Assets/Units/' + unit.texture)
                                            #colorarea imagini si transformarea acesteia
                                            for i in range(large_img_element_afisat.get_width()):
                                                for j in range(large_img_element_afisat.get_height()):
                                                    if large_img_element_afisat.get_at((i,j)) == (1,1,1):
                                                        large_img_element_afisat.set_at((i,j), colorTable[unit.owner])
                                            large_img_element_afisat = pygame.transform.scale(large_img_element_afisat,(HEIGHT/5 -50,HEIGHT/5 -50))
                                        elif tiles[selected_tile[1]][selected_tile[0]].structure != None :
                                            structure =  tiles[selected_tile[1]][selected_tile[0]].structure
                                            large_img_element_afisat = pygame.image.load('Assets/Structures/' + structure.texture)
                                            #colorarea imagini si transformarea acesteia
                                            for i in range(large_img_element_afisat.get_width()):
                                                for j in range(large_img_element_afisat.get_height()):
                                                    if large_img_element_afisat.get_at((i,j)) == (1,1,1):
                                                        large_img_element_afisat.set_at((i,j), colorTable[structure.owner])
                                            large_img_element_afisat = pygame.transform.scale(large_img_element_afisat,(HEIGHT/5 -50,HEIGHT/5 -50))

                                    if tiles[y_layer][x_layer].unit != None and tiles[y_layer][x_layer].unit.owner == map_locations[Pozitie] and (x_layer, y_layer) in visible_tiles:
                                        selected_controllable = tiles[y_layer][x_layer].unit
                                        if selected_controllable.canMove == True:
                                            determine_enlighted_tiles()
                                            enlighted_surface = draw_enlighted_tiles(True)
                                else :
                                    selected_tile = [None,None]

                    #detecteaza daca playeru a schimbat coinstruction tabul
                    elif press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] <= HEIGHT*2/3 -5 and press_coordonaits[1] >= HEIGHT*2/3 -55 :
                        Element_selectat = None
                        construction_tab_scroll = 0
                        if construction_tab == "Structures" :
                            construction_tab = "Units"
                        elif construction_tab == "Units" :
                            construction_tab = "Structures"
                    #detecteaza daca playerul a apasat un element din construction_tab
                    elif press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3 :
                        if construction_tab == "Structures" :
                            elements = len(structures)
                        else :
                            elements = len(units)
                        for i in range(math.ceil(elements/3)) :
                             y_rand = HEIGHT*2/3 +5 + i*70 + i*10 - C_menu_scroll
                             if y_rand + 70 > HEIGHT*2/3 :
                                 if press_coordonaits[1] >= y_rand and press_coordonaits[1] <= y_rand+70 :
                                     for j in range(min(3,elements-i*3)) :
                                         x_coloana = WIDTH-HEIGHT/3+10 + j*70 + j*spatiu_intre
                                         if press_coordonaits[0] >= x_coloana and press_coordonaits[0] <= x_coloana + 70 :
                                             Element_selectat = i*3 + j
                                             if construction_tab == "Structures" :
                                                large_img_element_afisat = pygame.transform.scale(structures[Element_selectat],(HEIGHT/5 -50,HEIGHT/5 -50))
                                             else :
                                                large_img_element_afisat = pygame.transform.scale(units[Element_selectat],(HEIGHT/5 -50,HEIGHT/5 -50))
                                             #break
                                     break

                #daca apesi click dreapta 
                if event.button == 3:
                    #daca ai o unitate selectata, incearca sa o muti  daca este tura playerului
                    if selected_controllable != None and timer>0 and Whos_turn == Pozitie :
                        if (press_coordonaits[1] > HEIGHT/25 and (press_coordonaits[1] > HEIGHT*2/3 and press_coordonaits[0] < HEIGHT/3)==0) and ((press_coordonaits[0]<(WIDTH-260)/2 + 260 and Chat_window == True) or Chat_window == False) and( selected_tile[0]==None or (press_coordonaits[1] < HEIGHT*4/5-5 and (tile_empty==False or (press_coordonaits[0]>WIDTH-HEIGHT/3 and press_coordonaits[1]>HEIGHT*2/3-60)==0 ))) :
                            x_layer = (press_coordonaits[0] + CurrentCamera.x) // current_tile_length 
                            y_layer = (press_coordonaits[1] + CurrentCamera.y) // current_tile_length
                            if x_layer >= 0 and x_layer < tiles_per_row:
                                if y_layer >= 0 and y_layer < rows:
                                    lastPos = selected_controllable.position
                                    hasMoved = selected_controllable.MoveTo((x_layer, y_layer), path_tiles, tiles)
                                    #If the unit has moved, delete the unit from last position tile and redraw those 2 tiles.
                                    if hasMoved:
                                        selected_controllable = None
                                        path_tiles.clear()

                                        del tiles[lastPos[1]][lastPos[0]].unit
                                        tiles[lastPos[1]][lastPos[0]].unit = None

                                        refresh_map([(x_layer, y_layer), lastPos])

                                        enlighted_surface = draw_enlighted_tiles()

                                        #Pune aceasta actiune in Turn-Actions
                                        Turn_Actions.append(("move_unit",lastPos,(x_layer, y_layer)))
                #daca dai scrol in sus
                if event.button == 4 :
                    if Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265 and len(chat_archive) > 30 :
                        chat_scroll = chat_scroll +1
                        if chat_scroll > len(chat_archive) - 31:
                            chat_scroll = len(chat_archive) - 31
                    elif press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3  :
                        construction_tab_scroll = construction_tab_scroll + 1
                        if construction_tab == "Structures" and construction_tab_scroll > math.ceil(len(structures)/3) -3 :
                            construction_tab_scroll = math.ceil(len(structures)/3) -3
                        elif construction_tab == "Units" and construction_tab_scroll > math.ceil(len(units)/3) -3 :
                            construction_tab_scroll = math.ceil(len(units)/3) -3
                        if construction_tab_scroll < 0:
                            construction_tab_scroll = 0
                        
                #daca dai scrol in jos
                elif event.button == 5 :
                    if Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265 :
                        chat_scroll = chat_scroll - 1
                        if chat_scroll < 0 :
                            chat_scroll = 0
                    elif press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3  :
                        construction_tab_scroll = construction_tab_scroll - 1
                        if construction_tab_scroll < 0 :
                            construction_tab_scroll = 0

                #Zoom si check_boundary pentru camera.
                modifier = 0
                if (Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265) == 0 and (press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3 and selected_tile[0] !=None and tile_empty == True) == 0 :
                    if event.button == 4:
                        modifier = 1
                    elif event.button == 5:
                        modifier = -1
               
                last_map_size_x = current_tile_length * tiles_per_row
                last_map_size_y = current_tile_length * rows

                #Update the zoom and tile length
                CurrentCamera.zoom += 0.1 * modifier
                CurrentCamera.Update_Camera_Zoom_Level()
                current_tile_length = int(normal_tile_length * CurrentCamera.zoom)

                map_size_x = current_tile_length * tiles_per_row
                map_size_y = current_tile_length * rows

                CurrentCamera.Check_Camera_Boundaries()
                CurrentCamera.Calculate_After_Zoom_Position(last_map_size_x, map_size_x, last_map_size_y, map_size_y)

                try:
                    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))
                    if enlighted_surface != None:
                        enlighted_surface = pygame.transform.scale(enlighted_surface, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))
                except:     #if that failed, the surface is too big.
                    print("Can't zoom in further")

            elif event.type == pygame.KEYDOWN :
                #Daca scrie in chat

                if writing_in_chat == False:
                    if event.key == pygame.K_z and event.mod & pygame.KMOD_CTRL :
                        if Ctrl_zeed == False and Whos_turn == Pozitie and timer >0 :
                            Ctrl_zeed = True 
                            #Se da reverse la ultima actiune luata in Tura playerului
                            if len(Turn_Actions) > 0 :
                                reverse_action(Turn_Actions[-1])
                                Turn_Actions.pop(-1)

                    elif event.unicode.lower() == 'l':  #Enable/Disable GUIs
                        #GUI.GUIs_enabled = not GUI.GUIs_enabled      
                        print("GUI disable not implemented yet. Sorry") 

                if writing_in_chat == True and event.key != pygame.K_TAB :
                    if event.key == pygame.K_ESCAPE :
                        writing_in_chat = False
                    elif event.key == pygame.K_DELETE :
                        message = ""
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER :
                        test = message.split()
                        if len(test) > 0:
                            if Role == "host" :
                                archive_message(message,playeri[Pozitie][0],Player_Colors[playeri[Pozitie][1]])
                                Transmit_to_all.append((("new_message",message,playeri[Pozitie][0],Player_Colors[playeri[Pozitie][1]]),None))
                            else :
                                data_send = pickle.dumps(("new_message",message,playeri[Pozitie][0],Player_Colors[playeri[Pozitie][1]]))
                                data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                                Connection.send(data_send)
                            message = ""
                    elif event.key == pygame.K_BACKSPACE  :
                        message = message[:-1]
                    elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL :
                        message += ((pygame.scrap.get(pygame.SCRAP_TEXT)).decode()[:-1])
                    else : 
                        message += event.unicode

            if pygame.key.get_pressed()[pygame.K_z]==False :
                Ctrl_zeed = False

        x_pos = pygame.mouse.get_pos()[0]
        y_pos = pygame.mouse.get_pos()[1]

        if x_pos == 0:
            CurrentCamera.x -= CurrentCamera.camera_movement
        if y_pos == 0:
            CurrentCamera.y -= CurrentCamera.camera_movement
        if x_pos == WIDTH - 1:
            CurrentCamera.x += CurrentCamera.camera_movement
        if y_pos == HEIGHT - 1:
            CurrentCamera.y += CurrentCamera.camera_movement

        CurrentCamera.Check_Camera_Boundaries()


    #finalul functiei si returnarea variabilelor necesare care s-ar fi putut schimba
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        return playeri,Pozitie 