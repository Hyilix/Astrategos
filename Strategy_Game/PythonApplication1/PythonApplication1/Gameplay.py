import pygame 
import os 
import socket
import pickle
import threading
import time

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

HEADERSIZE = 10
SPACE = "          "
Font = pygame.font.Font(None, 30)

run = True
timer = 120

Confirmatii_timer = 0
chat_notification = False

screen = pygame.display.Info()

rows = 40
tiles_per_row = 40

tiles = []

#De stiut map_position este un nr de la 1 la 4 care reprezinta ce pozitie ii apartine acestei instante pe harta
def gameplay (WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client,map_name,map_position) :
    global run
    global timer 
    global Confirmatii_timer
    global chat_notification

    WIN.fill((255,255,255))
    pygame.display.update()

    #adresa pentru txt-ul hartii pe care se afla playeri
    map_adres = "Maps\info" + map_name + ".txt"


    chat_icon = pygame.transform.scale(pygame.image.load('Assets/Gameplay_UI/chatbox-icon.png'),(60,60))


    def draw_window () :
        WIN.fill((255,255,255))

        #Draw map
        tempSurface = pygame.Surface((WIDTH, HEIGHT))
        tempSurface.blit(mapSurface, (0, 0), (CurrentCamera.x, CurrentCamera.y, WIDTH, HEIGHT))

        WIN.blit(tempSurface, (0, 0)) 

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
        #butonul de chat din dreapta sus
        pygame.draw.rect(WIN,(25,25,25),(WIDTH-80,0,80,80))
        pygame.draw.rect(WIN,(225, 223, 240),(WIDTH-75,0,75,75))
        WIN.blit(chat_icon,(WIDTH - 68,8))
        if chat_notification == True :
            pygame.draw.circle(WIN,Red,(WIDTH-10,20),8)
        #Partea de jos a UI-ului
        # draw mini_map part
        pygame.draw.rect(WIN,(25,25,25),(0,HEIGHT-300,300,300))
        
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

    CurrentCamera = Camera((0,0), 1, 3, 0.4)

    normal_tile_length = int(TileClass.base_texture_length * (WIDTH / HEIGHT))     #the length of a tile when the zoom is 1
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
                        new_unit, new_structure = None, None
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

                        new_tile = TileClass.Tile(loaded_object["Position"],
                                                    loaded_object["Collidable"],
                                                    None,     #Image Class
                                                    loaded_object["Image_name"],
                                                    None,     #Special
                                                    new_unit,
                                                    new_structure
                                                    )

                        new_vec.append(new_tile)
                    tiles.append(new_vec)

            for x in range(rows):  #Redraw the whole map
                for y in range(tiles_per_row):
                    tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                #tiles.append(newLine)

            nonlocal mapSurface
            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

        except:
            print("No such file exists")

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
                Changes_from_clients.pop(0)
        else :
            #Se verifica daca serverul a trimis lucruri spre acest client
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "leftplayer" :
                    playeri.pop(Changes_from_server[0][1])
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
                Changes_from_server.pop(0)

        if timer == 0 :
            if Role == "host" :
                if Confirmatii_timer == len(CLIENTS) :
                    Transmit_to_all.append((("next_turn",None),None))
                    #se schimba cel care joaca
                    Whos_turn += 1 
                    if Whos_turn == len(playeri) :
                        Whos_turn = 0
                    timer = turn_time
                    Confirmatii_timer = 0
            else :
                if timer_notification_sent == False :
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
                #daca dai scrol in sus
                if event.button == 4 :
                    if Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265 and len(chat_archive) > 30 :
                        chat_scroll = chat_scroll +1
                        if chat_scroll > len(chat_archive) - 31:
                            chat_scroll = len(chat_archive) - 31
                        
                #daca dai scrol in jos
                elif event.button == 5 :
                    if Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265 :
                        chat_scroll = chat_scroll - 1
                        if chat_scroll < 0 :
                            chat_scroll = 0

                #Zoom si check_boundary pentru camera.
                modifier = 0
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
                #TODO: Make a way to zoom in/out with minimal lag. This method is very bad but for now it works... kinda.
                #Apparently it works well with low texture sizes.
                try:
                    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))
                except:     #if that failed, the surface is too big.
                    print("Can't zoom in further")

            elif event.type == pygame.KEYDOWN :
                #Daca scrie in chat

                if writing_in_chat == False:
                    if event.unicode.lower() == 'p':    #Enable/Disable simple textures
                        TileClass.simple_textures_enabled = not TileClass.simple_textures_enabled

                        for x in range(rows):  #Redraw the whole map
                            for y in range(tiles_per_row):
                                tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))

                        mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

                    elif event.unicode.lower() == 'l':  #Enable/Disable GUIs
                        #GUI.GUIs_enabled = not GUI.GUIs_enabled      
                        print("No GUIs implemented for gameplay yet") 

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

