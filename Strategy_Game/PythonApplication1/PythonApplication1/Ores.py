import pygame
import os
import TileClass

default_path = 'Assets/Ores/'
texture_names = []
textures = []
base_textures = []

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

last_index = len(texture_names)

class Ore():
    def __init__(self, position, image_name, tier):
        self.position = position        #The position of the tile it's sitted.
        self.image_name = image_name    #The name of the image used.
        self.tier = tier                #The tier of the resource.  (1 / 2)

        self.texture = self.image_name + ".png"

    def DrawImage(self, screen, size, special_blit = False, visible_tuple = None):
        image = textures[texture_names.index(self.texture)].copy()
        dark = pygame.Surface(image.get_size()).convert_alpha()
        dark.fill((0, 0, 0, 0))

        for i in range(image.get_width()):
            for j in range(image.get_height()):
                if image.get_at((i,j)) != (0,0,0,0):
                    dark.set_at((i,j), (0, 0, 0, TileClass.darken_percent * 255))

        if special_blit == False:
            #img = textures[texture_names.index(self.texture)]
            if TileClass.full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and not (self.position in visible_tuple[1]):
                image.fill(TileClass.darkness)
            elif TileClass.full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and (self.position in visible_tuple[1]):
                image.blit(dark,(0,0))
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))
        else:

            image = pygame.transform.scale(image, size)
            dark = pygame.transform.scale(dark, size)
            if TileClass.full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and not (self.position in visible_tuple[1]):
                image.fill((0,0,0))
            elif TileClass.full_bright == False and visible_tuple and not (self.position in visible_tuple[0]) and (self.position in visible_tuple[1]):
                image.blit(dark,(0,0))
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))