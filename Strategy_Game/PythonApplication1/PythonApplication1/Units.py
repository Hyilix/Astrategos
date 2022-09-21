import pygame
import os

default_path = 'Assets/Units/'
texture_names = []
textures = []
base_textures = []

structure_prices_dict = {   #Prices for all units: first and second ore, supply
    "Marine" : (4,0,1),
    "Specialist" : (6,0,2),
    "Recon" : (11,0,1),
    "Drone" : (13,0,3),
    "Tank" : (20,2,6),
    "Goliath" : (35,6,10)
}

for img in os.listdir(default_path):    #Load all images
    texture_names.append(img)
    textures.append(pygame.image.load(default_path + img))
    base_textures.append(pygame.image.load(default_path + img))

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture

class Marine():
    def __init__(self, position, owner):
        self.position = position    #The position of the tile it's sitted.
        self.owner = owner          #The owner of the unit.

        self.texture = "Marine" + ".png"
        self.HP = 5
        self.attack = 2
        self.defence = 3
        self.Range = 1
        self.fog_range = (1,1)      #How much can the unit see

    def DrawImage(self, screen, size, offset_x, offset_y, pos_x, pos_y):
        screen.blit(textures[texture_names.index(self.texture)], ((self.position[0] - pos_x) * size[0] - offset_x, (self.position[1] - pos_y) * size[1] - offset_y), (0, 0, size[0], size[1]))
