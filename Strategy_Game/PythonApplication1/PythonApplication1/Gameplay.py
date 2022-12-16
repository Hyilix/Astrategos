import pygame 
import os 
import socket
import pickle
import threading


pygame.init()

run = True

def gameplay (WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client,map_name) :
    global run

    #adresa pentru txt-ul hartii pe care se afla playeri
    map_adres = "Maps\info" + map_name + ".txt"


    def draw_window () :
        pygame.display.update()

    while run == True :
        draw_window()

    #finalul functiei si returnarea variabilelor necesare care s-ar fi putut schimba
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        return playeri,Pozitie 

