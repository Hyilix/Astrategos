import pygame
import os

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

    def DrawImage(self, screen, size, special_blit = False):
        if special_blit == False:
            screen.blit(textures[texture_names.index(self.texture)], (self.position[0] * size[0], self.position[1]  * size[1]))
        else:
            img = textures[texture_names.index(self.texture)].copy()
            img = pygame.transform.scale(img, size)
            screen.blit(img, (self.position[0] * size[0], self.position[1]  * size[1]))