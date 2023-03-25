import pygame
import os

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

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

full_bright = False
darken_percent = .60    #Percentage of full black to use on partial visibility
darkness = (10,10,10)   #Color to use on non-visible tiles

show_walls = False

for img in os.listdir(default_path):
    if img[-4:] == '.png':
        avalible_textures.append(img)
        texture_names.append(img)
        textures.append(pygame.image.load(default_path + img).convert_alpha())
        base_textures.append(pygame.image.load(default_path + img).convert_alpha())

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture

empty_image_name = avalible_textures[0]

simple_textures_dict = {
    "Land" : "A-simple-land",
    "Wall" : "A-simple-wall",
    "Ore1" : "A-simple-ore1",
    "Ore2" : "A-simple-ore2"
    }

last_index = len(avalible_textures)

class Tile:
    def __init__(self, position, collidable, image_name, ore, unit, structure):
        self.position = position            #a tuple for the position
        self.collidable = collidable        #check if a unit can be placed there (ex. a wall or water)
        self.image_name = image_name        #the name of the image. Used by texture_names.
        self.ore = ore                      #The ore oject.
        self.unit = unit                    #store what unit is occupying this tile
        self.structure = structure          #store what structure is placed on this tile

    def DrawImage(self, screen, size, special_blit = False, visible_tuple = None):
        dark = pygame.Surface(size).convert_alpha()
        dark.fill((0,0,0, darken_percent * 255))

        if special_blit == False:   #Special blit resizes the texture on the spot and blits it, instead of blitting and resizing the map after.
            img = textures[texture_names.index(self.image_name)].copy()
            if full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and not (self.position in visible_tuple[1]):
                img.fill(darkness)
            elif full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and (self.position in visible_tuple[1]):
                img.blit(dark,(0,0))

            if show_walls == True:  #For editor
                if self.collidable == True:
                   darken = pygame.Surface(size).convert_alpha()
                   darken.fill((0,0,0, 0.9 * 255))
                   img.blit(darken,(0,0))

                if self.ore != None:
                    oreish = pygame.Surface(size).convert_alpha()
                    color = (76,0,153,0.6 * 255)
                    if self.ore.tier == 1:
                        color = (0,128,255,0.6 * 255)
                    oreish.fill(color)
                    img.blit(oreish,(0,0))

            screen.blit(img, (self.position[0] * size[0], self.position[1] * size[1]))
        else:
            img = textures[texture_names.index(self.image_name)].copy()
            img = pygame.transform.scale(img, size)
            if full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and not (self.position in visible_tuple[1]):
                img.fill((0,0,0))
            if full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and (self.position in visible_tuple[1]):
                img.blit(dark,(0,0))

            if show_walls == True:
                if self.collidable == True:
                   darken = pygame.Surface(size).convert_alpha()
                   darken.fill((0,0,0, 0.6 * 255))
                   img.blit(darken,(0,0))

                if self.ore != None:
                    oreish = pygame.Surface(size).convert_alpha()
                    color = (76,0,153,0.6 * 255)
                    if self.ore.tier == 1:
                        color = (0,128,255,0.6 * 255)
                    oreish.fill(color)
                    img.blit(oreish,(0,0))

            screen.blit(img, (self.position[0] * size[0], self.position[1] * size[1]))

        if self.ore != None:
            self.ore.DrawImage(screen, size, special_blit, visible_tuple)

        if (visible_tuple != None and self.position in visible_tuple[0]) or visible_tuple == None:  #If you can't see the tile, you can't see structures or units.
            if self.structure != None:
                if colorTable[self.structure.owner] == None:
                    del self.structure
                    self.structure = None
                else:
                    self.structure.DrawImage(screen, size, colorTable, special_blit, visible_tuple)
            if self.unit != None:
                if colorTable[self.unit.owner] == None:
                    del self.unit
                    self.unit = None
                else:
                    self.unit.DrawImage(screen, size, colorTable, special_blit, visible_tuple)