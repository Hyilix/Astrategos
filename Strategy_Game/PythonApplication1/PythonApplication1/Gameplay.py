from ast import Delete
from ctypes import Structure
from select import select
from tkinter.messagebox import showerror
from turtle import left
import pygame 
import os 
import socket
import pickle
import threading
import time
import math
import os
import random
import copy

import TileClass
import Structures
import Units
import Ores
from button import Button
import Node

pygame.init()

music_path = 'Assets/Music/'
music_vec = []

sounds_vec = [] #0 -> any turn, 1 -> your turn

for music in os.listdir(music_path):
    music_vec.append(music)

for sound in os.listdir('Assets/Sounds/'):
    sounds_vec.append(sound)

global SOUND_VOLUME
SOUND_VOLUME = 0.4

global VOLUM
VOLUM = 50

def PlayTurnSound(index):
    my_sound = pygame.mixer.Sound('Assets/Sounds/' + sounds_vec[index])
    my_sound.set_volume(SOUND_VOLUME)
    my_sound.play()

def PlayRandomMusic():
    rand = random.randint(0, len(music_vec) - 1)
    pygame.mixer.music.load(music_path + music_vec[rand])
    pygame.mixer.music.set_volume(VOLUM / 100)
    pygame.mixer.music.play()

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

camerabox_color = (192,192,192)

def RemoveObjectFromList(obj, ls):
    for i, o in enumerate(ls):
        if o.position == obj.position and type(o) == type(obj):
            del ls[i]
            break

colorTable = {  #Table for assigning each controller with a color. If "None", then don't draw
    0 : (64,64,64),
    1 : None,
    2 : None,
    3 : None,
    4 : None
    }

HEADERSIZE = 10
SPACE = "          "
Font = pygame.font.SysFont("Times New Roman.ttf", 30)
FontT = pygame.font.SysFont("Times New Roman.ttf", 50)

run = True
timer = 120
tile_empty = False

Confirmatii_timer = 0
chat_notification = False

screen = pygame.display.Info()

rows = 40
tiles_per_row = 40

tiles = []

controllables_vec = []  #Vector containing units and structures.
caster_controllables_vec = []   #Vector containing units and structures that call a function at each end of turn

visible_tiles = []
partially_visible_tiles = []
path_tiles = [] #Tiles that a selected unit can move to

DEBUG_FORCED_POSITION = None

lastPositionForRendering = None

SWAP_TO_NORMAL = pygame.USEREVENT + 1   #event for refreshing the map after some time when a thing was hit.

canRenderMinimap = True

global left_click_holding
left_click_holding = False

def draw_star(length, y, x, TrueSight = False):    #Determine what tiles the player currently sees.
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
                stop = False

            if (y, x) not in visited_vec:
                if x >= 0 and y >= 0 and y < rows and x < tiles_per_row and (stop == False or First == True):
                    checks += 1
                    visited_vec.append((y, x))
                    if (x, y) not in visible_tiles: visible_tiles.append((x, y))
                    if (x, y) not in partially_visible_tiles: partially_visible_tiles.append((x, y))

                    if First != True:
                        if tiles[y][x].unit != None or tiles[y][x].structure != None or tiles[y][x].ore != None:
                            continue

                    for direction in directions:
                        in_x = direction[0]
                        in_y = direction[1]
                        if (y + in_y, x + in_x) not in visited_vec:
                            if TrueSight == True:
                                new_tiles.append((y + in_y, x + in_x))
                            else:
                                if tiles[y][x].collidable == False:
                                    new_tiles.append((y + in_y, x + in_x))
                                    First = False
                            
                                elif tiles[y][x].collidable == True and y + in_y >= 0 and x + in_x >= 0 and y + in_y < rows and x + in_x < tiles_per_row and tiles[y + in_y][x + in_x].collidable == False and tiles[y + in_y][x + in_x].unit == None and tiles[y + in_y][x + in_x].structure == None and tiles[y + in_y][x + in_x].ore == None:
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
            if type(obj) == Structures.Structure:
                if obj.TrueSight == True:
                    draw_star(obj.fog_range, obj.position[1], obj.position[0], True)
                    continue

            draw_star(obj.fog_range, obj.position[1], obj.position[0])

selected_controllable = None
enlighted_surface = None
minimap_surface = None
fake_minimap_surface = None     #Surface to store a rectangle to show where you are looking currently

#De stiut map_locations este un vector de aceasi lungime cu vectorul de playeri care contine locatia de pe hart a fiecaruia reprezentata printr-un nr de la 1 la 4
def gameplay (WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client,map_name,map_locations) :
    if DEBUG_FORCED_POSITION != None:
        map_locations[Pozitie] = DEBUG_FORCED_POSITION

    TileClass.show_walls = False
    global run
    global timer 
    global tile_empty
    global Confirmatii_timer
    global chat_notification
    global colorTable
    global selected_controllable
    global enlighted_surface
    global minimap_surface
    global fake_minimap_surface
    global canRenderMinimap
    global lastPositionForRendering
    global tiles
    lastPositionForRendering = None
    canRenderMinimap = True
    run=True
    global VOLUM
    VOLUM = 50

    left_click_holding = False

    controllables_vec.clear()
    caster_controllables_vec.clear()

    visible_tiles.clear()
    partially_visible_tiles.clear()
    path_tiles.clear()

    can_build = False
    SHOW_UI = True 

    selected_controllable = None
    enlighted_surface = None
    minimap_surface = None
    fake_minimap_surface = None     #Surface to store a rectangle to show where you are looking currently

    minimap_surface = pygame.Surface((HEIGHT // 3, HEIGHT // 3)).convert_alpha()
    enlighted_surface = None
    fake_minimap_surface = pygame.Surface((HEIGHT // 3, HEIGHT // 3)).convert_alpha()

    def draw_minimap():
        sizeY = int(HEIGHT / 3 * HEIGHT / current_tile_length / rows)
        sizeX = int(HEIGHT / 3 * WIDTH / current_tile_length / tiles_per_row)
        global canRenderMinimap
        global fake_minimap_surface
        ratio = int((HEIGHT // 3) / max(rows, tiles_per_row))
        fake_minimap_surface.fill((0,0,0,0))
        pygame.draw.rect(fake_minimap_surface, camerabox_color, (int(CurrentCamera.x / 3 * HEIGHT / current_tile_length / tiles_per_row), int(CurrentCamera.y / 3 * HEIGHT / current_tile_length / rows), sizeX, sizeY), 3)
        if canRenderMinimap == True:
            minimap_surface.fill((50,50,50,110))

            for tile in partially_visible_tiles:
                tiles[tile[1]][tile[0]].DrawImage(minimap_surface, (ratio, ratio), True, (visible_tiles, partially_visible_tiles))
            canRenderMinimap = False

            return True
        return False

    def draw_path_star(length, y, x):
        visited_vec = []
        queued_tiles = [(y,x)]

        directions = [
            (-1,0),
            (1,0),
            (0,1),
            (0,-1)
        ]

        or_x = x
        or_y = y

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
                                if tiles[y][x].structure == None or (y == or_y and x == or_x):
                                    if Y >= 0 and X >= 0 and Y < rows and X < tiles_per_row:
                                        if tiles[Y][X].collidable == False and (tiles[Y][X].structure == None or (tiles[Y][X].structure.owner == map_locations[Pozitie] and tiles[Y][X].structure.canShareSpace == True)) and tiles[Y][X].ore == None and tiles[Y][X].unit == None:
                                            new_tiles.append((y + in_y, x + in_x))

            queued_tiles.clear()

            if len(new_tiles) == 0: isDone = True

            queued_tiles += new_tiles
            length -= 1

        visited_vec.clear()
        queued_tiles.clear()

    def determine_enlighted_tiles():
        if timer > 0 and Whos_turn == Pozitie:
            path_tiles.clear()
            draw_path_star(selected_controllable.move_range, selected_controllable.position[1], selected_controllable.position[0])

    colorTable = {  #Remake the dictionary
    0 : (64,64,64),
    1 : None,
    2 : None,
    3 : None,
    4 : None
    }

    TileClass.full_bright = False #if full_bright == True, player can see the whole map at any time, like in editor.

    index = 0
    for player in playeri:  #assign colors to structures and units. Any structure/unit with 
        colorTable[map_locations[index]] = Player_Colors[player[1]]
        index += 1
    TileClass.colorTable = colorTable
    del index

    WIN.fill((255,255,255))
    pygame.display.update()


    chat_icon = pygame.transform.scale(pygame.image.load('Assets/Gameplay_UI/chatbox-icon.png'),(60,60))
    mithril_icon = pygame.transform.scale(pygame.image.load('Assets/Gameplay_UI/mars-mithril-bar-1.png'),(32,32))
    flerovium_icon = pygame.transform.scale(pygame.image.load('Assets/Gameplay_UI/mars-flerovium-crystal-1.png'),(32,32))
    man_power_icon = pygame.transform.scale(pygame.image.load('Assets/Units/Marine.png'),(32,32))
    nodes_icon = pygame.transform.scale(pygame.image.load('Assets/Structures/Node.png'),(32,32))

    #butonul de creare a unei cladiri/unitati
    x_b =HEIGHT/3 + 50 + HEIGHT/5 -50 + (WIDTH - HEIGHT*2/3 -25 -HEIGHT/5 +50)/2 - 185/2
    ButtonC_rect = (x_b,HEIGHT-95,185,70)
    Create_Button = Button((x_b+5,HEIGHT-90,175,60),Gri,None,**{"text": "Recruit","font": FontT})
    #butonul de repair si refund
    x_b = HEIGHT/3 + 50 + HEIGHT/5 -50 + (WIDTH - HEIGHT/3 -25 -HEIGHT/5 +50)/2 - 185/2
    ButtonR_rect = (x_b,HEIGHT-95,186,70)
    Refund_Button = Button((x_b+5,HEIGHT-90,175,60),Gri,None,**{"text": "Refund","font": FontT})
    refund_bool = False
    Repair_Button = Button((x_b+5,HEIGHT-90,175,60),Gri,None,**{"text": "Repair","font": FontT})
    repair_bool = False
    aford_repair = False
    #Escape Button
    l_emp = 600
    Escape_menu_part = (WIDTH/2-250,HEIGHT/2-l_emp/2, 500,l_emp)
    ButtonE_rect = (WIDTH/2-155,Escape_menu_part[1]+Escape_menu_part[3] - 160 -25,310,160)
    if Role == "host" :
        Escape_Button = Button((WIDTH/2-150,Escape_menu_part[1]+Escape_menu_part[3] - 160 -20,300,150),Gri,None,**{"text": "Return to lobby","font": FontT})
    else :
        Escape_Button = Button((WIDTH/2-150,Escape_menu_part[1]+Escape_menu_part[3] - 160 -20,300,150),Gri,None,**{"text": "Disconect","font": FontT})
    #music slider
    music_text = FontT.render("Music Volume",True,(0,0,0)) 
    music_text_rect = music_text.get_rect()
    music_text_rect.center = (WIDTH/2,Escape_menu_part[1] + 25 +music_text_rect[3]/2)
    slider_rect = [WIDTH/2 - 12,music_text_rect[1]+music_text_rect[3]+10,24,55]
    VOLUM = 50
    #buton next song 
    ButtonN_rect = (ButtonE_rect[0],ButtonE_rect[1]-160-25,310,160)
    Next_Button = Button((ButtonE_rect[0]+5,ButtonE_rect[1]-160-20,300,150),Gri,PlayRandomMusic,**{"text": "(M)Next Song","font": FontT})
    # incaracarea imaginilor structurilor si unitatilor care le poate produce playeru, cu culoarea specifica.
    grosime_outline = 5
    spatiu_intre = (HEIGHT/3 - 5 - 70*3)/3
    C_menu_scroll = 0
    Element_selectat = None
    large_img_element_afisat = None

    structures = []
    s_names = []
    directory = "Assets\Structures"
    for filename in os.listdir(directory):
        if  filename[:-4] != "Kernel" :
            s_names.append(filename[:-4])
            adres=os.path.join(directory, filename)
            structures.append(pygame.transform.scale(pygame.image.load(adres),(64,64)))
    #colorarea structurilor cu culoarea playerului
    for structure in structures :
        for i in range(structure.get_width()):
            for j in range(structure.get_height()):
                if structure.get_at((i,j)) == (1,1,1):
                    structure.set_at((i,j), Player_Colors[playeri[Pozitie][1]])

    mines = []
    m_names = []
    directory = "Assets\Mines"
    for filename in os.listdir(directory):
        m_names.append(filename[:-4])
        adres=os.path.join(directory, filename)
        mines.append(pygame.transform.scale(pygame.image.load(adres),(64,64)))
    #colorarea structurilor cu culoarea playerului
    for mine in mines :
        for i in range(mine.get_width()):
            for j in range(mine.get_height()):
                if mine.get_at((i,j)) == (1,1,1):
                    mine.set_at((i,j), Player_Colors[playeri[Pozitie][1]])

    units = []
    u_names = []
    directory = "Assets" + '\\' + "Units"
    for filename in os.listdir(directory):
        u_names.append(filename[:-4])
        adres=os.path.join(directory, filename)
        units.append(pygame.transform.scale(pygame.image.load(adres),(64,64)))
    #colorarea unitatilor cu culoarea playerului
    for unit in units :
        for i in range(unit.get_width()):
            for j in range(unit.get_height()):
                if unit.get_at((i,j)) == (1,1,1):
                    unit.set_at((i,j), Player_Colors[playeri[Pozitie][1]])

    def draw_selected_controllable_radius():
        if selected_tile[0] != None:
            examined_struct = tiles[selected_tile[1]][selected_tile[0]].structure
            examined_unit = tiles[selected_tile[1]][selected_tile[0]].unit

            if examined_unit != None and examined_unit in controllables_vec and timer > 0 and Whos_turn == Pozitie:
                if examined_unit.owner == map_locations[Pozitie] and examined_unit.canAttack == True:
                    examined_unit.Draw_AOE(WIN, current_tile_length, (CurrentCamera.x, CurrentCamera.y))

            elif examined_struct != None and examined_struct in controllables_vec:
                if examined_struct.owner == map_locations[Pozitie]:
                    examined_struct.Draw_AOE(WIN, current_tile_length, (CurrentCamera.x, CurrentCamera.y))

    def draw_nodes():
        if selected_tile[0] != None:
            examined_struct = tiles[selected_tile[1]][selected_tile[0]].structure   #Selecting a node structure will draw the whole Tree
            if examined_struct != None and examined_struct in controllables_vec:
                if examined_struct.owner == map_locations[Pozitie]:
                    if examined_struct.name == "Kernel" or examined_struct.name == "Node":
                        node = Node.getNodeFromObj(examined_struct)
                        if node in Node.NodesFound:
                            Node.Draw_tree_circles(Node.TreeRoot, WIN, current_tile_length, (CurrentCamera.x, CurrentCamera.y))

            if Element_selectat != None:    #Selecting an unit/structure in construction tab will draw the whole Tree
                Node.Draw_tree_circles(Node.TreeRoot, WIN, current_tile_length, (CurrentCamera.x, CurrentCamera.y))

    def draw_window () :
        nonlocal ButtonR_rect
        nonlocal refund_bool
        nonlocal repair_bool
        nonlocal aford_repair
        WIN.fill((255,255,255))

        #Draw map
        tempSurface = pygame.Surface((WIDTH, HEIGHT))
        tempSurface.blit(mapSurface, (0, 0), (CurrentCamera.x, CurrentCamera.y, WIDTH, HEIGHT))

        global enlighted_surface
        if timer <= 0 or Whos_turn != Pozitie and enlighted_surface == None:
            enlighted_surface = draw_enlighted_tiles()
            selected_tile_check()

        if enlighted_surface != None:
            tempSurface.blit(enlighted_surface, (0, 0), (CurrentCamera.x, CurrentCamera.y, WIDTH, HEIGHT))

        WIN.blit(tempSurface, (0, 0))

        #Draw Nodes circles
        draw_nodes()
        draw_selected_controllable_radius()
        #draw selected tile outline
        if selected_tile[0] != None : 
            x_tile=selected_tile[0]* current_tile_length - CurrentCamera.x
            y_tile = selected_tile[1]* current_tile_length - CurrentCamera.y
            pygame.draw.rect(WIN,Light_Green,(x_tile,y_tile,current_tile_length,math.ceil(grosime_outline*CurrentCamera.zoom)))
            pygame.draw.rect(WIN,Light_Green,(x_tile,y_tile,math.ceil(grosime_outline*CurrentCamera.zoom),current_tile_length))
            pygame.draw.rect(WIN,Light_Green,(x_tile,y_tile+current_tile_length-math.ceil(grosime_outline*CurrentCamera.zoom),current_tile_length,math.ceil(grosime_outline*CurrentCamera.zoom)))
            pygame.draw.rect(WIN,Light_Green,(x_tile+current_tile_length-math.ceil(grosime_outline*CurrentCamera.zoom),y_tile,math.ceil(grosime_outline*CurrentCamera.zoom),current_tile_length))

        #desenarea Ui - ului 
        if SHOW_UI == True :
            draw_minimap()
            WIN.blit(minimap_surface, (0, HEIGHT - HEIGHT // 3))
            WIN.blit(fake_minimap_surface, (0, HEIGHT - HEIGHT // 3))

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
            if Win_condition == 0 :
                x_coord = 5
                WIN.blit(mithril_icon,(x_coord,(HEIGHT/25-32)/2))
                x_coord = x_coord +32 + 10
                mit_count = Font.render(str(Mithril),True,(75, 91, 248))
                mit_rect = mit_count.get_rect()
                WIN.blit(mit_count,(x_coord,(HEIGHT/25-mit_rect[3])/2))
                x_coord = mit_rect[2] + 10 + x_coord
                fle_count = Font.render(str(Flerovium),True,(152, 65, 182))
                fle_rect = fle_count.get_rect()
                WIN.blit(flerovium_icon,(x_coord,(HEIGHT/25-32)/2))
                x_coord = x_coord + 10 + 32
                WIN.blit(fle_count,(x_coord,(HEIGHT/25-fle_rect[3])/2))
                x_coord = x_coord + fle_rect[2]+10
                man_power_count = Font.render(("  " + str(Man_power_used))[-3:]+' / '+ str(Max_Man_power),True,(0,0,0))
                man_rect = man_power_count.get_rect()
                WIN.blit(man_power_icon,(x_coord,(HEIGHT/25-32)/2))
                x_coord = x_coord + 32 + 10
                WIN.blit(man_power_count,(x_coord,(HEIGHT/25-man_rect[3])/2))
                x_coord = x_coord + man_rect[2] + 10
                nodes_count = Font.render(("  " + str(Nodes))[-2:] + " / " + str(Max_Nodes),True,(0,0,0))
                nodes_rect = nodes_count.get_rect()
                WIN.blit(nodes_icon,(x_coord,(HEIGHT/25-32)/2))
                x_coord = x_coord + 10 + 32
                WIN.blit(nodes_count,(x_coord,(HEIGHT/25-nodes_rect[3])/2))
            elif Win_condition != 0 :
                if Win_condition == -1 :
                    if Winner == None :
                        text = FontT.render("You died and LOST wait for the match to end",True,(0,0,0))
                    else :
                        text = FontT.render(Winner+" WON, wait for the host to return to the lobby",True,(0,0,0))
                else :
                    text = FontT.render("You WON, wait for the host to return to the lobby",True,(0,0,0))
                text_rect =  text.get_rect()
                text_rect.center = ((WIDTH-260)/4,HEIGHT/50)
                WIN.blit(text,text_rect)
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
                        if tiles[selected_tile[1]][selected_tile[0]].ore.tier == 1 :
                            elements = len(mines)
                        else :
                            elements = 1
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
                                else :
                                    WIN.blit(mines[i*3+j],(x_coloana+3,y_rand+3))
                    #Afisarea imaginii si informatiilor elementului selectat din meniul de structuri
                    if Element_selectat != None :
                        #desenare chenarul in care sa se incadreze imaginea
                        pygame.draw.rect(WIN,(25,25,25),(HEIGHT/3+20,HEIGHT*4/5+20,large_img_element_afisat.get_width()+10,large_img_element_afisat.get_width()+10))
                        pygame.draw.rect(WIN,Gri,(HEIGHT/3+25,HEIGHT*4/5+25,large_img_element_afisat.get_width(),large_img_element_afisat.get_width()))
                        WIN.blit(large_img_element_afisat,(HEIGHT/3+25,HEIGHT*4/5+25))
                        nonlocal can_build
                        can_build = True
                        #afisarea caracteristicilor elementului selectat
                        if construction_tab == "Units" :
                            text = Font.render("HP: "+str(Units.predefined_Units[u_names[Element_selectat]][1]) + "   DEF: " + str(Units.predefined_Units[u_names[Element_selectat]][3]) +"   ATK: " +str(Units.predefined_Units[u_names[Element_selectat]][2]) ,True,(0,0,0))
                        elif construction_tab == "Structures" :
                            if s_names[Element_selectat] == "Healing_Point" :
                                text = Font.render("HP: "+str(Structures.predefined_structures[s_names[Element_selectat]][1]) + "   DEF: " + str(Structures.predefined_structures[s_names[Element_selectat]][3]) + "   Heal: " + str(Structures.hospital_heal) ,True,(0,0,0))
                            elif s_names[Element_selectat] == "Cache" :
                                text = Font.render("HP: "+str(Structures.predefined_structures[s_names[Element_selectat]][1]) + "   DEF: " + str(Structures.predefined_structures[s_names[Element_selectat]][3]) + "   Supply: 6" ,True,(0,0,0))
                            else :
                                text = Font.render("HP: "+str(Structures.predefined_structures[s_names[Element_selectat]][1]) + "   DEF: " + str(Structures.predefined_structures[s_names[Element_selectat]][3]) ,True,(0,0,0))
                        else :
                            if tiles[selected_tile[1]][selected_tile[0]].ore.tier == 1 :
                                Yield = Structures.predefined_structures[m_names[Element_selectat]][10][0]
                            else :
                                Yield = Structures.predefined_structures[m_names[Element_selectat]][10][1]
                            text = Font.render("HP: "+str(Structures.predefined_structures[s_names[Element_selectat]][1]) + "   DEF: " + str(Structures.predefined_structures[s_names[Element_selectat]][3]) + "   Yield: " + str(Yield)  ,True,(0,0,0))

                        y_center  = (HEIGHT*4/5 + ButtonR_rect[1])/2
                        text_rect = text.get_rect()
                        x_afis = HEIGHT/3 + HEIGHT/5 + (WIDTH-HEIGHT*2/3 - HEIGHT/5 - text_rect[2])/2
                        WIN.blit(text,(x_afis,y_center-text_rect[3]/2))
                        #desenarea butonului de Build sau recruit
                        if construction_tab == "Units" :
                            Create_Button.text = FontT.render("Recruit",True,(0,0,0))
                            #desenarea resurselor necesare construirii 
                            cost = Units.predefined_Units[u_names[Element_selectat]][7]
                            lungime = 0
                            M_cost = None
                            F_cost = None
                            MP_cost = None
                            if cost[0] != None and cost[0] != 0 :
                                if Mithril >= cost[0] :
                                    M_cost = Font.render(str(cost[0]),True,Green)
                                else :
                                    can_build = False
                                    M_cost = Font.render(str(cost[0]),True,Red)
                                M_rect =  M_cost.get_rect()
                            if cost[1] != None and cost[1] != 0 :
                                if Flerovium >= cost[1] :
                                    F_cost = Font.render(str(cost[1]),True,Green)
                                else :
                                    can_build = False
                                    F_cost = Font.render(str(cost[1]),True,Red)
                                F_rect = F_cost.get_rect()
                            if cost[2] != None and cost[2] != 0 :
                                if Max_Man_power - Man_power_used >= cost[2] :
                                    MP_cost = Font.render(str(cost[2]),True,Green)
                                else :
                                    can_build = False
                                    MP_cost = Font.render(str(cost[2]),True,Red)
                                MP_rect = MP_cost.get_rect()
                            #determinarea lungimii costului cand e afisat
                            if M_cost != None :
                                lungime += 32 + 10 + M_rect[2]
                                if F_cost !=None or MP_cost !=None :
                                    lungime += 10
                            if F_cost != None :
                                lungime += 32 + 10 + F_rect[2]
                                if  MP_cost !=None :
                                    lungime += 10
                            if MP_cost != None :
                                lungime += 32 + 10 + MP_rect[2]
                            #afisarea costurilor
                            start_x = ButtonC_rect[0] + ButtonC_rect[2]/2 - lungime/2 
                            y_center = ButtonC_rect[1] -21
                            if M_cost != None :
                                WIN.blit(mithril_icon,(start_x,y_center - 16))
                                start_x += 42
                                WIN.blit(M_cost,(start_x,y_center - M_rect[3]/2)) 
                                start_x += M_rect[2] + 10
                            if F_cost != None :
                                WIN.blit(flerovium_icon,(start_x,y_center - 16))
                                start_x += 42
                                WIN.blit(F_cost,(start_x,y_center - F_rect[3]/2)) 
                                start_x += F_rect[2] + 10
                            if MP_cost != None :
                                WIN.blit(man_power_icon,(start_x,y_center - 16))
                                start_x += 42
                                WIN.blit(MP_cost,(start_x,y_center - MP_rect[3]/2)) 
                        else :
                            Create_Button.text = FontT.render("Build",True,(0,0,0))
                            #desenarea resurselor necesare construirii 
                            if construction_tab == "Structures" :
                                cost = Structures.predefined_structures[s_names[Element_selectat]][7]
                            else :
                                cost = Structures.predefined_structures[m_names[Element_selectat]][7]
                            lungime = 0
                            M_cost = None
                            F_cost = None
                            if cost[0] != None and cost[0] != 0 :
                                if Mithril >= cost[0] :
                                    M_cost = Font.render(str(cost[0]),True,Green)
                                else :
                                    can_build = False
                                    M_cost = Font.render(str(cost[0]),True,Red)
                                M_rect =  M_cost.get_rect()
                            if cost[1] != None and cost[1] != 0 :
                                if Flerovium >= cost[1] :
                                    F_cost = Font.render(str(cost[1]),True,Green)
                                else :
                                    can_build = False
                                    F_cost = Font.render(str(cost[1]),True,Red)
                                F_rect = F_cost.get_rect()

                            if s_names[Element_selectat] == "Node" and Max_Nodes == Nodes :
                                can_build = False

                            #determinarea lungimii costului cand e afisat
                            if M_cost !=None and F_cost !=None  :
                                lungime = 64 + 30 + M_rect[2] + F_rect[2]
                            elif M_cost !=None or F_cost !=None :
                                lungime = 32 +  10 
                                if M_cost != None :
                                    lungime += M_rect[3] 
                                else :
                                    lungime += F_rect[3]
                            #afisarea costurilor
                            start_x = ButtonC_rect[0] + ButtonC_rect[2]/2 - lungime/2 
                            y_center = ButtonC_rect[1] -21
                            if M_cost != None :
                                WIN.blit(mithril_icon,(start_x,y_center - 16))
                                start_x += 42
                                WIN.blit(M_cost,(start_x,y_center - M_rect[3]/2)) 
                                start_x += M_rect[2] +10
                            if F_cost != None :
                                WIN.blit(flerovium_icon,(start_x,y_center - 16))
                                start_x += 42
                                WIN.blit(F_cost,(start_x,y_center - F_rect[3]/2)) 
                                start_x += F_rect[2]


                        if can_build == False :
                            pygame.draw.rect(WIN,(25,25,25),ButtonC_rect)
                        else :
                            pygame.draw.rect(WIN,Light_Green,ButtonC_rect)
                        Create_Button.update(WIN)
                else :
                    pygame.draw.rect(WIN,(25,25,25),(HEIGHT/3,HEIGHT*4/5-5 , WIDTH - HEIGHT/3,5))
                    pygame.draw.rect(WIN,(225, 223, 240),(HEIGHT/3,HEIGHT*4/5, WIDTH - HEIGHT/3,HEIGHT/5))
                    #daca este selectata o unitate sau cladire o afiseaza :
                    if tile_empty == False and (tiles[selected_tile[1]][selected_tile[0]].structure != None or tiles[selected_tile[1]][selected_tile[0]].unit != None) :
                        refund_bool = False
                        repair_bool = False
                        aford_repair = True
                        pygame.draw.rect(WIN,(25,25,25),(HEIGHT/3+20,HEIGHT*4/5+20,large_img_element_afisat.get_width()+10,large_img_element_afisat.get_width()+10))
                        pygame.draw.rect(WIN,Gri,(HEIGHT/3+25,HEIGHT*4/5+25,large_img_element_afisat.get_width(),large_img_element_afisat.get_width()))
                        WIN.blit(large_img_element_afisat,(HEIGHT/3+25,HEIGHT*4/5+25))
                        if tiles[selected_tile[1]][selected_tile[0]].unit != None and  (tiles[selected_tile[1]][selected_tile[0]].structure == None or (tiles[selected_tile[1]][selected_tile[0]].structure.name == "Bunker" and tiles[selected_tile[1]][selected_tile[0]].structure.owner == map_locations[Pozitie])) :
                            type = "unit"
                            entity =  tiles[selected_tile[1]][selected_tile[0]].unit
                        else :
                            type = "structure"
                            entity =  tiles[selected_tile[1]][selected_tile[0]].structure
                        #determinarea lungimii afisarii caracteristicilor
                        y_center  = (HEIGHT*4/5 + ButtonR_rect[1])/2
                        l_afis = 0
                        HP = Font.render("HP:",True,(0,0,0))
                        HP_rect = HP.get_rect()
                        l_afis += HP_rect[2] + 5
                        H_value = Font.render(str(entity.HP)+"/"+str(entity.MaxHP),True,(0,0,0))
                        H_value_rect = H_value.get_rect()
                        l_afis += 256 + 25
                        #Afisare defence
                        Dtext = Font.render("DEFENCE: "+ str(entity.defence),True,(0,0,0))
                        Dtext_rect = Dtext.get_rect()
                        l_afis += Dtext_rect[2] + 25
                        if type == "unit" :
                            DMtext = Font.render("DAMAGE: "+ str(entity.attack),True,(0,0,0))
                            DMtext_rect = DMtext.get_rect()
                            l_afis += DMtext_rect[2]
                        elif entity.name == "Healing_Point" :
                            Healtext = Font.render("Heal: "+ str(Structures.hospital_heal),True,(0,0,0))
                            Healtext_rect = Healtext.get_rect()
                            l_afis += Healtext_rect[2]
                        elif entity.name == "Cache" :
                            Stext = Font.render("Supply: 6",True,(0,0,0))
                            Stext_rect = Stext.get_rect()
                            l_afis += Stext_rect[2]
                        elif entity.name[:4] == "Mine" :
                            if tiles[selected_tile[1]][selected_tile[0]].ore.tier == 1 :
                                Yield = Structures.predefined_structures[entity.name][10][0]
                            else :
                                Yield = Structures.predefined_structures[entity.name][10][1]
                            Yieldtext = Font.render("Yield: "+ str(Yield),True,(0,0,0))
                            Yieldtext_rect = Yieldtext.get_rect()
                            l_afis += Yieldtext_rect[2]
                        #Afisarea caracteristicilor
                        x_afis = HEIGHT/3 + HEIGHT/5 +(WIDTH - HEIGHT/3 - HEIGHT/5 - l_afis)/2
                        WIN.blit(HP,(x_afis,y_center -HP_rect[3]/2))
                        x_afis += HP_rect[2] + 5
                        #Healthbar
                        pygame.draw.rect(WIN,(25,25,25),(x_afis,y_center-18,256,36))
                        pygame.draw.rect(WIN,Gri,(x_afis+3,y_center-15,250,30))
                        pygame.draw.rect(WIN,Light_Green,(x_afis+3,y_center-15,250*entity.HP/entity.MaxHP,30))
                        WIN.blit(H_value,(x_afis + 10,y_center-H_value_rect[3]/2))
                        x_afis += 256 + 25
                        WIN.blit(Dtext,(x_afis,y_center-Dtext_rect[3]/2))
                        x_afis += Dtext_rect[2] + 25
                        if type == "unit" :
                            WIN.blit(DMtext,(x_afis,y_center - DMtext_rect[3]/2))
                        elif entity.name == "Healing_Point" :
                            WIN.blit(Healtext,(x_afis,y_center - Healtext_rect[3]/2))
                        elif entity.name == "Cache" :
                            WIN.blit(Stext,(x_afis,y_center - Stext_rect[3]/2))
                        elif entity.name[:4] == "Mine" :
                            WIN.blit(Yieldtext,(x_afis,y_center - Yieldtext_rect[3]/2))
                        #Afiseaza  butonul de Refund si butonulde repair
                        if (tiles[selected_tile[1]][selected_tile[0]].structure != None and tiles[selected_tile[1]][selected_tile[0]].structure.name == "Kernel") == 0 and ((tiles[selected_tile[1]][selected_tile[0]].structure != None and tiles[selected_tile[1]][selected_tile[0]].structure.owner == map_locations[Pozitie] and tiles[selected_tile[1]][selected_tile[0]].structure.HP == tiles[selected_tile[1]][selected_tile[0]].structure.MaxHP) or (tiles[selected_tile[1]][selected_tile[0]].unit != None and tiles[selected_tile[1]][selected_tile[0]].unit.owner == map_locations[Pozitie] and tiles[selected_tile[1]][selected_tile[0]].unit.HP == tiles[selected_tile[1]][selected_tile[0]].unit.MaxHP and tiles[selected_tile[1]][selected_tile[0]].unit.canAttack == True and tiles[selected_tile[1]][selected_tile[0]].unit.canMove == True )) :
                            refund_bool = True
                        if tiles[selected_tile[1]][selected_tile[0]].structure != None  and tiles[selected_tile[1]][selected_tile[0]].unit == None and  tiles[selected_tile[1]][selected_tile[0]].structure.HP < math.ceil(tiles[selected_tile[1]][selected_tile[0]].structure.MaxHP *0.65) and tiles[selected_tile[1]][selected_tile[0]].structure.owner == map_locations[Pozitie] :
                            repair_bool = True
                            #determinare pret
                            cost = tiles[selected_tile[1]][selected_tile[0]].structure.price
                            if tiles[selected_tile[1]][selected_tile[0]].structure.HP < math.ceil(tiles[selected_tile[1]][selected_tile[0]].structure.MaxHP *0.2) :
                                cost = (math.ceil(cost[0]/2),math.ceil(cost[1]/2))
                            elif tiles[selected_tile[1]][selected_tile[0]].structure.HP < math.ceil(tiles[selected_tile[1]][selected_tile[0]].structure.MaxHP *0.45) :
                                cost = (math.ceil(cost[0]*0.3),math.ceil(cost[1]*0.3))
                            else :
                                cost = (math.ceil(cost[0]*0.2),math.ceil(cost[1]*0.2))
                            lungime = 0
                            M_cost = None
                            F_cost = None
                            if cost[0] > 0 :
                                if Mithril >= cost[0] :
                                    M_cost = Font.render(str(cost[0]),True,Green)
                                else :
                                    aford_repair = False
                                    M_cost = Font.render(str(cost[0]),True,Red)
                                M_rect = M_cost.get_rect()
                                lungime += M_rect[2] + 42
                                if cost[1] > 0 :
                                    if Flerovium >= cost[1] :
                                        F_cost = Font.render(str(cost[1]),True,Green)
                                    else :
                                        aford_repair = False
                                        F_cost = Font.render(str(cost[1]),True,Red)
                                    F_rect = F_cost.get_rect()
                                    lungime += F_rect[2] + 52
                            elif cost[1] > 0 :
                                if Flerovium >= cost[1] :
                                    F_cost = Font.render(str(cost[1]),True,Green)
                                else :
                                    aford_repair = False
                                    F_cost = Font.render(str(cost[1]),True,Red)
                                F_rect = F_cost.get_rect()
                                lungime += F_rect[2] + 42
                        #afisarea butoanelor 
                        if refund_bool == True and repair_bool == True :
                            #ButtonR_rect = (ButtonR_rect[0] -ButtonR_rect[2]/2 - 50,ButtonR_rect[1],ButtonR_rect[2],ButtonR_rect[3])
                            Refund_Button.rect = pygame.Rect(Refund_Button.rect[0] -ButtonR_rect[2]/2 - 50,Refund_Button.rect[1],Refund_Button.rect[2],Refund_Button.rect[3])
                            pygame.draw.rect(WIN,(25,25,25),(ButtonR_rect[0] -ButtonR_rect[2]/2 - 50,ButtonR_rect[1],ButtonR_rect[2],ButtonR_rect[3]))
                            Refund_Button.update(WIN)
                            Refund_Button.rect = pygame.Rect(Refund_Button.rect[0] +ButtonR_rect[2]/2 + 50,Refund_Button.rect[1],Refund_Button.rect[2],Refund_Button.rect[3])
                            ButtonR_rect = (ButtonR_rect[0] +ButtonR_rect[2]/2 + 50,ButtonR_rect[1],ButtonR_rect[2],ButtonR_rect[3])
                            Repair_Button.rect =pygame.Rect(Repair_Button.rect[0] +ButtonR_rect[2]/2 + 50,Repair_Button.rect[1],Repair_Button.rect[2],Repair_Button.rect[3])
                            #Afisare costuri repairs
                            start_x = ButtonR_rect[0] + ButtonR_rect[2]/2 - lungime/2 
                            y_center = ButtonR_rect[1] -21
                            if M_cost != None :
                                WIN.blit(mithril_icon,(start_x,y_center - 16))
                                start_x += 42
                                WIN.blit(M_cost,(start_x,y_center - M_rect[3]/2)) 
                                start_x += M_rect[2] +10
                            if F_cost != None :
                                WIN.blit(flerovium_icon,(start_x,y_center - 16))
                                start_x += 42
                                WIN.blit(F_cost,(start_x,y_center - F_rect[3]/2)) 
                            pygame.draw.rect(WIN,(25,25,25),ButtonR_rect)
                            Repair_Button.update(WIN)
                            ButtonR_rect = (ButtonR_rect[0] -ButtonR_rect[2]/2 - 50,ButtonR_rect[1],ButtonR_rect[2],ButtonR_rect[3])
                            Repair_Button.rect =pygame.Rect(Repair_Button.rect[0] -ButtonR_rect[2]/2 - 50,Repair_Button.rect[1],Repair_Button.rect[2],Repair_Button.rect[3])
                        elif  (refund_bool == True or repair_bool == True)  :
                            if refund_bool == True :
                                pygame.draw.rect(WIN,(25,25,25),ButtonR_rect)
                                Refund_Button.update(WIN)
                            else :
                                start_x = ButtonR_rect[0] + ButtonR_rect[2]/2 - lungime/2 
                                y_center = ButtonR_rect[1] -21
                                if M_cost != None :
                                    WIN.blit(mithril_icon,(start_x,y_center - 16))
                                    start_x += 42
                                    WIN.blit(M_cost,(start_x,y_center - M_rect[3]/2)) 
                                    start_x += M_rect[2] +10
                                if F_cost != None :
                                    WIN.blit(flerovium_icon,(start_x,y_center - 16))
                                    start_x += 42
                                    WIN.blit(F_cost,(start_x,y_center - F_rect[3]/2)) 
                                if aford_repair == True :
                                    pygame.draw.rect(WIN,Green,ButtonR_rect)
                                else :
                                    pygame.draw.rect(WIN,Red,ButtonR_rect)
                                Repair_Button.update(WIN)

            #desenare ESCAPE_TAB
            if Escape_tab == True :
                #desenare escape part
                pygame.draw.rect(WIN,(25,25,25),(Escape_menu_part[0]-5,Escape_menu_part[1]-5,Escape_menu_part[2]+10,Escape_menu_part[3]+10))
                pygame.draw.rect(WIN,Gri,Escape_menu_part)
                #Volume slider
                WIN.blit(music_text,music_text_rect)
                pygame.draw.rect(WIN,(25,25,25),(Escape_menu_part[0]+50,music_text_rect[1]+music_text_rect[3]+30,Escape_menu_part[2]-100,15))
                pygame.draw.rect(WIN,Cyan,slider_rect)
                text = Font.render(str(VOLUM),True,(0,0,0))
                text_rect = text.get_rect()
                text_rect.center = (slider_rect[0]+12,slider_rect[1]+slider_rect[3]+20)
                WIN.blit(text,text_rect)
                #next song button
                pygame.draw.rect(WIN,(25,25,25),ButtonN_rect)
                Next_Button.update(WIN)
                #escape button
                pygame.draw.rect(WIN,(25,25,25),ButtonE_rect)
                Escape_Button.update(WIN)

        pygame.display.update()

    #Functia cu care serverul asculta pentru mesajele unui client
    def reciev_thread_from_client(client,cod) :
        global Confirmatii_timer
        nonlocal Confirmatii
        try :
            while True :
                header = client.recv(10)
                while len(header) != HEADERSIZE :
                    header += server.recv(HEADERSIZE-len(header))
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    while len(data_recv) != int(header) :
                        data_recv += client.recv(int(header) - len(data_recv))
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
                    elif data_recv[0] == "return_to_lobby" :
                        Confirmatii += 1 
                        break
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
        nonlocal Confirmation
        try :
            while True :
                header = server.recv(10)
                while len(header) != HEADERSIZE :
                    header += server.recv(HEADERSIZE-len(header))
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = server.recv(int(header))
                    while len(data_recv) != int(header) :
                        data_recv += server.recv(int(header) - len(data_recv))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "I_died...Fuck_off":
                        server.close()
                        run = False
                        break
                    elif data_recv[0] == "return_to_lobby":
                        data_send = pickle.dumps(("return_to_lobby",None))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        server.send(data_send)
                        Confirmation = True
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

    if Role == "host":
        sent_reaquest = False

    #Un thread care va functiona la host care are rolul sa tina cont de cat timp trece in timpul jocului
    def timer_thread ():
        global timer
        while  run == True :
            time.sleep(1)
            if timer > 0 :
                timer = timer - 1

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
        nonlocal Flerovium
        nonlocal F_Yield
        nonlocal Mithril
        nonlocal M_Yield
        nonlocal Nodes
        nonlocal Man_power_used
        nonlocal Max_Man_power

        global tiles

        #reverse unit movement
        if Action[0] == "move_unit" :
            tiles[Action[1][1]][Action[1][0]].unit = tiles[Action[2][1]][Action[2][0]].unit
            tiles[Action[1][1]][Action[1][0]].unit.position = tiles[Action[1][1]][Action[1][0]].position

            del tiles[Action[2][1]][Action[2][0]].unit
            tiles[Action[2][1]][Action[2][0]].unit = None

            refresh_map([Action[1], Action[2]])

            tiles[Action[1][1]][Action[1][0]].unit.canMove = True
            selected_tile_check()
        elif Action[0] == "new_entity" :
            if Action[1] == "Structures":
                new_struct = tiles[Action[4][1]][Action[4][0]].structure
                #se reda costul
                Flerovium += new_struct.price[1]
                Mithril += new_struct.price[0]
                #conditie daca este Node
                if new_struct.name == "Node":
                    Nodes -= 1
                    new_node = Node.getNodeFromObj(new_struct)
                    new_node.Kill()
                    del new_node

                if new_struct.name == "Cache":
                    Max_Man_power -= 6
                #Sterge structura
                tiles[Action[4][1]][Action[4][0]].structure = None
                refresh_map([[Action[4][0],Action[4][1]]])
                RemoveObjectFromList(Action[5], controllables_vec)
                if Action[5] in caster_controllables_vec:
                    RemoveObjectFromList(Action[5], caster_controllables_vec)
                del new_struct
            
            elif Action[1] == "Mines":
                new_struct = tiles[Action[4][1]][Action[4][0]].structure
                #se reda costul
                Flerovium += new_struct.price[1]
                Mithril += new_struct.price[0]
                if new_struct.name[:4] == "Mine" :
                    #se adauga yieldul pentru o resursa
                    if tiles[selected_tile[1]][selected_tile[0]].ore.tier == 1 :
                        M_Yield -= Structures.predefined_structures[new_struct.name][10][0]
                    else :
                        F_Yield -= Structures.predefined_structures[new_struct.name][10][1]
                #Sterge structura
                tiles[Action[4][1]][Action[4][0]].structure = None
                refresh_map([[Action[4][0],Action[4][1]]])
                RemoveObjectFromList(Action[5], controllables_vec)
                if Action[5] in caster_controllables_vec:
                    RemoveObjectFromList(Action[5], caster_controllables_vec)
                del new_struct
            elif Action[1] == "Units":
                new_unit = tiles[Action[4][1]][Action[4][0]].unit
                #se redau costurile
                Flerovium += new_unit.price[1]
                Mithril += new_unit.price[0]
                Man_power_used -= new_unit.price[2]
                del new_unit
                #Se sterge unitatea
                tiles[Action[4][1]][Action[4][0]].unit = None
                refresh_map([[Action[4][0],Action[4][1]]])
                if Action[5] in caster_controllables_vec:
                    RemoveObjectFromList(Action[5], caster_controllables_vec)
                selected_tile_check()

        elif Action[0] == "refund_entity":
            if Action[1] == "structure" : #Structure case. Also don't refund Kernel lol
                my_struct = Action[3]

                #if the structure was a node
                if my_struct.name == "Node" :
                    Nodes += 1
                    new_node = Node.Node((Action[2][0] + 0.5, Action[2][1] + 0.5), 4.5, my_struct)
                    for node in Node.NodeList:
                        if node != new_node and new_node.CheckCollision(node):
                            new_node.Add(node)

                if my_struct.name == "Cache":
                    Max_Man_power += 6

                Flerovium -= int(my_struct.price[1] * my_struct.refund_percent)
                Mithril -= int(my_struct.price[0] * my_struct.refund_percent)
                if my_struct.name[:4] == "Mine" :
                    #se adauga yieldul pentru o resursa
                    if tiles[selected_tile[1]][selected_tile[0]].ore.tier == 1 :
                        M_Yield += Structures.predefined_structures[my_struct.name][10][0]
                    else :
                        F_Yield += Structures.predefined_structures[my_struct.name][10][1]

                tiles[Action[2][1]][Action[2][0]].structure = my_struct
                refresh_map([[Action[2][0],Action[2][1]]])
                del my_struct

            else  :    #Unit case
                my_unit = Action[3]

                Flerovium -= int(my_unit.price[1] * my_unit.refund_percent)
                Mithril -= int(my_unit.price[0] * my_unit.refund_percent)
                Man_power_used += my_unit.price[2]

                tiles[Action[2][1]][Action[2][0]].unit = my_unit
                refresh_map([[Action[2][0],Action[2][1]]])
                del my_unit
                
        elif Action[0] == "repair_entity":
            #scaderea pretului
            Mithril += Action[3][0]
            Flerovium += Action[3][1]
            tiles[Action[1][1]][Action[1][0]].structure.ModifyHealth(-Action[2])
        
        elif Action[0] == "damaged_entity" :
            if Action[1] == "unit" :
                if Action[5] == False :
                    tiles[Action[2][1]][Action[2][0]].unit.ModifyHealth(-Action[3])
                else :
                    new_unit = Units.BuildUnit(u_names.index(Action[6]), (Action[2][0], Action[2][1]), Action[8])
                    tiles[Action[2][1]][Action[2][0]].unit = new_unit
                    tiles[Action[2][1]][Action[2][0]].unit.HP = Action[7]
                    refresh_map([[Action[2][0],Action[2][1]]])
                    del new_unit
            else :
                if Action[5] == False :
                    tiles[Action[2][1]][Action[2][0]].structure.ModifyHealth(-Action[3])
                else :
                    #determina daca e mina sau nu
                    if Action[6][:4] == "Mine" :
                        new_struct = Structures.BuildStructure(m_names.index(Action[6]) + len(s_names),(Action[2][0], Action[2][1]), Action[8])
                    else :
                        new_struct = Structures.BuildStructure(s_names.index(Action[6]),(Action[2][0], Action[2][1]), Action[8])
                    if Action[6] == "Kernel" :
                        tiles = copy.deepcopy(Action[9])
                        colorTable[Action[8]] = Action[10]
                        TileClass.colorTable = colorTable
                        refresh_map()

                    else :
                        tiles[Action[2][1]][Action[2][0]].structure = new_struct
                        tiles[Action[2][1]][Action[2][0]].structure.HP = Action[7]
                        refresh_map([[Action[2][0],Action[2][1]]])
                    if new_struct:
                        del new_struct

            tiles[Action[4][1]][Action[4][0]].unit.canAttack = True
        selected_tile_check()

    def selected_tile_check() :
        global tile_empty
        global enlighted_surface
        nonlocal construction_tab
        if timer <= 0 or Whos_turn != Pozitie:
            enlighted_surface = draw_enlighted_tiles()
        if selected_tile[0] != None:
            if tiles[selected_tile[1]][selected_tile[0]].unit == None and tiles[selected_tile[1]][selected_tile[0]].structure == None :
                tile_empty = True
                enlighted_surface = draw_enlighted_tiles()
                if  tiles[selected_tile[1]][selected_tile[0]].ore != None :
                    construction_tab = "Mines"
                elif construction_tab == "Mines" :
                    construction_tab = "Structures"
            else :
                nonlocal Element_selectat
                global selected_controllable
                if tiles[selected_tile[1]][selected_tile[0]].unit != None and tiles[selected_tile[1]][selected_tile[0]].unit.owner == map_locations[Pozitie] and (selected_tile[0], selected_tile[1]) in visible_tiles:
                    enlighted_surface = draw_enlighted_tiles()
                    selected_controllable = tiles[selected_tile[1]][selected_tile[0]].unit
                    if selected_controllable.canMove == True:
                        determine_enlighted_tiles()
                        enlighted_surface = draw_enlighted_tiles(True)
                        Element_selectat = None
                tile_empty = False

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
    Mithril = 20
    M_Yield = 0
    Flerovium = 0
    F_Yield = 0
    Man_power_used = 0
    ManPowerCap = 126
    Max_Man_power = 6
    Nodes = 0
    Max_Nodes = 50
    #Vectorul care detine actiunile playerului din tura lui
    Turn_Actions = []
    Ctrl_zeed = False
    #daca e -1 playerul a murit, daca este 1 playerul este singurul viu
    Win_condition = 0
    Winner = None
    Escape_tab = False
    Slider_Got = False
    #flashes 
    Transmited_flashes = {}
    flash = 0
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
        sent_reaquest = False
        return_lobby = False
        Confirmatii = 0
    else :
        #restart listenig to the server
        recv_from_server = threading.Thread(target = reciev_thread_from_server, args = (Connection,))
        recv_from_server.start()
        Changes_from_server = []
        timer_notification_sent = False
        next_turn = False
        Confirmation = False

    time_thread = threading.Thread(target = timer_thread)
    time_thread.start() 

    def delete_entity(entity,transmited = False):
        nonlocal Man_power_used
        nonlocal M_Yield
        nonlocal F_Yield
        nonlocal Max_Man_power
        nonlocal Nodes
        nonlocal Win_condition
        nonlocal Transmited_flashes
        removed_position = []
        position = entity.position
        if type(entity) == Structures.Structure:
            tiles[position[1]][position[0]].structure = None
            if transmited == False :
                removed_position.append(position)
            elif entity.owner == map_locations[Pozitie] :
                image = Structures.textures[Structures.texture_names.index(entity.texture)].copy()
                dark = pygame.Surface(image.get_size()).convert_alpha()
                dark.fill((0, 0, 0, 0))
                for i in range(image.get_width()):
                    for j in range(image.get_height()):
                        if image.get_at((i,j)) != (0,0,0,0):
                            dark.set_at((i,j), (0, 0, 0,255))
                Transmited_flashes[position] = dark
            if entity.name == "Kernel":
                for y in range(rows):
                    for x in range(tiles_per_row):
                        if tiles[y][x].unit != None and tiles[y][x].unit.owner == entity.owner:
                            tiles[y][x].unit = None
                            if transmited == False :
                                removed_position.append(position)
                            elif entity.owner == map_locations[Pozitie] :
                                image = Structures.textures[Structures.texture_names.index(entity.texture)].copy()
                                dark = pygame.Surface(image.get_size()).convert_alpha()
                                dark.fill((0, 0, 0, 0))
                                for i in range(image.get_width()):
                                    for j in range(image.get_height()):
                                        if image.get_at((i,j)) != (0,0,0,0):
                                            dark.set_at((i,j), (0, 0, 0,255))
                                Transmited_flashes[position] = dark
                        elif tiles[y][x].structure != None and tiles[y][x].structure.owner == entity.owner:
                            tiles[y][x].structure = None
                            if transmited == False :
                                removed_position.append(position)
                            elif entity.owner == map_locations[Pozitie] :
                                image = Structures.textures[Structures.texture_names.index(entity.texture)].copy()
                                dark = pygame.Surface(image.get_size()).convert_alpha()
                                dark.fill((0, 0, 0, 0))
                                for i in range(image.get_width()):
                                    for j in range(image.get_height()):
                                        if image.get_at((i,j)) != (0,0,0,0):
                                            dark.set_at((i,j), (0, 0, 0,255))
                                Transmited_flashes[position] = dark
                
                colorTable[entity.owner] = None
                TileClass.colorTable = colorTable
                if entity.owner ==  map_locations[Pozitie] :
                    Win_condition = -1
                check_for_winner()
                if Winner == map_locations[Pozitie] and Whos_turn == Pozitie :
                    #end turn
                    timer = 0 
                    if Role == "host" :
                        Transmit_to_all.append((("Force_end_turn",None),None))
                    else :
                        data_send = pickle.dumps(("Force_end_turn",None))
                        data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                        Connection.send(data_send)
                
            if entity.owner == map_locations[Pozitie] :
                RemoveObjectFromList(entity, controllables_vec)
                if tiles[position[1]][position[0]].ore != None :
                    #daca e mina
                    if tiles[position[1]][position[0]].ore.tire ==1 :
                        M_Yield -= entity.Yield[0]
                    else :
                        F_Yield -= entity.Yield[1]
                elif entity.name == "Healing_Point":
                    RemoveObjectFromList(entity, caster_controllables_vec)
                elif entity.name == "Cache":
                    Max_Man_power -= 6
                elif entity.name == "Node":
                    Nodes -=1
                    my_node = Node.getNodeFromObj(entity)
                    my_node.Kill()
                    del my_node

        elif type(entity) == Units.Unit:
            tiles[position[1]][position[0]].unit = None
            if transmited == False :
                removed_position.append(position)
            elif entity.owner == map_locations[Pozitie] :
                image = Units.textures[Units.texture_names.index(entity.texture)].copy()
                dark = pygame.Surface(image.get_size()).convert_alpha()
                dark.fill((0, 0, 0, 0))
                for i in range(image.get_width()):
                    for j in range(image.get_height()):
                        if image.get_at((i,j)) != (0,0,0,0):
                            dark.set_at((i,j), (0, 0, 0,255))
                Transmited_flashes[position] = dark
            if entity.owner == map_locations[Pozitie]:
                Man_power_used -= entity.price[2]
                RemoveObjectFromList(entity, controllables_vec)

        return removed_position

    
    def repair_building() :
        nonlocal Flerovium
        nonlocal Mithril
        nonlocal Whos_turn

        if timer > 0 and Whos_turn == Pozitie:
            #determinare pret
            cost = tiles[selected_tile[1]][selected_tile[0]].structure.price
            if tiles[selected_tile[1]][selected_tile[0]].structure.HP < math.ceil(tiles[selected_tile[1]][selected_tile[0]].structure.MaxHP *0.2) :
                cost = (math.ceil(cost[0]/2),math.ceil(cost[1]/2))
            elif tiles[selected_tile[1]][selected_tile[0]].structure.HP < math.ceil(tiles[selected_tile[1]][selected_tile[0]].structure.MaxHP *0.45) :
                cost = (math.ceil(cost[0]*0.3),math.ceil(cost[1]*0.3))
            else :
                cost = (math.ceil(cost[0]*0.2),math.ceil(cost[1]*0.2))
            #scaderea pretului
            Mithril -= cost[0]
            Flerovium -= cost[1]
            modify_value = tiles[selected_tile[1]][selected_tile[0]].structure.MaxHP - tiles[selected_tile[1]][selected_tile[0]].structure.HP
            tiles[selected_tile[1]][selected_tile[0]].structure.ModifyHealth(modify_value)
            Turn_Actions.append(("repair_entity",selected_tile,modify_value,cost))
            

    def refund_entity():
        nonlocal Flerovium
        nonlocal F_Yield
        nonlocal Mithril
        nonlocal M_Yield
        nonlocal Nodes
        nonlocal Man_power_used
        nonlocal Whos_turn
        nonlocal selected_tile
        nonlocal Max_Man_power

        if timer > 0 and Whos_turn == Pozitie:
            if (selected_tile[0], selected_tile[1]) in visible_tiles:
                if tiles[selected_tile[1]][selected_tile[0]].unit != None:    #Unit case
                    my_unit = tiles[selected_tile[1]][selected_tile[0]].unit

                    Flerovium += int(my_unit.price[1] * my_unit.refund_percent)
                    Mithril += int(my_unit.price[0] * my_unit.refund_percent)
                    Man_power_used -= my_unit.price[2]

                    tiles[selected_tile[1]][selected_tile[0]].unit = None
                    refresh_map([[selected_tile[0],selected_tile[1]]])
                    RemoveObjectFromList(my_unit, controllables_vec)
                    Turn_Actions.append(("refund_entity","unit",selected_tile,my_unit))
                    del my_unit
                elif tiles[selected_tile[1]][selected_tile[0]].structure != None and tiles[selected_tile[1]][selected_tile[0]].structure.name != "Kernel": #Structure case. Also don't refund Kernel lol
                    my_struct = tiles[selected_tile[1]][selected_tile[0]].structure

                    #if the structure was a node
                    if my_struct.name == "Node" :
                        Nodes -=1
                        my_node = Node.getNodeFromObj(my_struct)
                        my_node.Kill()
                        del my_node

                    if my_struct.name == "Cache":
                        Max_Man_power -= 6

                    Flerovium += int(my_struct.price[1] * my_struct.refund_percent)
                    Mithril += int(my_struct.price[0] * my_struct.refund_percent)
                    if my_struct.name[:4] == "Mine" :
                        #se adauga yieldul pentru o resursa
                        if tiles[selected_tile[1]][selected_tile[0]].ore.tier == 1 :
                            M_Yield -= Structures.predefined_structures[my_struct.name][10][0]
                        else :
                            F_Yield -= Structures.predefined_structures[my_struct.name][10][1]

                    RemoveObjectFromList(my_struct, controllables_vec)

                    if my_struct in caster_controllables_vec:
                        RemoveObjectFromList(my_struct, caster_controllables_vec)

                    tiles[selected_tile[1]][selected_tile[0]].structure = None
                    refresh_map([[selected_tile[0],selected_tile[1]]])
                    Turn_Actions.append(("refund_entity","structure",selected_tile,my_struct))
                    del my_struct
        selected_tile_check()

    def Create_Building():
        nonlocal Flerovium
        nonlocal F_Yield
        nonlocal Mithril
        nonlocal M_Yield
        nonlocal Nodes
        nonlocal Man_power_used
        nonlocal Max_Man_power
        nonlocal Whos_turn
        nonlocal Element_selectat
        nonlocal selected_tile
        nonlocal ManPowerCap

        if timer > 0 and Whos_turn == Pozitie:
            if  (selected_tile[0], selected_tile[1]) in visible_tiles:
                if construction_tab == "Structures":
                    new_struct = Structures.BuildStructure(Element_selectat, (selected_tile[0], selected_tile[1]), map_locations[Pozitie])
                    for node in Node.NodesFound:
                        if node.CheckBuildingInRadius(new_struct):
                            #conditie daca este Node
                            if new_struct.name == "Node":
                                if Nodes + 1 > Max_Nodes:   #check if can place node
                                    break

                                Nodes += 1
                                new_node = Node.Node((selected_tile[0] + 0.5, selected_tile[1] + 0.5), 4.5, new_struct)
                                Node.Find_connections()

                            if new_struct.name == "Cache":
                                if Max_Man_power < ManPowerCap:
                                    Max_Man_power += 6
                                else:
                                    return

                            #construieste structura
                            tiles[selected_tile[1]][selected_tile[0]].structure = new_struct
                            refresh_map([[selected_tile[0],selected_tile[1]]])
                            if new_struct.special_function != None:
                                caster_controllables_vec.append(new_struct)
                            controllables_vec.append(new_struct)
                            #scade costul
                            Flerovium -= new_struct.price[1]
                            Mithril -= new_struct.price[0]
                            #Adaugarea actiunii in Istoricul actiunilor
                            Turn_Actions.append(("new_entity",construction_tab,Element_selectat,map_locations[Pozitie],selected_tile,new_struct))
                            break
                    del new_struct

                elif construction_tab == "Mines" :
                    new_struct = Structures.BuildStructure(len(structures)+Element_selectat, (selected_tile[0], selected_tile[1]), map_locations[Pozitie])
                    for node in Node.NodesFound:
                        if node.CheckBuildingInRadius(new_struct):
                            #construieste structura
                            tiles[selected_tile[1]][selected_tile[0]].structure = new_struct
                            refresh_map([[selected_tile[0],selected_tile[1]]])
                            if new_struct.special_function != None:
                                caster_controllables_vec.append(new_struct)
                            controllables_vec.append(new_struct)
                            #scade costul
                            Flerovium -= new_struct.price[1]
                            Mithril -= new_struct.price[0]
                            #se adauga yieldul pentru o resursa
                            if tiles[selected_tile[1]][selected_tile[0]].ore.tier == 1 :
                                M_Yield += Structures.predefined_structures[new_struct.name][10][0]
                            else :
                                F_Yield += Structures.predefined_structures[new_struct.name][10][1]
                            #Adaugarea actiunii in Istoricul actiunilor
                            Turn_Actions.append(("new_entity",construction_tab,Element_selectat,map_locations[Pozitie],selected_tile,new_struct))
                            break
                    del new_struct
                elif construction_tab == "Units":
                    new_unit = Units.BuildUnit(Element_selectat, (selected_tile[0], selected_tile[1]), map_locations[Pozitie])
                    for node in Node.NodesFound:
                        if node.CheckBuildingInRadius(new_unit):
                            #Se recruteaza noua unitate
                            tiles[selected_tile[1]][selected_tile[0]].unit = new_unit
                            refresh_map([[selected_tile[0],selected_tile[1]]])
                            controllables_vec.append(new_unit)
                            #se iau costurile
                            Flerovium -= new_unit.price[1]
                            Mithril -= new_unit.price[0]
                            Man_power_used += new_unit.price[2]

                            new_unit.canAttack = False
                            new_unit.canMove = False

                            #Adaugarea actiunii in Istoricul actiunilor
                            Turn_Actions.append(("new_entity",construction_tab,Element_selectat,map_locations[Pozitie],selected_tile,new_unit))
                            break
                    del new_unit
                selected_tile_check()
   
    def check_for_winner():
        nonlocal Winner
        nonlocal Win_condition
        nr_active = 0
        w = None
        for i in range(len(playeri)) :
            if colorTable[map_locations[i]] != None :
                nr_active += 1
                w = playeri[i][0]
        if nr_active == 1 :
            Winner = w
            if Winner == playeri[Pozitie][0] :
                Win_condition = 1
                

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
        global rows
        global tiles_per_row
        nonlocal mapSurfaceNormal 
        nonlocal mapSurface
        nonlocal M_Yield
        nonlocal F_Yield
        infile = None
        try:
            infile = open("Maps/info/" + map_name + ".txt", "rb")
        except:
            infile = open("Maps/Imported_Maps/info/" + map_name + ".txt", "rb")

        tiles.clear()
        rows = pickle.load(infile)
        tiles_per_row = pickle.load(infile)
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

                nonlocal Man_power_used
                nonlocal Nodes

                #Detect if the structure is either Kernel or Node to populate the Node module.
                if new_tile.structure != None:
                    if (new_tile.structure.name == "Kernel" or new_tile.structure.name == "Node") and new_tile.structure.owner == map_locations[Pozitie]:
                        new_node = Node.Node((new_tile.position[0] + 0.5, new_tile.position[1] + 0.5), 4.5, new_tile.structure)
                        if new_tile.structure.name == "Kernel":
                            Node.TreeRoot = new_node
                            new_node.Powered = True

                        #Node.NodeList.append(new_node)

                #Save controlling units and structures
                if new_tile.structure != None: 
                    #Center camera to player's Kernel at the start of the game.
                    if new_tile.structure.name == "Kernel" and new_tile.structure.owner == map_locations[Pozitie]:
                        CurrentCamera.x = new_tile.structure.position[0] * current_tile_length - WIDTH // 2
                        CurrentCamera.y = new_tile.structure.position[1] * current_tile_length - HEIGHT // 2
                        CurrentCamera.Check_Camera_Boundaries()

                    if new_tile.structure.owner == map_locations[Pozitie]:
                        controllables_vec.append(new_tile.structure)

                    if new_tile.structure.name == "Node" and new_tile.structure.owner == map_locations[Pozitie]:
                        Nodes += 1

                    if new_tile.structure.name == "Healing_Point" and new_tile.structure.owner == map_locations[Pozitie]:
                        caster_controllables_vec.append(new_tile.structure)

                    if new_tile.structure.name == "Cache" and new_tile.structure.owner == map_locations[Pozitie]:
                        if Max_Man_power < ManPowerCap:
                            Max_Man_power += 6

                    if new_tile.structure.name[:4] == "Mine" and new_tile.ore != None and new_tile.structure.owner == map_locations[Pozitie]:
                        if new_tile.ore.tier == 1:
                            M_Yield += new_tile.structure.Yield[0]
                        elif new_tile.ore.tier == 2:
                            F_Yield += new_tile.structure.Yield[1]

                if new_tile.unit != None:
                    if new_tile.unit.owner == map_locations[Pozitie]:
                        controllables_vec.append(new_tile.unit)
                        Man_power_used += new_tile.unit.price[2]

                new_vec.append(new_tile)
            tiles.append(new_vec)

        determine_visible_tiles()

        for x in range(rows):  #Redraw the whole map
            for y in range(tiles_per_row):
                tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length), False, (visible_tiles, partially_visible_tiles))
            #tiles.append(newLine)

        mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

        Node.InitTree()

        if TileClass.full_bright == True:
            for y in range(rows):
                for x in range(tiles_per_row):
                    visible_tiles.append((x,y))
                    partially_visible_tiles.append((x,y))

    #functia asta face refresh la harta 
    def refresh_map(specific_vector = None,renderMm = True) :
        nonlocal mapSurface
        global canRenderMinimap
        if renderMm == True :
            canRenderMinimap = True
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

        if timer <= 0 or Whos_turn != Pozitie:
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
    while run == True :
        clock.tick(FPS)

        #actualizare flashuri
        if flash > 0 :
            for x in Transmited_flashes :
                mapSurface.blit(pygame.transform.scale(Transmited_flashes[x],(current_tile_length,current_tile_length)), (x[0] * current_tile_length, x[1]* current_tile_length))
                Transmited_flashes[x].set_alpha(flash)
                flash += -1
            if flash <= 0 :
                Transmited_flashes.clear()
                flash = -1
        #afiseaza totul
        draw_window()
        if flash >= 0 :
            refresh_vector =[]
            for x in Transmited_flashes :
                refresh_vector.append(x)
            refresh_map(refresh_vector,False)
            refresh_vector.clear()
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
                check_for_winner()
                refresh_map()
                map_locations.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1 )
                #modificarea turelor
                if Whos_turn == Coduri_pozitie_client[Killed_Clients[0]] + 1 :
                    timer = turn_time
                    while   Whos_turn >= len(playeri) or colorTable[map_locations[Whos_turn]] == None :
                        if Whos_turn >= len(playeri) :
                            Whos_turn = 0
                        if colorTable[map_locations[Whos_turn]] == None :
                            Whos_turn += 1 
                elif Whos_turn > Coduri_pozitie_client[Killed_Clients[0]] + 1 :
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
                elif Changes_from_clients[0][0] == "new_entity" :
                    if Changes_from_clients[0][1] == "Structures":
                        new_struct = Structures.BuildStructure(Changes_from_clients[0][2], (Changes_from_clients[0][4][0], Changes_from_clients[0][4][1]), Changes_from_clients[0][3])
                        #construieste structura
                        tiles[Changes_from_clients[0][4][1]][Changes_from_clients[0][4][0]].structure = new_struct
                        refresh_map([[Changes_from_clients[0][4][0],Changes_from_clients[0][4][1]]])
                        del new_struct
                    elif Changes_from_clients[0][1] == "Units":
                        new_unit = Units.BuildUnit(Changes_from_clients[0][2], (Changes_from_clients[0][4][0], Changes_from_clients[0][4][1]), Changes_from_clients[0][3])
                        #Se recruteaza noua unitate
                        tiles[Changes_from_clients[0][4][1]][Changes_from_clients[0][4][0]].unit = new_unit
                        refresh_map([[Changes_from_clients[0][4][0],Changes_from_clients[0][4][1]]])
                        del new_unit
                elif Changes_from_clients[0][0] == "refund_entity" :
                    if Changes_from_clients[0][1] == "unit":    #Unit case
                        tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit = None
                        refresh_map([[Changes_from_clients[0][2][0],Changes_from_clients[0][2][1]]])
                    else : #Structure case. Also don't refund Kernel lol
                        tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].structure = None
                        refresh_map([[Changes_from_clients[0][2][0],Changes_from_clients[0][2][1]]])
                elif Changes_from_clients[0][0] == "repair_entity" :
                    tiles[Changes_from_clients[0][1][1]][Changes_from_clients[0][1][0]].structure.ModifyHealth(Changes_from_clients[0][2])
                elif Changes_from_clients[0][0] == "healed_units" :
                    hu_vector = Changes_from_clients[0][1]
                    for i in range(len(hu_vector)) :
                        tiles[hu_vector[i].position[1]][hu_vector[i].position[0]].unit.ModifyHealth(Structures.hospital_heal)
                elif Changes_from_clients[0][0] == "damaged_entity" :
                    if Changes_from_clients[0][1] == "unit" :
                        tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit.ModifyHealth(Changes_from_clients[0][3])
                        if tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit.HP <= 0 :
                            delete_entity(tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit,True)
                        elif tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit.owner == map_locations[Pozitie] :
                            image = Units.textures[Units.texture_names.index(tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].unit.texture)].copy()
                            dark = pygame.Surface(image.get_size()).convert_alpha()
                            dark.fill((0, 0, 0, 0))
                            for i in range(image.get_width()):
                                for j in range(image.get_height()):
                                    if image.get_at((i,j)) != (0,0,0,0):
                                        dark.set_at((i,j), (250, 0, 0,255))
                            Transmited_flashes[Changes_from_clients[0][2]] = dark
                    else :
                        tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].structure.ModifyHealth(Changes_from_clients[0][3])
                        if tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].structure.HP <= 0 :
                            delete_entity(tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].structure,True)
                        elif tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].structure.owner == map_locations[Pozitie] :
                            image = Structures.textures[Structures.texture_names.index(tiles[Changes_from_clients[0][2][1]][Changes_from_clients[0][2][0]].structure.texture)].copy()
                            dark = pygame.Surface(image.get_size()).convert_alpha()
                            dark.fill((0, 0, 0, 0))
                            for i in range(image.get_width()):
                                for j in range(image.get_height()):
                                    if image.get_at((i,j)) != (0,0,0,0):
                                        dark.set_at((i,j), (250, 0, 0,255))
                            Transmited_flashes[Changes_from_clients[0][2]] = dark
                Changes_from_clients.pop(0)
        else :
            #Se verifica daca serverul a trimis lucruri spre acest client
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "leftplayer" :
                    playeri.pop(Changes_from_server[0][1])
                    #modifecarea pozitiilor de pe harta si stergerea cladirilor
                    colorTable[map_locations[Changes_from_server[0][1]]] = None
                    TileClass.colorTable = colorTable
                    check_for_winner()
                    refresh_map()
                    map_locations.pop(Changes_from_server[0][1] )
                    #modificarea turelor
                    if Whos_turn == Changes_from_server[0][1] :
                        timer = turn_time
                        while   Whos_turn >= len(playeri) or colorTable[map_locations[Whos_turn]] == None :
                            if Whos_turn >= len(playeri) :
                                Whos_turn = 0
                            if colorTable[map_locations[Whos_turn]] == None :
                                Whos_turn += 1 
                    elif  Whos_turn > Changes_from_server[0][1] :
                        Whos_turn -= 1
                    if Changes_from_server[0][1] < Pozitie :
                        Pozitie -= 1 
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
                elif Changes_from_server[0][0] == "new_entity" :
                    if Changes_from_server[0][1] == "Structures":
                        new_struct = Structures.BuildStructure(Changes_from_server[0][2], (Changes_from_server[0][4][0], Changes_from_server[0][4][1]), Changes_from_server[0][3])
                        #construieste structura
                        tiles[Changes_from_server[0][4][1]][Changes_from_server[0][4][0]].structure = new_struct
                        refresh_map([[Changes_from_server[0][4][0],Changes_from_server[0][4][1]]])
                        del new_struct

                    elif Changes_from_server[0][1] == "Units":
                        new_unit = Units.BuildUnit(Changes_from_server[0][2], (Changes_from_server[0][4][0], Changes_from_server[0][4][1]), Changes_from_server[0][3])
                        #Se recruteaza noua unitate
                        tiles[Changes_from_server[0][4][1]][Changes_from_server[0][4][0]].unit = new_unit
                        refresh_map([[Changes_from_server[0][4][0],Changes_from_server[0][4][1]]])
                        del new_unit
                elif Changes_from_server[0][0] == "refund_entity" :
                    if Changes_from_server[0][1] == "unit":    #Unit case
                        tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit = None
                        refresh_map([[Changes_from_server[0][2][0],Changes_from_server[0][2][1]]])
                    else : #Structure case. Also don't refund Kernel lol
                        tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].structure = None
                        refresh_map([[Changes_from_server[0][2][0],Changes_from_server[0][2][1]]])
                elif Changes_from_server[0][0] == "repair_entity" :
                    tiles[Changes_from_server[0][1][1]][Changes_from_server[0][1][0]].structure.ModifyHealth(Changes_from_server[0][2])
                elif Changes_from_server[0][0] == "healed_units" :
                    hu_vector = Changes_from_server[0][1]
                    for i in range(len(hu_vector)) :
                        tiles[hu_vector[i].position[1]][hu_vector[i].position[0]].unit.ModifyHealth(Structures.hospital_heal)

                elif Changes_from_server[0][0] == "damaged_entity" :
                    if Changes_from_server[0][1] == "unit" :
                        tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit.ModifyHealth(Changes_from_server[0][3])
                        if tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit.HP <= 0 :
                            delete_entity(tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit,True)
                        elif tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit.owner == map_locations[Pozitie] :
                            image = Units.textures[Units.texture_names.index(tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].unit.texture)].copy()
                            dark = pygame.Surface(image.get_size()).convert_alpha()
                            dark.fill((0, 0, 0, 0))
                            for i in range(image.get_width()):
                                for j in range(image.get_height()):
                                    if image.get_at((i,j)) != (0,0,0,0):
                                        dark.set_at((i,j), (250, 0, 0,255))
                            Transmited_flashes[Changes_from_server[0][2]] = dark
                    else :
                        tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].structure.ModifyHealth(Changes_from_server[0][3])
                        if tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].structure.HP <= 0 :
                            delete_entity(tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].structure,True)
                        elif tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].structure.owner == map_locations[Pozitie] :
                            image = Structures.textures[Structures.texture_names.index(tiles[Changes_from_server[0][2][1]][Changes_from_server[0][2][0]].structure.texture)].copy()
                            dark = pygame.Surface(image.get_size()).convert_alpha()
                            dark.fill((0, 0, 0, 0))
                            for i in range(image.get_width()):
                                for j in range(image.get_height()):
                                    if image.get_at((i,j)) != (0,0,0,0):
                                        dark.set_at((i,j), (250, 0, 0,255))
                            Transmited_flashes[Changes_from_server[0][2]] = dark
                Changes_from_server.pop(0)

        if timer <= 0 :
            for unit in controllables_vec: 
                if unit.HP <= 0:    #If unit is below 0 hp, remove it from the game
                    the_tile = tiles[unit.position[1]][unit.position[0]]
                    if type(unit) == Structures.Structure:
                        the_tile.structure = None
                    if type(unit) == Units.Unit:
                        the_tile.unit = None

                    RemoveObjectFromList(unit, controllables_vec)   #Remove dead controllable from the vector
                    del unit

                if tiles[unit.position[1]][unit.position[0]].unit == unit : #Allow each unit to move and attack for the next round
                    unit.canMove = True
                    unit.canAttack = True           

            determine_visible_tiles()

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
                    while   Whos_turn >= len(playeri) or colorTable[map_locations[Whos_turn]] == None :
                        if Whos_turn >= len(playeri) :
                            Whos_turn = 0
                        if colorTable[map_locations[Whos_turn]] == None :
                            Whos_turn += 1 
                    if Whos_turn == Pozitie :
                        Mithril += M_Yield
                        Flerovium += F_Yield
                        PlayTurnSound(0)
                    else:
                        PlayTurnSound(1)
                    timer = turn_time
                    units_healed = []   #a vector to store all units healed. Hospital effects don't stack
                    for caster in caster_controllables_vec: #For every caster, call it's function. Because of time and internal issues, the only caster is the hospital.
                        caster.call_special_function([caster, controllables_vec, units_healed])
                    if len(units_healed) != 0 :
                        Turn_Actions.append(("healed_units",units_healed))
                    del units_healed    
                    flash = 255
                    Confirmatii_timer = 0
                    if TileClass.full_bright == False :
                        refresh_map()
                    canRenderMinimap = True
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
                    while   Whos_turn >= len(playeri) or colorTable[map_locations[Whos_turn]] == None :
                        if Whos_turn >= len(playeri) :
                            Whos_turn = 0
                        if colorTable[map_locations[Whos_turn]] == None :
                            Whos_turn += 1 
                    if Whos_turn == Pozitie :
                        Mithril += M_Yield
                        Flerovium += F_Yield
                        PlayTurnSound(0)
                    else:
                        PlayTurnSound(1)
                    timer = turn_time
                    units_healed = []   #a vector to store all units healed. Hospital effects don't stack
                    for caster in caster_controllables_vec: #For every caster, call it's function. Because of time and internal issues, the only caster is the hospital.
                        caster.call_special_function([caster, controllables_vec, units_healed])
                    if len(units_healed) != 0 :
                        Turn_Actions.append(("healed_units",units_healed))
                    del units_healed    
                    flash = 255
                    timer_notification_sent = False
                    next_turn = False
                    if TileClass.full_bright == False :
                        refresh_map()
                    canRenderMinimap = True

            selected_tile_check()

        #The event loop
        for event in pygame.event.get():
            if event.type == SWAP_TO_NORMAL:
                if lastPositionForRendering != None :
                    refresh_map([lastPositionForRendering])
                    lastPositionForRendering = None

            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    left_click_holding = False
                    if Slider_Got == True:
                        Slider_Got = False

            elif event.type == pygame.MOUSEBUTTONDOWN  :
                press_coordonaits = event.pos 
                #daca apesi click stanga
                if event.button == 1 :
                    left_click_holding = True
                    #Se verifica daca apasa butonul de chat
                    if Escape_tab == False and SHOW_UI == True and press_coordonaits[1] <= 75  and press_coordonaits[0] >= WIDTH -75 :
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
                    elif Escape_tab == False and SHOW_UI == True and Chat_window == True :
                        if press_coordonaits[0] < (WIDTH-260)/2 + 265 :
                            Chat_window = False
                            writing_in_chat = False
                            message = ""
                            chat_scroll = 0
                        elif press_coordonaits[1] >= HEIGHT - 50 and press_coordonaits[0] >= (WIDTH-260)/2 + 265 :
                            writing_in_chat = True
                        else :
                            writing_in_chat = False
                    #Detecteaza daca a apasat butonul de End Turn
                    elif Escape_tab == False and SHOW_UI == True and Whos_turn == Pozitie and press_coordonaits[0]>(WIDTH-260)/2 and press_coordonaits[0]<(WIDTH-260)/2 +260 and press_coordonaits[1]>HEIGHT*2/25 and press_coordonaits[1]<HEIGHT*2/25 + 40 :
                        timer = 0 
                        if Role == "host" :
                            Transmit_to_all.append((("Force_end_turn",None),None))
                        else :
                            data_send = pickle.dumps(("Force_end_turn",None))
                            data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                            Connection.send(data_send)
                    #detecteaza daca playeru apasa un tile vizibil
                    elif Escape_tab == False and (SHOW_UI == False or( press_coordonaits[1] > HEIGHT/25 and (press_coordonaits[0] >= (WIDTH-260)/2 and press_coordonaits[0] <= (WIDTH-260)/2 + 260 and (press_coordonaits[1] <= HEIGHT*2/25 +5 or (Whos_turn == Pozitie and press_coordonaits[1] <= HEIGHT*2/25 + 40 )) )==0 and (press_coordonaits[1] > HEIGHT*2/3 and press_coordonaits[0] < HEIGHT/3)==0 and ((press_coordonaits[0]<(WIDTH-260)/2 + 260 and Chat_window == True) or Chat_window == False) and( selected_tile[0]==None or (press_coordonaits[1] < HEIGHT*4/5-5 and (tile_empty==False or (press_coordonaits[0]>WIDTH-HEIGHT/3 and press_coordonaits[1]>HEIGHT*2/3-60)==0 ))))) :
                        x_layer = (press_coordonaits[0] + CurrentCamera.x) // current_tile_length 
                        y_layer = (press_coordonaits[1] + CurrentCamera.y) // current_tile_length
                        if x_layer >= 0 and x_layer < tiles_per_row:
                            if y_layer >= 0 and y_layer < rows:
                                enlighted_surface = draw_enlighted_tiles()
                                selected_controllable = None
                                if selected_tile[0] == None or (selected_tile[0] == x_layer and selected_tile[1] == y_layer)==0 : 
                                    selected_tile = [x_layer,y_layer]
                                    if tiles[y_layer][x_layer].structure == None and tiles[y_layer][x_layer].unit == None and tiles[y_layer][x_layer].collidable == False :
                                        if tile_empty != True or tiles[y_layer][x_layer].ore != None :
                                            tile_empty = True
                                            Element_selectat = None
                                        if tiles[y_layer][x_layer].ore != None :
                                            if construction_tab != "Mines" :
                                                construction_tab = "Mines"
                                                Element_selectat = None
                                        elif construction_tab != "Structures" and construction_tab != "Units" :
                                            construction_tab = "Structures"
                                            Element_selectat = None
                                    else : 
                                        Element_selectat = None
                                        tile_empty=False
                                        #daca tile_ul are o strucutra sau unitate ii salveaza imaginea pentru afisare
                                        if tiles[selected_tile[1]][selected_tile[0]].unit != None and  (tiles[selected_tile[1]][selected_tile[0]].structure == None or (tiles[selected_tile[1]][selected_tile[0]].structure.name == "Bunker" and tiles[selected_tile[1]][selected_tile[0]].structure.owner == map_locations[Pozitie])) :
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
                                            try :
                                                large_img_element_afisat = pygame.image.load('Assets/Structures/' + structure.texture)
                                            except :
                                                large_img_element_afisat = pygame.image.load('Assets/Mines/' + structure.texture)
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
                                            tile_empty = False
                                            Element_selectat = None
                                else :
                                    selected_tile = [None,None]
                    #detecteaza daca playeru a schimbat coinstruction tabul
                    elif Escape_tab == False and SHOW_UI == True and press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] <= HEIGHT*2/3 -5 and press_coordonaits[1] >= HEIGHT*2/3 -55 :
                        Element_selectat = None
                        construction_tab_scroll = 0
                        if construction_tab == "Structures" :
                            construction_tab = "Units"
                        elif construction_tab == "Units" :
                            construction_tab = "Structures"
                    #detecteaza daca playerul a apasat un element din construction_tab
                    elif Escape_tab == False and SHOW_UI == True and press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3 :
                        if construction_tab == "Structures" :
                            elements = len(structures)
                        else :
                            elements = len(units)
                        for i in range(math.ceil(elements/3)) :
                             y_rand = HEIGHT*2/3 +10 + i*70 + i*10 - C_menu_scroll
                             if y_rand + 70 > HEIGHT*2/3 :
                                 if press_coordonaits[1] >= y_rand and press_coordonaits[1] <= y_rand+70 :
                                     for j in range(min(3,elements-i*3)) :
                                         x_coloana = WIDTH-HEIGHT/3+5 + j*70 + (j + 0.5)*spatiu_intre
                                         if press_coordonaits[0] >= x_coloana and press_coordonaits[0] <= x_coloana + 70 :
                                             Element_selectat = i*3 + j
                                             if construction_tab == "Structures" :
                                                large_img_element_afisat = pygame.transform.scale(structures[Element_selectat],(HEIGHT/5 -50,HEIGHT/5 -50))
                                             elif construction_tab == "Units" :
                                                large_img_element_afisat = pygame.transform.scale(units[Element_selectat],(HEIGHT/5 -50,HEIGHT/5 -50))
                                             else :
                                                 large_img_element_afisat = pygame.transform.scale(mines[Element_selectat],(HEIGHT/5 -50,HEIGHT/5 -50))
                                     break
                    #detecteaza daca s-a apasat butonul de Build/recruit
                    elif Escape_tab == False and Win_condition == 0 and SHOW_UI == True and Create_Button.on_click(event) and can_build == True :
                        Create_Building()
                        selected_tile_check()
                        can_build = False
                    #verifica daca playerul a apasat butonul de refund
                    elif Escape_tab == False and Win_condition == 0 and Refund_Button.on_click(event) and tile_empty == False and refund_bool :
                        refund_entity()
                        selected_tile_check()
                        refund_bool = False
                    #verifica daca apasa butonul de repair
                    elif Escape_tab == False and Win_condition == 0 and Repair_Button.on_click(event) and tile_empty == False and repair_bool and aford_repair == True :
                        repair_building()
                        repair_bool = False
                    elif Escape_tab == True :
                        if Escape_Button.on_click(event) :
                            if Role == "host" :
                                if sent_reaquest == False :
                                    return_lobby = True
                                    #trimite tuturor playerilor ca am trecut la urmatoru stage
                                    data_send = pickle.dumps(("return_to_lobby",None))
                                    data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                                    for i in range(len(CLIENTS)) :
                                        CLIENTS[i][0].send(data_send)
                                    sent_reaquest = True
                            else :
                                Connection.close()

                        elif Next_Button.on_click(event) :
                            #aici se va pune ce face butonul de next song
                            nimic = None
                        elif slider_rect[0]<=press_coordonaits[0] and slider_rect[0] + slider_rect[2]>=press_coordonaits[0] and slider_rect[1]<=press_coordonaits[1] and slider_rect[1] + slider_rect[3]>=press_coordonaits[1] :
                            Slider_Got = True
                #daca apesi click dreapta 
                if event.button == 3:

                    #daca ai o unitate selectata, incearca sa o muti  daca este tura playerului

                    if Escape_tab == False and Win_condition == 0 and selected_controllable != None and timer>0 and Whos_turn == Pozitie :
                    
                        #!!WARNING!!: Huge line of code ahead! Proceed with extreme caution! Effects include dizziness, headaches, disorientation and sudden suicidal impulses!
                    
                        if SHOW_UI == False or( press_coordonaits[1] > HEIGHT/25 and (press_coordonaits[0] >= (WIDTH-260)/2 and press_coordonaits[0] <= (WIDTH-260)/2 + 260 and (press_coordonaits[1] <= HEIGHT*2/25 +5 or (Whos_turn == Pozitie and press_coordonaits[1] <= HEIGHT*2/25 + 40 )) )==0 and (press_coordonaits[1] > HEIGHT*2/3 and press_coordonaits[0] < HEIGHT/3)==0 and ((press_coordonaits[0]<(WIDTH-260)/2 + 260 and Chat_window == True) or Chat_window == False) and( selected_tile[0]==None or (press_coordonaits[1] < HEIGHT*4/5-5 and (tile_empty==False or (press_coordonaits[0]>WIDTH-HEIGHT/3 and press_coordonaits[1]>HEIGHT*2/3-60)==0 )))) :

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
                                        selected_tile_check()

                                    if type(selected_controllable) == Units.Unit and selected_controllable.canAttack == True:
                                        tile = tiles[y_layer][x_layer]
                                        hitinformation = None   #The Attack function returns a tuple: has hit an enemy and the absolute value (abs) of damage it did
                                        target = None
                                        if tile.structure != None:
                                            target = tile.structure
                                            HP_target = target.HP
                                            owner_target = target.owner
                                            if target.name == "Kernel" :
                                                backup_matrix = copy.deepcopy(tiles)
                                                color_owner = colorTable[target.owner]
                                            hitinformation = selected_controllable.Attack(tile.structure)
                                        elif tile.unit != None:
                                            target = tile.unit
                                            HP_target = target.HP
                                            owner_target = target.owner
                                            hitinformation = selected_controllable.Attack(tile.unit)
                                        if hitinformation and hitinformation[0] == True and target != None:
                                            selected_controllable.canAttack = False
                                            target.took_damage = True
                                            
                                            if target.HP <= 0:
                                                if tile.structure != None :
                                                    if target.name == "Kernel" :
                                                        Turn_Actions.append(("damaged_entity","structure",(x_layer,y_layer),-(selected_controllable.attack-target.defence),selected_controllable.position,True,target.name,HP_target,owner_target,backup_matrix,color_owner))
                                                    else :
                                                        Turn_Actions.append(("damaged_entity","structure",(x_layer,y_layer),-(selected_controllable.attack-target.defence),selected_controllable.position,True,target.name,HP_target,owner_target,None))
                                                else :
                                                    Turn_Actions.append(("damaged_entity","unit",(x_layer,y_layer),-(selected_controllable.attack-target.defence),selected_controllable.position,True,target.name,HP_target,owner_target,None))

                                                vec = delete_entity(target)
                                                refresh_map(vec)
                                            else:
                                                if tile.structure != None :
                                                    Turn_Actions.append(("damaged_entity","structure",(x_layer,y_layer),-(selected_controllable.attack-target.defence),selected_controllable.position,False))
                                                else :
                                                    Turn_Actions.append(("damaged_entity","unit",(x_layer,y_layer),-(selected_controllable.attack-target.defence),selected_controllable.position,False))
                                                refresh_map([target.position])
                                            lastPositionForRendering = target.position
                                            pygame.time.set_timer(SWAP_TO_NORMAL, 200)


                #daca dai scrol in sus
                if  event.button == 4 :
                    if Escape_tab == False and SHOW_UI == True and Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265 and len(chat_archive) > 30 :
                        chat_scroll = chat_scroll +1
                        if chat_scroll > len(chat_archive) - 31:
                            chat_scroll = len(chat_archive) - 31
                    elif Escape_tab == False and SHOW_UI == True and press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3  :
                        construction_tab_scroll = construction_tab_scroll + 1
                        if construction_tab == "Structures" and construction_tab_scroll > math.ceil(len(structures)/3) -3 :
                            construction_tab_scroll = math.ceil(len(structures)/3) -3
                        elif construction_tab == "Units" and construction_tab_scroll > math.ceil(len(units)/3) -3 :
                            construction_tab_scroll = math.ceil(len(units)/3) -3
                        if construction_tab_scroll < 0:
                            construction_tab_scroll = 0
                        
                #daca dai scrol in jos
                elif event.button == 5 :
                    if Escape_tab == False and SHOW_UI == True and Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265 :
                        chat_scroll = chat_scroll - 1
                        if chat_scroll < 0 :
                            chat_scroll = 0
                    elif Escape_tab == False and SHOW_UI == True and press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3  :
                        construction_tab_scroll = construction_tab_scroll - 1
                        if construction_tab_scroll < 0 :
                            construction_tab_scroll = 0

                #Zoom si check_boundary pentru camera.
                modifier = 0
                if Escape_tab == False and ( SHOW_UI == False or (Chat_window == True and press_coordonaits[0] >= (WIDTH-260)/2 + 265) == 0 and (press_coordonaits[0]> WIDTH-HEIGHT/3 and press_coordonaits[1] >= HEIGHT*2/3 and selected_tile[0] !=None and tile_empty == True) == 0) :
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

                    elif event.unicode.lower() == 'm':  #Test some music playin
                        PlayRandomMusic()

                    elif event.unicode.lower() == 'l':  #Enable/Disable GUIs
                        if SHOW_UI   :
                            SHOW_UI = False  
                        else :
                            SHOW_UI = True

                    elif event.key == pygame.K_ESCAPE :
                        if Escape_tab == False :
                            Escape_tab = True
                            selected_tile = (None,None)
                        else :
                            Escape_tab = False
                            Slider_Got = False

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

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and Slider_Got == True :
                Slider_Got = False

        #ctrl_z verify
        if pygame.key.get_pressed()[pygame.K_z]==False :
            Ctrl_zeed = False

        x_pos = pygame.mouse.get_pos()[0]
        y_pos = pygame.mouse.get_pos()[1]

        if Escape_tab == False :
            if x_pos == 0:
                CurrentCamera.x -= CurrentCamera.camera_movement
            if y_pos == 0:
                CurrentCamera.y -= CurrentCamera.camera_movement
            if x_pos == WIDTH - 1:
                CurrentCamera.x += CurrentCamera.camera_movement
            if y_pos == HEIGHT - 1:
                CurrentCamera.y += CurrentCamera.camera_movement

        if x_pos > 0 and x_pos < HEIGHT // 3 and y_pos < HEIGHT and y_pos > 2 * HEIGHT // 3 and SHOW_UI == True and left_click_holding == True:
            #sizeY = int(HEIGHT / 3 * HEIGHT / current_tile_length / rows)
            X = x_pos
            Y = y_pos - 2 * HEIGHT // 3
            size_y  = int(HEIGHT / 3 * HEIGHT / current_tile_length / rows)
            size_x  = int(HEIGHT / 3 * WIDTH / current_tile_length / rows)
            world_y = int((Y - size_y / 2) * rows * current_tile_length * 3 / HEIGHT)
            world_x = int((X - size_x / 2) * tiles_per_row * current_tile_length * 3 / HEIGHT)

            CurrentCamera.x = world_x
            CurrentCamera.y = world_y

        CurrentCamera.Check_Camera_Boundaries()
        #volume slider modify
        if Slider_Got == True :
           slider_rect[0] = pygame.mouse.get_pos()[0] -12
           if slider_rect[0] < Escape_menu_part[0]+50 :
                slider_rect[0] = Escape_menu_part[0]+50
           elif slider_rect[0] > Escape_menu_part[0] + Escape_menu_part[2]-50 -24 :
                slider_rect[0] = Escape_menu_part[0] + Escape_menu_part[2]-50 -24
           VOLUM = math.ceil(((slider_rect[0]-(Escape_menu_part[0]+50))/((Escape_menu_part[0] + Escape_menu_part[2]-50 -24) -(Escape_menu_part[0]+50)))*100)
           pygame.mixer.music.set_volume(VOLUM / 100)
           #if pygame.mixer.music.get_busy():
           #    pygame.mixer.music.play()

        #return to lobby check
        if Role == "client" and Confirmation == True :
            recv_from_server.join()
            run = False
        elif Role == "host" and sent_reaquest == True and  Confirmatii == len(Client_THREADS) :  
            while len(Client_THREADS) > 0 :
                Client_THREADS[0].join()
                Client_THREADS.pop(0)
            run = False


    #finalul functiei si returnarea variabilelor necesare care s-ar fi putut schimba
    time_thread.join()
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        return playeri,Pozitie 