import pygame
import os

default_path = 'Assets/Structures/'
texture_names = []
textures = []
base_textures = []

structure_prices_dict = {   #Prices for all structures: first and second ore
    "Mine_1" : (4,0),
    "Mine_2" : (10,0),
    "Mine_3" : (21,1),
    "Bunker_1" : (20,0),
    "Bunker_2" : (42,2),
    "Radar_1" : (11,0),
    "Radar_2" : (28,1),
    "Pylon" : (15,0)
}

for img in os.listdir(default_path):    #Load all images.
    texture_names.append(img)
    textures.append(pygame.image.load(default_path + img))
    base_textures.append(pygame.image.load(default_path + img))

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture

class Core():
    def __init__(self, position, owner):
        self.position = position    #The position of the tile it's sitted.
        self.owner = owner          #The owner of the unit.

        self.texture = "Core" + ".png"
        self.HP = 100
        self.attack = 2
        self.defence = 3
        self.canShareSpace = False
        self.fog_range = (2,2)      #How much can the structure see

    def DrawImage(self, screen, size):
        screen.blit(textures[texture_names.index(self.texture)], (self.position[0] * size[0], self.position[1]  * size[1]))