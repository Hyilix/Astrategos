import pygame
import os
import TileClass

default_path = 'Assets/Structures/'
texture_names = []
textures = []
base_textures = []

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

last_index = len(texture_names)

predefined_structures = {   #HP, MaxHp, Area_of_effect(block radius), defence, canShareSpace, fog_range, Price (Mithril, Flerovium)
    "Kernel" : [100, 100, 5, 3, False, 7, (0,0)],
    "Node" : [10, 10, 4, 0, False, 3, (3,0)],
    }

def BuildStructure(index, position, owner):
    found = None
    new_index = 0
    for i in predefined_structures.keys():
        if index == new_index:
            found = i
            break
        new_index += 1
    new_struct = Structure(found, position, owner)
    return new_struct

class Structure():
    def __init__(self, name, position, owner):
        self.position = position    #The position of the tile it's sitted.
        self.owner = owner          #The owner of the unit.
        self.name = name            #The structure.

        vec = predefined_structures[name]

        self.texture = name + ".png"
        self.HP = vec[0]
        self.MaxHP = vec[1]
        self.AOE = vec[2]   #Area of effect
        self.defence = vec[3]   #Damage reduction
        self.canShareSpace = vec[4]     #If an allied unit can stay inside the structure. Usefull for a bunker.
        self.fog_range = vec[5]      #How much can the structure see

        self.price = vec[6]

    def DrawImage(self, screen, size, colorTable, special_blit = False, visible_tuple = None):
        image = textures[texture_names.index(self.texture)].copy()
        dark = pygame.Surface(image.get_size()).convert_alpha()
        dark.fill((0, 0, 0, 0))

        for i in range(image.get_width()):
            for j in range(image.get_height()):
                if image.get_at((i,j)) == (1,1,1):
                    image.set_at((i,j), colorTable[self.owner])
                if image.get_at((i,j)) != (0,0,0,0):
                    dark.set_at((i,j), (0, 0, 0, TileClass.darken_percent * 255))

        if special_blit == False:
            if TileClass.full_bright == False and not (self.position in visible_tuple[0]) and not (self.position in visible_tuple[1]):
                image.fill(TileClass.darkness)
            elif TileClass.full_bright == False and not (self.position in visible_tuple[0]) and (self.position in visible_tuple[1]):
                image.blit(dark,(0,0))
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))
        else:
            image = pygame.transform.scale(image, size)
            dark = pygame.transform.scale(dark, size)
            if TileClass.full_bright == False:
                image.blit(dark, (0,0))
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))