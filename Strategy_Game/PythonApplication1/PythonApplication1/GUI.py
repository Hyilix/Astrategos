import pygame
import TileClass

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

GUIs_enabled = True

texture_size = 64
texture_distance = 10
max_x_pos = 4
max_y_pos = TileClass.last_index // max_x_pos

Texture_x_size = (texture_size + texture_distance * 3) * max_x_pos
print(Texture_x_size)

#Surfaces for Editor GUI
TextureSurface = pygame.Surface((Texture_x_size, texture_size * 2 * max_y_pos * texture_distance), pygame.SRCALPHA)
ToolsSurface = pygame.Surface((WIDTH // 5, HEIGHT))

def Initialize_GUIs():
    TextureSurface.convert_alpha()
    ToolsSurface.convert_alpha()

    TextureSurface.fill((0, 0, 0, 150))

    current_x = 0
    current_y = 0

    for image_name in TileClass.avalible_textures:
        cloned_image = pygame.transform.scale(TileClass.textures[TileClass.texture_names.index(image_name)], (texture_size, texture_size))
        TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
        if current_x >= max_x_pos:
            current_x = 0
            current_y += 1
        else:
            current_x += 1
