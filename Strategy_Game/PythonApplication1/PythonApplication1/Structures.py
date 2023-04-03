import pygame
import os
import TileClass
import Units
import math

default_path = 'Assets/Structures/'
sound_path = 'Assets/Sound'

texture_names = []
textures = []
base_textures = []

damage_percent = 70/100
dead_percent = 90/100

#VARIABLES FOR STRUCTURES
hospital_heal = 2   #HP per end turn to each unit in range of hospital(healing_point)
hospital_circle_color = (0,204,204)     #Color of the circle drawn if a hospital is selected.

for img in os.listdir(default_path):    #Load all images.
    texture_names.append(img)
    textures.append(pygame.image.load(default_path + img))
    base_textures.append(pygame.image.load(default_path + img))

default_path = "Assets/Mines/"
for img in os.listdir(default_path):    #Load all images.
    texture_names.append(img)
    textures.append(pygame.image.load(default_path + img))
    base_textures.append(pygame.image.load(default_path + img))
default_path = "Assets/Structures/"

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture

last_index = len(texture_names)

#Special custom functions for structures. SpecialFunction attribute must be EXACTLY the same name as the function name.
def heal_units(val_list):
    struct = val_list[0]
    controllables = val_list[1]
    for thing in controllables:
        if type(thing) == Units.Unit and thing not in val_list[2]:
            if math.sqrt((struct.position[0] - thing.position[0]) ** 2 + (struct.position[1] - thing.position[1]) ** 2) <= struct.AOE:
                thing.ModifyHealth(hospital_heal)
                val_list[2].append(thing)

predefined_structures = {   
                        #HP, MaxHp, Area_of_effect(block radius), defence, canShareSpace, fog_range, TrueSight, Price (Mithril, Flerovium), Refund_percent, SpecialFunction, (Mithril_rate, Flerovium_rate)
    "Barricade" :       [10, 10, 0, 4, False, 2, False, (10, 0), 60/100, None, (None, None)],
    "Bunker" :          [30, 30, 0, 2, True, 3, False, (20, 2), 35/100, None, (None, None)],
    "Cache" :           [15, 15, 0, 0, False, 3, False, (10, 0), 70/100, None, (None, None)],
    "Healing_Point" :   [15, 15, 5, 1, False, 3, False, (40, 5), 30/100, "heal_units", (None, None)],
    "Node" :            [6, 6, 0, 1, False, 2, False, (3, 0), 75/100, None, (None, None)],
    "Radar" :           [8, 8, 0, 0, False, 11, True, (20, 3), 20/100, None, (None, None)],
    #De acum kernel va trebui sa stea pe ultima pozitie
    "Mine_1" :          [15, 15, 0, 1, False, 3, False, (35,0), 60/100, None, (7, 3)],
    "Mine_2" :          [10, 10, 0, 0, False, 2, False, (10,0), 70/100, None, (4, 0)],
    "Kernel" :          [100, 100, 0, 3, False, 5, False, (2000,1000), 0, None, (None, None)]

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

        self.took_damage = False

        vec = predefined_structures[name]

        self.texture = name + ".png"
        self.HP = vec[0]
        self.MaxHP = vec[1]
        self.AOE = vec[2]   #Area of effect
        self.defence = vec[3]   #Damage reduction
        self.canShareSpace = vec[4]     #If an allied unit can stay inside the structure. Usefull for a bunker.
        self.fog_range = vec[5]      #How much can the structure see
        self.TrueSight = vec[6]     #If True, you can see trough walls.

        self.price = vec[7]
        self.refund_percent = vec[8]

        self.special_function = vec[9]
        self.Yield = vec[10]

    def call_special_function(self, value_list):    #Call the special function
        if self.special_function != None:
            func = globals()[self.special_function]
            func(value_list)

    def ModifyHealth(self, value):
        if self.HP + value > self.MaxHP:
            self.HP = self.MaxHP
            self.took_damage == True
        else:
            self.HP += value
            self.took_damage == True

    def Draw_AOE(self, screen, size, offset):   #Draw the area of efect of a structure
        if self.AOE != 0:
            pygame.draw.circle(screen, hospital_circle_color, ((self.position[0] + 0.5) * size - offset[0], (self.position[1] + 0.5) * size - offset[1]), self.AOE * size, 1)

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