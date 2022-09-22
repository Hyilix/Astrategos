import pygame 
import os 
import socket
import pickle
import threading

White = (255,255,255)

def lobby(WIN,WIDTH,HEIGHT,FPS,Role,name,Connection) :
    pygame.init()

    playeri = [["",None,0],["",None,0],["",None,0],["",None,0]]
    Font = pygame.font.Font(None, 40)
    Cerc_draw = []
    Text_draw = []

    y = HEIGHT/2
    diametru = (WIDTH - 50*3)/6
    for i in range(1,5) :
        x = diametru*i + diametru/2 + 50 *(i-1)
        Cerc_draw.append((x,y))

    def draw_window () :
        WIN.fill((255,255,255))
        for i in range( len(Cerc_draw)) :
            pygame.draw.circle(WIN,(225, 223, 240),Cerc_draw[i],diametru/2)
            if playeri[i][0] != "" :
                pygame.draw.circle(WIN,White,Cerc_draw[i],diametru/2 - 10)
                WIN.blit(playeri[i][1],Text_draw[i])

        pygame.display.update()
        


    if Role == "host" :
        playeri[0][0] = name
        playeri[0][1] = Font.render(playeri[0][0], True, (0,0,0))
        text_rect = playeri[0][1].get_rect()
        text_rect.center = (diametru + diametru/2,HEIGHT/2 - diametru/2-30)
        Text_draw.append(text_rect)

    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)
        
        draw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)