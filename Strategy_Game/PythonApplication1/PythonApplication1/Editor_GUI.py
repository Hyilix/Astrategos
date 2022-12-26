import pygame

import TileClass
import Structures
import Units
import Ores
import os
import button

font = pygame.font.Font('freesansbold.ttf', 256)
font_string = pygame.font.Font('freesansbold.ttf', 32)

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

GUIs_enabled = True

#print(pygame.font.get_fonts())

#Possible screens:
#-Tiles
#-Structures
#-Units
#-Ores
current_texture_screen = "Ores"

Tools_icon_size = 64

icons = []
icon_names = []
brush_icons = []
brush_names = []
ore_icons = []
ore_names = []

plus_brush = (0,0)
minus_brush = (0,0)

ore_tier_selection = True   #True -> tier 1    /    False -> tier 2

def toggle_selection():
    global ore_tier_selection
    ore_tier_selection = not ore_tier_selection
    print("CLICK")

for img in os.listdir('Assets/EditorToolBrushIcons/'):  #Load all brush icons
    image = pygame.image.load('Assets/EditorToolBrushIcons/' + img)
    image = pygame.transform.scale(image, (Tools_icon_size, Tools_icon_size))
    brush_icons.append(image)
    brush_names.append(img)

for img in os.listdir('Assets/EditorToolIcons/'):    #Load all icons
    icons.append(pygame.image.load('Assets/EditorToolIcons/' + img))
    icon_names.append(img)

for i in range(len(icons)):
    newTexture = pygame.transform.scale(icons[i], (Tools_icon_size, Tools_icon_size))
    icons[i] = newTexture

last_icons_index = len(icons)

texture_size = 64
texture_distance = 10
max_x_pos = 2
max_y_pos = TileClass.last_index // max_x_pos

Tools_icon_distance = 10
Tools_max_x_pos = 2
Tools_max_y_pos = last_icons_index // Tools_max_x_pos

Texture_x_size = (texture_size + texture_distance) * (max_x_pos + 1) + texture_distance
Tool_x_size = (Tools_icon_size + Tools_icon_distance) * (Tools_max_x_pos + 1) + Tools_icon_distance

#Surfaces for Editor GUI
TextureSurface = pygame.Surface((Texture_x_size, texture_size * 2 * max_y_pos * texture_distance), pygame.SRCALPHA)
ToolsSurface = pygame.Surface((Tool_x_size, HEIGHT), pygame.SRCALPHA)
PlacableSurface = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
PlacableButtons = []

def Initialize_Editor_GUIs():
    TextureSurface.convert_alpha()
    ToolsSurface.convert_alpha()
    PlacableSurface.convert_alpha()

def Draw_Textures_GUI(position):
    TextureSurface.fill((32, 32, 32, 150))

    current_x = 0
    current_y = 0

    if current_texture_screen == "Tiles":

        for image_name in TileClass.avalible_textures:
            cloned_image = pygame.transform.scale(TileClass.base_textures[TileClass.texture_names.index(image_name)], (texture_size, texture_size))
            if position != None:
                pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
            TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
            if current_x >= max_x_pos:
                current_x = 0
                current_y += 1
            else:
                current_x += 1

    elif current_texture_screen == "Structures":

        for image_name in Structures.texture_names:
            cloned_image = pygame.transform.scale(Structures.base_textures[Structures.texture_names.index(image_name)], (texture_size, texture_size))
            if position != None:
                pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
            TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
            if current_x >= max_x_pos:
                current_x = 0
                current_y += 1
            else:
                current_x += 1

    elif current_texture_screen == "Units":

        for image_name in Units.texture_names:
            cloned_image = pygame.transform.scale(Units.base_textures[Units.texture_names.index(image_name)], (texture_size, texture_size))
            if position != None:
                pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
            TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
            if current_x >= max_x_pos:
                current_x = 0
                current_y += 1
            else:
                current_x += 1

    elif current_texture_screen == "Ores":

        for image_name in Ores.texture_names:
            cloned_image = pygame.transform.scale(Ores.base_textures[Ores.texture_names.index(image_name)], (texture_size, texture_size))
            if position != None:
                pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
            TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
            if current_x >= max_x_pos:
                current_x = 0
                current_y += 1
            else:
                current_x += 1

def Draw_Tools_GUI(positions, brush_size):
    #Draw Tools
    PlacableSurface.fill((32, 32, 32, 0))
    ToolsSurface.fill((32, 32, 32, 150))

    current_x = 0
    current_y = 0

    for i in range(len(icons)):
        if positions != None:
            for position in positions:
               pygame.draw.rect(ToolsSurface, (255, 255, 0), (position[0] * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance - 5, position[1] * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance - 5, texture_size + 10, texture_size + 10), 5)
        
        ToolsSurface.blit(icons[i], (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance, current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance))
        if current_x >= max_x_pos:
            current_x = 0
            current_y += 1
        else:
            current_x += 1

    #Draw Brush Tools

    #First draw a text
    current_y += 1
    current_x = 1

    text1 = font_string.render("Brush Size", True, (230,230,230))
    textRect = text1.get_rect()
    textRect.center = (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + Tools_icon_size / 2,
                    current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + int(Tools_icon_size / 1.3))
    ToolsSurface.blit(text1, textRect)

    #Then draw the buttons

    current_y += 1
    current_x = 0

    ToolsSurface.blit(brush_icons[0], (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance, current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance))
    
    global minus_brush
    minus_brush = (current_x, current_y)

    current_x += 1 
    if brush_size != None:
        text = font.render(str(brush_size), True, (230,230,230))
        text = pygame.transform.smoothscale(text, (Tools_icon_size / 2 + Tools_icon_size * (brush_size > 9) / 2, Tools_icon_size))
        textRect = text.get_rect()
        textRect.x = current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + Tools_icon_size / 4 - Tools_icon_size / 4 * (brush_size > 9)
        textRect.y = current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance
        ToolsSurface.blit(text, textRect)

    current_x += 1
    
    global plus_brush
    plus_brush = (current_x, current_y)

    ToolsSurface.blit(brush_icons[1], (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance, current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance))

    #Draw Ores Tools

    if current_texture_screen == "Ores":
        current_y += 1
        current_x = 1

        #Draw Text
        
        text1 = font_string.render("Ore Tier", True, (230,230,230))
        textRect = text1.get_rect()
        textRect.center = (WIDTH - Texture_x_size - (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + Tools_icon_size / 2),
                        current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + int(Tools_icon_size / 1.3))
        PlacableSurface.blit(text1, textRect)

        #Draw button

        current_y += 1

        if len(PlacableButtons) == 0:
            new_button = button.Button( (WIDTH - Texture_x_size - Tools_icon_size - (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance),
                            current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance,
                            Tools_icon_size, Tools_icon_size),
                            (64,64,64,0),
                            toggle_selection,
                            **{"text": "1", "alternate_text": "2", "font": pygame.font.Font(None, 60),"font_color": (230,230,230), "border_color" : (64,64,64,0), "hover_color" : (160,160,160,255)}
                            )

            PlacableButtons.append(new_button)
