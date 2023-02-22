import pygame
import os

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

colorTable = {  #Table for assigning each controller with a color. In editor it's set, but in game it will get from lobby.
    0 : (64,64,64),
    1 : (204,0,0),
    2 : (0,0,204),
    3 : (0,204,0),
    4 : (204,204,0)
    }

#load all textures.
default_path = 'Assets/Tiles/'
texture_names = []
textures = []
base_textures = []
avalible_textures = []

base_texture_length = 32

image_class_familly = {}

for img in os.listdir(default_path):
    if img[-4:] == '.png':
        if img[0:8] != "A-simple":
            avalible_textures.append(img)

        texture_names.append(img)
        textures.append(pygame.image.load(default_path + img))
        base_textures.append(pygame.image.load(default_path + img))
    else:
        new_names = []
        new_textures = []
        new_base_textures = []
        for sub_img in os.listdir(default_path + img + '/'):
            new_names.append(sub_img)
            myTexture = pygame.image.load(default_path + img + '/' + sub_img)
            new_textures.append(myTexture)
            new_base_textures.append(myTexture)

        image_class_familly[img] = [new_names, new_textures, new_base_textures]

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture

empty_image_name = avalible_textures[0]

simple_textures_enabled = True

simple_textures_dict = {
    "Land" : "A-simple-land",
    "Wall" : "A-simple-wall",
    "Ore1" : "A-simple-ore1",
    "Ore2" : "A-simple-ore2"
    }

last_index = len(avalible_textures)

class Tile:
    def __init__(self, position, collidable, image_class, image_name, ore, unit, structure):
        self.position = position            #a tuple for the position
        self.collidable = collidable        #check if a unit can be placed there (ex. a wall or water)
        self.image_class = image_class
        self.image_name = image_name        #the name of the image. Used by texture_names.
        self.ore = ore                      #The ore oject.
        self.unit = unit                    #store what unit is occupying this tile
        self.structure = structure          #store what structure is placed on this tile

    def DrawImage(self, screen, size, special_blit = False):
        if simple_textures_enabled == True:
            if special_blit == False:
                screen.blit(textures[texture_names.index(self.image_name)], (self.position[0] * size[0], self.position[1]  * size[1]))
            else:
                img = textures[texture_names.index(self.image_name)].copy()
                img = pygame.transform.scale(img, size)
                screen.blit(img, (self.position[0] * size[0], self.position[1]  * size[1]))
        else:
            key = ""
            if self.ore != None:
                if self.ore.tier == 1:
                    key = simple_textures_dict["Ore1"]
                elif self.ore.tier == 2:
                    key = simple_textures_dict["Ore2"]
            elif self.collidable == True:
                key = simple_textures_dict["Wall"]
            elif self.collidable == False:
                key = simple_textures_dict["Land"]
            screen.blit(textures[texture_names.index(key + ".png")], (self.position[0] * size[0], self.position[1]  * size[1]))
            
        if self.structure != None:
            self.structure.DrawImage(screen, size, colorTable)
        if self.unit != None:
            self.unit.DrawImage(screen, size, colorTable)
        if self.ore != None and simple_textures_enabled == True:
            self.ore.DrawImage(screen, size)