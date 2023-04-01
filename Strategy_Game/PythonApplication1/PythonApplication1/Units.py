import pygame
import os
import TileClass
import math

default_path = 'Assets/Units/'
sound_path = 'Assets/Sound'

texture_names = []
textures = []
base_textures = []

damage_percent = 70/100
dead_percent = 90/100


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

unit_attack_range_color = (235, 0, 0)

predefined_Units = {   
                #HP, MaxHp, attack, defence, range, move_range, fog_range, price (Mithril, Flerovium, Supply), Refund_percent
    "Marine" :  [5, 5, 2, 0, 4, 4, 5, (6,0,1), 60/100],
    "Phantom" : [3, 3, 6, 1, 6, 8, 10, (10,0,2), 55/100],
    "Phlegm" :  [7, 7, 8, 1, 2, 4, 4, (12,0,1), 60/100],
    "Pounder":  [4, 4, 20, 1, 11, 2, 3, (20,6,2), 20/100],
    "Tank" :    [18, 18, 8, 3, 6, 6, 7, (30,4,3), 35/100],
    "XGoliath": [40, 40, 12, 4, 7, 4, 5, (60,10,6), 20/100],

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

        self.took_damage = False

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

    def Draw_AOE(self, screen, size, offset):   #Draw the area range
        if self.range != 0:
            pygame.draw.circle(screen, unit_attack_range_color, ((self.position[0] + 0.5) * size - offset[0], (self.position[1] + 0.5) * size - offset[1]), self.range * size, 2)

    def Attack(self, target):
        if target.owner != self.owner:  #You can only attack enemy units
            inrange = math.sqrt((self.position[0] - target.position[0]) ** 2 + (self.position[1] - target.position[1]) ** 2) <= self.range
            if inrange == True:
                target.ModifyHealth(min(-(self.attack - target.defence), -1))
                return (inrange, (self.attack - target.defence))
        return (False, None)    

    def ModifyHealth(self, value):
        if self.HP + value > self.MaxHP:
            self.HP = self.MaxHP
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
                    dark.set_at((i,j), (153, 0, 0, damage_percent * 255))

        if special_blit == False:
            if TileClass.full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and not (self.position in visible_tuple[1]):
                image.fill(TileClass.darkness)
            if self.took_damage:
                self.took_damage = False
                image.blit(dark,(0,0)) 
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))
        else:
            image = pygame.transform.scale(image, size)
            dark = pygame.transform.scale(dark, size)
            if self.took_damage:
                self.took_damage = False
                image.blit(dark,(0,0))
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))