import pygame
import os
import TileClass

default_path = 'Assets/Units/'
texture_names = []
textures = []
base_textures = []

for img in os.listdir(default_path):    #Load all images
    texture_names.append(img)
    image = pygame.image.load(default_path + img)
    textures.append(image)
    base_textures.append(image)

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture  

last_index = len(texture_names)

predefined_Units = {   
                #HP, MaxHp, attack, defence, range, move_range, fog_range, price (Mithril, Flerovium, Supply), Refund_percent
    "Marine" :  [5, 5, 2, 0, 2, 4, 5, (6,0,1), 60/100],
    "Phantom" : [7, 7, 4, 1, 5, 7, 9, (10,0,2), 55/100],
    "Tank" :    [20, 20, 8, 3, 3, 5, 6, (30,4,2), 35/100],

    }

def BuildUnit(index, position, owner):
    found = None
    new_index = 0
    for i in predefined_Units.keys():
        if index == new_index:
            found = i
            break
        new_index += 1
    new_struct = Unit(found, position, owner)
    return new_struct

class Unit():
    def __init__(self, name, position, owner):
        self.position = position    #The position of the tile it's sitted.
        self.owner = owner          #The owner of the unit.
        self.name = name            #The unit

        vec = predefined_Units[name]

        self.canMove = True
        self.canAttack = True

        self.texture = name + ".png"
        self.HP = vec[0]
        self.MaxHP = vec[1]
        self.attack = vec[2]
        self.defence = vec[3]
        self.range = vec[4]
        self.move_range = vec[5]
        self.fog_range = vec[6]      #How much can the unit see

        self.price = vec[7]
        self.refund_percent = vec[8]

    def ModifyHealth(self, value):
        if self.HP + value > self.MaxHP:
            self.HP = self.MaxHP
        elif self.HP + value < 0:
            self.HP = 0
        else:
            self.HP += value

    def MoveTo(self, position, path_vec, tiles):
        if position in path_vec:
            tiles[position[1]][position[0]].unit = self
            tiles[position[1]][position[0]].unit.position = tiles[position[1]][position[0]].position
            tiles[position[1]][position[0]].unit.canMove = False
            return True
        return False

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
            if TileClass.full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and not (self.position in visible_tuple[1]):
                image.fill(TileClass.darkness)
            elif TileClass.full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and (self.position in visible_tuple[1]):
                image.blit(dark,(0,0))
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))
        else:
            image = pygame.transform.scale(image, size)
            dark = pygame.transform.scale(dark, size)
            if TileClass.full_bright == False:
                image.blit(dark, (0,0))
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))