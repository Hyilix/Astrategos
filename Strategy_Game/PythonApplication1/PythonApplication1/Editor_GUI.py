import pygame

import TileClass
import Structures
import Units
import Ores
import os
import button

import math

font = pygame.font.Font('freesansbold.ttf', 256)
font_string = pygame.font.Font("Assets/Fonts/zektonregular.otf", 32)

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
current_texture_screen = "Tiles"

Tools_icon_size = 64

icons = []
icon_names = []
brush_icons = []
brush_names = []
ore_icons = []
ore_names = []

OreButtons = []
ControllerButtons = []

plus_brush = (0,0)
minus_brush = (0,0)

ore_tier_selection = True   #True -> tier 1    /    False -> tier 2
controller_selection = 0

def toggle_selection():
    global ore_tier_selection
    ore_tier_selection = not ore_tier_selection

def toggle_selection_controller(arg):
    global controller_selection
    if ControllerButtons[arg - 1].has_been_activated == False:
        controller_selection = 0

    else:
        for i in ControllerButtons:
            i.has_been_activated = False
        controller_selection = arg
        ControllerButtons[arg - 1].has_been_activated = True

    print(controller_selection)

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

texture_cap = (max_x_pos + 1) * int((HEIGHT * 9 / 10) / (texture_size + 2 * texture_distance))

tabs = math.ceil(TileClass.last_index / texture_cap)
current_tab = 1

max_y = texture_cap / (max_x_pos + 1)

Tools_icon_distance = 10
Tools_max_x_pos = 2
Tools_max_y_pos = last_icons_index // Tools_max_x_pos

Texture_x_size = (texture_size + texture_distance) * (max_x_pos + 1) + texture_distance
Tool_x_size = (Tools_icon_size + Tools_icon_distance) * (Tools_max_x_pos + 1) + Tools_icon_distance

#Surfaces for Editor GUI
TextureSurface = pygame.Surface((Texture_x_size, HEIGHT), pygame.SRCALPHA)
ToolsSurface = pygame.Surface((Tool_x_size, HEIGHT), pygame.SRCALPHA)
PlacableSurface = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)

last_tool_position = None

def Initialize_Editor_GUIs():
    TextureSurface.convert_alpha()
    ToolsSurface.convert_alpha()
    PlacableSurface.convert_alpha()

def Draw_Textures_GUI(position): 
    TextureSurface.fill((32, 32, 32, 150))

    current_x = 0
    current_y = 0

    comparison = 0
    if current_tab != tabs:
        comparison = texture_cap
    elif current_tab == tabs:
        comparison = TileClass.last_index - (tabs - 1) * texture_cap

    if current_texture_screen == "Tiles":
        for i in range((current_tab - 1) * texture_cap, (current_tab - 1) * texture_cap + comparison):
            image_name = TileClass.avalible_textures[i]
            if current_y < max_y:
                cloned_image = pygame.transform.scale(TileClass.base_textures[TileClass.texture_names.index(image_name)], (texture_size, texture_size))
                if position != None:
                    pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
                TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
                if current_x >= max_x_pos:
                    current_x = 0
                    current_y += 1
                else:
                    current_x += 1
            else: break

    comparison = 0
    if current_tab != math.ceil(Structures.last_index / texture_cap):
        comparison = texture_cap
    elif current_tab == math.ceil(Structures.last_index / texture_cap):
        comparison = Structures.last_index - (math.ceil(Structures.last_index / texture_cap) - 1) * texture_cap

    if current_texture_screen == "Structures":

        for i in range((current_tab - 1) * texture_cap, (current_tab - 1) * texture_cap + comparison):
            image_name = Structures.texture_names[i]
            cloned_image = pygame.transform.scale(Structures.base_textures[Structures.texture_names.index(image_name)], (texture_size, texture_size))
            if position != None:
                pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
            TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
            if current_x >= max_x_pos:
                current_x = 0
                current_y += 1
            else:
                current_x += 1

    comparison = 0
    if current_tab != math.ceil(Structures.last_index / texture_cap):
        comparison = texture_cap
    elif current_tab == math.ceil(Units.last_index / texture_cap):
        comparison = Units.last_index - (math.ceil(Units.last_index / texture_cap) - 1) * texture_cap

    if current_texture_screen == "Units":
        for i in range((current_tab - 1) * texture_cap, (current_tab - 1) * texture_cap + comparison):
            image_name = Units.texture_names[i]
            cloned_image = pygame.transform.scale(Units.base_textures[Units.texture_names.index(image_name)], (texture_size, texture_size))
            if position != None:
                pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
            TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
            if current_x >= max_x_pos:
                current_x = 0
                current_y += 1
            else:
                current_x += 1

    comparison = 0
    if current_tab != math.ceil(Ores.last_index / texture_cap):
        comparison = texture_cap
    elif current_tab == math.ceil(Ores.last_index / texture_cap):
        comparison = Ores.last_index - (math.ceil(Ores.last_index / texture_cap) - 1) * texture_cap

    if current_texture_screen == "Ores":

        for i in range((current_tab - 1) * texture_cap, (current_tab - 1) * texture_cap + comparison):
            image_name = Ores.texture_names[i]
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
    global last_tool_position
    last_tool_position = positions
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
            
        if len(OreButtons) == 0:
            OreButtons.append(
                button.Button( (WIDTH - Texture_x_size - Tools_icon_size - (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance),
                            current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance,
                            Tools_icon_size, Tools_icon_size),
                            (64,64,64,0),
                            toggle_selection,
                            **{"text": "1", "alternate_text": "2", "font": pygame.font.Font(None, 60),"font_color": (230,230,230), "border_color" : (64,64,64,0), "hover_color" : (160,160,160,255)}
                            )
                )

    elif current_texture_screen == "Units" or current_texture_screen == "Structures":
        current_y += 1
        current_x = 1

        #Draw Text
        
        text1 = font_string.render("Ownership", True, (230,230,230))
        textRect = text1.get_rect()
        textRect.center = (WIDTH - Texture_x_size - (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + Tools_icon_size / 2),
                        current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + int(Tools_icon_size / 1.3))
        PlacableSurface.blit(text1, textRect)

        #Draw button

        current_y += 1

        if len(ControllerButtons) < 4:
            ControllerButtons.append(
                button.Button( (WIDTH - Texture_x_size - Tool_x_size + 3 * Tools_icon_distance,
                            current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance,
                            Tools_icon_size, Tools_icon_size),
                            (204,0,0,50),
                            toggle_selection_controller,
                            **{"text": "1", "alternate_color": (204,0,0,200), "func_arg" : 1, "font": pygame.font.Font(None, 60),"font_color": (230,230,230), "border_color" : (204,0,0,50)}
                            )
                )
            ControllerButtons.append(
                button.Button( (WIDTH - Texture_x_size - Tools_icon_size - 3 * Tools_icon_distance,
                            current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance,
                            Tools_icon_size, Tools_icon_size),
                            (0,0,204,50),
                            toggle_selection_controller,
                            **{"text": "2", "alternate_color": (0,0,204,200), "func_arg" : 2, "font": pygame.font.Font(None, 60),"font_color": (230,230,230), "border_color" : (0,0,204,50)}
                            )
                )
            ControllerButtons.append(
                button.Button( (WIDTH - Texture_x_size - Tool_x_size + 3 * Tools_icon_distance,
                            current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + Tools_icon_size + Tools_icon_distance,
                            Tools_icon_size, Tools_icon_size),
                            (0,204,0,50),
                            toggle_selection_controller,
                            **{"text": "3", "alternate_color": (0,204,0,200), "func_arg" : 3, "font": pygame.font.Font(None, 60),"font_color": (230,230,230), "border_color" : (0,204,0,50)}
                            )
                )
            ControllerButtons.append(
                button.Button( (WIDTH - Texture_x_size - Tools_icon_size - 3 * Tools_icon_distance,
                            current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance + Tools_icon_size + Tools_icon_distance,
                            Tools_icon_size, Tools_icon_size),
                            (204,204,0,50),
                            toggle_selection_controller,
                            **{"text": "4", "alternate_color": (204,204,0,200), "func_arg" : 4, "font": pygame.font.Font(None, 60),"font_color": (230,230,230), "border_color" : (204,204,0,50)}
                            )
                )
