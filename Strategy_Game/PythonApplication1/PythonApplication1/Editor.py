import TileClass
import Structures
import Units
import Ores
import Editor_GUI as GUI
import math
import os
import pickle
import numpy

import button
import pygame

pygame.init()
screen = pygame.display.Info()
FPS = 60

TileClass.full_bright = True

colorTable = {  #Table for assigning each controller with a color. In editor it's set, but in game it will get from lobby.
    0 : (64,64,64),
    1 : (204,0,0),
    2 : (0,0,204),
    3 : (0,204,0),
    4 : (204,204,0)
    }

mouse_pos = None

def editor(WIN,WIDTH,HEIGHT,FPS) :
    global mouse_pos
    rows = 100
    tiles_per_row = 100

    tiles = []
    #Editor specific variables:
    Brush_size = 1
    Brush_min = 1
    Brush_max = 35

    TileClass.colorTable = colorTable

    current_index = 0

    global Running
    Running = True

    GUI.Initialize_Editor_GUIs()
    GUI.Draw_Textures_GUI((0,0))

    class Camera:
        def __init__(self, position, zoom, max_zoom, min_zoom):
            self.x = position[0]
            self.y = position[1]
            self.zoom = zoom
            self.max_zoom = max_zoom
            self.min_zoom = min_zoom
        
            self.camera_movement = 15

            #make sure the zoom is insde [min_zoom, max_zoom]
            if min_zoom > zoom:
                self.zoom = self.min_zoom

            if zoom > max_zoom:
                self.zoom = self.max_zoom

        def Update_Camera_Zoom_Level(self):     #Make sure the camera zoom is within [min_zoom, max_zoom]
            if self.min_zoom > self.zoom:
                self.zoom = self.min_zoom

            if self.zoom > self.max_zoom:
                self.zoom = self.max_zoom

        def Check_Camera_Boundaries(self):     #Check if camera is within the boundaries of the map. If not, bring it there
            if self.x - self.camera_movement < - WIDTH // 2:
                self.x  = 0 - WIDTH // 2
            if self.y - self.camera_movement < - HEIGHT // 2:
                self.y = 0 - HEIGHT // 2
            if self.x + self.camera_movement + WIDTH // 2 > tiles_per_row * current_tile_length:
                self.x = tiles_per_row * current_tile_length - WIDTH // 2
            if self.y + self.camera_movement + HEIGHT // 2 > rows * current_tile_length:
                self.y = rows * current_tile_length - HEIGHT // 2

        def Calculate_After_Zoom_Position(self, last_map_size_x, map_size_x, last_map_size_y, map_size_y):  #Make the camera stay in the middle when zooming in/out
            self.x = int((self.x + WIDTH // 2) / last_map_size_x * map_size_x) - WIDTH // 2
            self.y = int((self.y + HEIGHT // 2) / last_map_size_y * map_size_y) - HEIGHT // 2

    CurrentCamera = Camera((0,0), 1, 1.4, 0.4)

    normal_tile_length = TileClass.base_texture_length    #the length of a tile when the zoom is 1
    current_tile_length = normal_tile_length * CurrentCamera.zoom

    TileClass.resize_textures(current_tile_length)
    Structures.resize_textures(current_tile_length)
    Units.resize_textures(current_tile_length)
    Ores.resize_textures(current_tile_length)

    #The base surface of the map. Zooming in/out will use this surface.
    mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))

    #Editor functions
    def load_map(map_name):
        try:
            with open("Maps/info/" + map_name + ".txt", "rb") as infile:
                print("STARTED")
                tiles.clear()
                nonlocal rows
                nonlocal tiles_per_row
                rows = pickle.load(infile)
                tiles_per_row = pickle.load(infile)
                nonlocal mapSurfaceNormal 
                mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))
                for x in range(rows):
                    new_vec = []
                    for y in range(tiles_per_row):        
                        loaded_object = pickle.load(infile)
                        new_unit, new_structure, new_ore = None, None, None
                        if loaded_object["Unit"]:  
                            new_unit = Units.Unit(loaded_object["Unit"]["Name"],
                                                    loaded_object["Unit"]["Position"],
                                                    loaded_object["Unit"]["Owner"]
                                                    )

                        if loaded_object["Structure"]:
                            new_structure = Structures.Structure(loaded_object["Structure"]["Name"],
                                                    loaded_object["Structure"]["Position"],
                                                    loaded_object["Structure"]["Owner"]
                                                    )

                        if loaded_object["Ore"]:
                            new_ore = Ores.Ore(loaded_object["Ore"]["Position"],
                                                    loaded_object["Ore"]["Name"],
                                                    loaded_object["Ore"]["Tier"]
                                                    )

                        new_tile = TileClass.Tile(loaded_object["Position"],
                                                    loaded_object["Collidable"],
                                                    loaded_object["Image_name"],
                                                    new_ore,
                                                    new_unit,
                                                    new_structure
                                                    )

                        new_vec.append(new_tile)
                    tiles.append(new_vec)

            for x in range(rows):  #Redraw the whole map
                for y in range(tiles_per_row):
                    tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                #tiles.append(newLine)

            nonlocal mapSurface
            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

            GUI_BUTTONS[-1].text = "Collumns: " + str(tiles_per_row)
            GUI_BUTTONS[-1].render_text()
            GUI_BUTTONS[-2].text = "Rows: " + str(rows)
            GUI_BUTTONS[-2].render_text()

        except:
            print("No such file exists")

    def save_map(map_name):
        try:
            print("Overwrite warning!")
            os.remove("Maps/images/" + map_name + ".jpg")
            os.remove("Maps/info/" + map_name + ".txt")
        except:
            print("No overwrite found.")
        print(map_name)
        pygame.image.save(mapSurfaceNormal, "Maps/images/" + map_name + ".jpg")
        used_textures = []
        with open("Maps/info/" + map_name + ".txt", "wb") as outfile:   #Saves the map into the file.
            pickle.dump(rows, outfile)
            pickle.dump(tiles_per_row, outfile)
            for x in range(rows):
                for y in range(tiles_per_row):
                    rawUnitData = {}
                    rawStructureData = {}
                    rawOreData = {}
                    if tiles[x][y].structure != None:
                        rawStructureData = {
                            "Position" : tiles[x][y].structure.position,
                            "Owner" : tiles[x][y].structure.owner,
                            "Name" : tiles[x][y].structure.name,
                            }

                    if tiles[x][y].unit != None:
                        rawUnitData = {
                            "Position" : tiles[x][y].unit.position,
                            "Owner" : tiles[x][y].unit.owner,
                            "Name" : tiles[x][y].unit.name,
                            }

                    if tiles[x][y].ore != None:
                        rawOreData = {
                            "Position" : tiles[x][y].ore.position,
                            "Name" : tiles[x][y].ore.image_name,
                            "Tier" : tiles[x][y].ore.tier,
                            }

                    rawTileData = {
                        "Position" : tiles[x][y].position,
                        "Collidable" : tiles[x][y].collidable,
                        "Image_name" : tiles[x][y].image_name,
                        "Unit" : rawUnitData,
                        "Structure" : rawStructureData,
                        "Ore" : rawOreData,
                        }

                    pickle.dump(rawTileData, outfile)
                    used_textures.append(tiles[x][y].image_name)
            pickle.dump(used_textures, outfile)
        outfile.close()

    #Button functions

    def save_screen():
        done = False
        map_text = ''
        max_str_length = 24
        font = pygame.font.Font('freesansbold.ttf', 32)

        nonlocal hasLeftClickPressed
        hasLeftClickPressed = False

        while not done:
            pygame.draw.rect(WIN, (148,148,148), pygame.Rect(WIDTH // 2 - WIDTH // 8, HEIGHT // 2 - HEIGHT // 8, WIDTH // 4, HEIGHT // 4))

            text1 = font.render(map_text, True, (32,32,32))
            textRect = text1.get_rect()
            textRect.center = (WIDTH // 2, HEIGHT // 2)
            WIN.blit(text1, textRect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    os._exit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        map_text = map_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        return
                    else:
                        if len(map_text) < max_str_length:
                            map_text += event.unicode

        save_map(map_text)

    def load_screen():
        done = False
        map_text = ''
        max_str_length = 24
        font = pygame.font.Font('freesansbold.ttf', 32)
        esc_font = pygame.font.Font('freesansbold.ttf', 64)

        nonlocal hasLeftClickPressed
        hasLeftClickPressed = False

        while not done:
            pygame.draw.rect(WIN, (148,148,148), pygame.Rect(WIDTH // 2 - WIDTH // 8, HEIGHT // 2 - HEIGHT // 8, WIDTH // 4, HEIGHT // 4))

            text1 = font.render(map_text, True, (32,32,32))
            textRect = text1.get_rect()
            textRect.center = (WIDTH // 2, HEIGHT // 2)
            WIN.blit(text1, textRect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        map_text = map_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        return
                    else:
                        if len(map_text) < max_str_length:
                            map_text += event.unicode

        load_map(map_text)

    def Menu():
        global Running
        Running = False

    def change_texture_screen(screen):
        GUI.current_tab = 1
        print(screen)
        GUI.current_texture_screen = screen
        nonlocal current_index
        current_index = 0
        GUI.Draw_Textures_GUI((0,0))
        GUI.Draw_Tools_GUI(GUI.last_tool_position, Brush_size)

    def change_dimension(dimension):
        nonlocal rows
        nonlocal tiles_per_row

        old_rows = rows
        old_tiles_per_row = tiles_per_row

        nonlocal hasLeftClickPressed
        hasLeftClickPressed = False

        done = False
        dim_text = ''
        max_str_length = 3
        font = pygame.font.Font('freesansbold.ttf', 32)
        while not done:
            pygame.draw.rect(WIN, (148,148,148), pygame.Rect(WIDTH // 2 - WIDTH // 8, HEIGHT // 2 - HEIGHT // 8, WIDTH // 4, HEIGHT // 4))

            text1 = font.render(dim_text, True, (32,32,32))
            textRect = text1.get_rect()
            textRect.center = (WIDTH // 2, HEIGHT // 2)
            WIN.blit(text1, textRect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    os._exit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        dim_text = dim_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        return
                    else:
                        if len(dim_text) < max_str_length and event.key <= 57 and event.key >= 48:
                            if not (len(dim_text) == 0 and event.key == 48):
                                dim_text += event.unicode

        if dimension == "rows":
            rows = int(dim_text)
        else:
            tiles_per_row = int(dim_text)

        nonlocal mapSurfaceNormal
        mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))

        nonlocal tiles

        #Shrink the map
        if rows < old_rows or tiles_per_row < old_tiles_per_row:
            temp_tile_map = []
            for x in range(rows):
                new_vec = []
                for y in range(tiles_per_row):
                    new_vec.append(tiles[x][y])
                temp_tile_map.append(new_vec)
            tiles = temp_tile_map
            del temp_tile_map

        #Grow the map. Save the old map in a temp array and then assemble the pieces.
        if rows > old_rows or tiles_per_row > old_tiles_per_row:
            temp_tile_map = []

            for x in range(old_rows):
                newLine = []
                for y in range(old_tiles_per_row):
                    newLine.append(tiles[x][y])
                temp_tile_map.append(newLine)

            tiles.clear()
            for x in range(rows):  #Create the map with empty tiles
                newLine = []
                for y in range(tiles_per_row):
                    newTile = TileClass.Tile((y, x), False, None, TileClass.empty_image_name, None, None, None)
                    newLine.append(newTile)
                    newTile.DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                tiles.append(newLine)
                del newTile

            for x in range(old_rows):
                for y in range(old_tiles_per_row):
                    tiles[x][y] = temp_tile_map[x][y]

            del temp_tile_map

        for x in range(rows):  #Redraw the whole map
            for y in range(tiles_per_row):
                tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))

        nonlocal mapSurface
        mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

        GUI_BUTTONS[-1].text = "Collumns: " + str(tiles_per_row)
        GUI_BUTTONS[-1].render_text()
        GUI_BUTTONS[-2].text = "Rows: " + str(rows)
        GUI_BUTTONS[-2].render_text()

    #Buttons
    ButtonSurface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    GUI_BUTTONS = []

    ButtonSurface.convert_alpha()
    
    texture_size = GUI.texture_size

    GUI_BUTTONS.append( #Menu button
        button.Button(  (WIDTH * 9.5 // 10 - (texture_size * 1.5 // 2),
                        HEIGHT * 9 // 10, texture_size * 1.5, texture_size * 0.85),
                        (64,64,64,180),
                        Menu,
                        **{"text": "Menu","font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,180), "hover_color" : (192,192,192,180)}
                        )
    )

    GUI_BUTTONS.append( #Load button
        button.Button(  (WIDTH * 9.5 // 10 - (texture_size * 1.5 // 2) - texture_size * 1.5 - texture_size // 3,
                        HEIGHT * 9 // 10, texture_size * 1.5, texture_size * 0.85),
                        (64,64,64,180),
                        load_screen,
                        **{"text": "Load","font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,180), "hover_color" : (192,192,192,180)}
                        )
    )

    GUI_BUTTONS.append( #Save button
        button.Button(  (WIDTH * 9.5 // 10 - (texture_size * 1.5 // 2) + 2 * (- texture_size * 1.5 - texture_size // 3),
                        HEIGHT * 9 // 10, texture_size * 1.5, texture_size * 0.85),
                        (64,64,64,180),
                        save_screen,
                        **{"text": "Save","font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,180), "hover_color" : (192,192,192,180)}
                        )
    )

    GUI_BUTTONS.append( #Tiles button
        button.Button(  (WIDTH - GUI.Tool_x_size - GUI.Texture_x_size,
                        HEIGHT // 2, GUI.Tool_x_size, texture_size),
                        (64,64,64,180),
                        change_texture_screen,
                        **{"text": "Tiles","func_arg" : "Tiles","font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,180), "hover_color" : (192,192,192,180)}
                        )
    )

    GUI_BUTTONS.append( #Structures button
        button.Button(  (WIDTH - GUI.Tool_x_size - GUI.Texture_x_size,
                        HEIGHT // 2 + 1 * (texture_size), GUI.Tool_x_size, texture_size),
                        (64,64,64,180),
                        change_texture_screen,
                        **{"text": "Structures","func_arg" : "Structures","font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,180), "hover_color" : (192,192,192,180)}
                        )
    )

    GUI_BUTTONS.append( #Units button
        button.Button(  (WIDTH - GUI.Tool_x_size - GUI.Texture_x_size,
                        HEIGHT // 2 + 2 * (texture_size), GUI.Tool_x_size, texture_size),
                        (64,64,64,180),
                        change_texture_screen,
                        **{"text": "Units","func_arg" : "Units","font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,180), "hover_color" : (192,192,192,180)}
                        )
    )

    GUI_BUTTONS.append( #Ores button
        button.Button(  (WIDTH - GUI.Tool_x_size - GUI.Texture_x_size,
                        HEIGHT // 2 + 3 * (texture_size), GUI.Tool_x_size, texture_size),
                        (64,64,64,180),
                        change_texture_screen,
                        **{"text": "Ores","func_arg" : "Ores","font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,180), "hover_color" : (192,192,192,180)}
                        )
    )

    GUI_BUTTONS.append( #Rows button
        button.Button(  (WIDTH - GUI.Tool_x_size - GUI.Texture_x_size,
                        HEIGHT // 2 + 4.3 * (texture_size), GUI.Tool_x_size, texture_size),
                        (64,64,64,0),
                        change_dimension,
                        **{"text": "Rows: " + str(rows), "func_arg":"rows", "font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,0), "hover_color" : (192,192,192,80)}
                        )
    )

    GUI_BUTTONS.append( #Rows button
        button.Button(  (WIDTH - GUI.Tool_x_size - GUI.Texture_x_size,
                        HEIGHT // 2 + 5.3 * (texture_size), GUI.Tool_x_size, texture_size),
                        (64,64,64,0),
                        change_dimension,
                        **{"text": "Collumns: " + str(tiles_per_row), "func_arg":"collumn", "font": pygame.font.Font(None, 40),"font_color": (196,196,196), "border_color" : (64,64,64,0), "hover_color" : (192,192,192,80)}
                        )
    )

    for x in range(rows):  #Create the map with empty tiles
        newLine = []
        for y in range(tiles_per_row):
            newTile = TileClass.Tile((y, x), False, TileClass.empty_image_name, None, None, None)
            newLine.append(newTile)
            newTile.DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
        tiles.append(newLine)
        del newTile

    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

    ToolsSelectedPositions = []

    GUI.Draw_Tools_GUI(None, Brush_size)

    Collision = False
    Eraser = False
    Fill = False
    FillAll = False
    FillSame = False

    Editor_var_dict = {
        "ZCollision" : Collision,
        "Eraser" : Eraser,
        "Fill" : Fill,
        "FillAll" : FillAll,
        "FillSame" : FillSame
    }

    def image_modifier(x,y, special_blit = False):
        if GUI.current_texture_screen == "Tiles":
            tiles[y][x].image_name = TileClass.avalible_textures[current_index]
        elif GUI.current_texture_screen == "Structures":
            struct = Structures.Structure(Structures.texture_names[current_index][:-4], (x,y), GUI.controller_selection)
            tiles[y][x].structure = struct
        elif GUI.current_texture_screen == "Units":
            unit = Units.Unit(Units.texture_names[current_index][:-4], (x,y), GUI.controller_selection)
            tiles[y][x].unit = unit
        elif GUI.current_texture_screen == "Ores":
            result = 1
            if GUI.ore_tier_selection == False:
                result = 2
            ore = Ores.Ore((x,y), Ores.texture_names[current_index][:-4], result)
            tiles[y][x].ore = ore

        if Editor_var_dict["Eraser"] == True:
            tiles[y][x].structure = None
            tiles[y][x].special = None
            tiles[y][x].unit = None
            tiles[y][x].ore = None
        tiles[y][x].collidable = Editor_var_dict["ZCollision"]
        tiles[y][x].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
        if special_blit == True:
            tiles[y][x].DrawImage(mapSurface, (current_tile_length, current_tile_length), True)

    def place_tile(target_img = None, special_blit = False):     #Function to determine what to place and how
        if Editor_var_dict["Fill"] == True:
            mouse_pos = pygame.mouse.get_pos()

            x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
            y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

            visited_vec = []
            queued_tiles = [(x_layer, y_layer)]

            directions = [
                (-1,0),
                (1,0),
                (0,1),
                (0,-1)
            ]

            checks = 0
            tries = 0

            isDone = False

            while not isDone:

                new_tiles = []

                for myTile in queued_tiles:

                    tries += 1

                    x = myTile[0]
                    y = myTile[1]

                    if (x, y) not in visited_vec:
                        if x >= 0 and y >= 0 and x < rows and y < tiles_per_row and tiles[x][y].image_name[:-4] == target_img:
                            checks += 1
                            visited_vec.append((x, y))
                            image_modifier(x, y, special_blit)

                            for direction in directions:
                                in_x = direction[0]
                                in_y = direction[1]
                                if (x + in_x, y + in_y) not in visited_vec:
                                    new_tiles.append((x + in_x, y + in_y))

                queued_tiles.clear()

                if len(new_tiles) == 0: isDone = True

                queued_tiles += new_tiles

            visited_vec.clear()
            queued_tiles.clear()

        elif Editor_var_dict["FillAll"] == True:
            for y in range(rows):
                for x in range(tiles_per_row):
                    image_modifier(x,y, special_blit)

        elif Editor_var_dict["FillSame"] == True:
            for y in range(rows):
                for x in range(tiles_per_row):
                    if tiles[y][x].image_name[:-4] == target_img:
                        image_modifier(x,y, special_blit)

        else:
            mouse_pos = pygame.mouse.get_pos()

            x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
            y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

            x = x_layer
            y = y_layer

            if Brush_size == 1:
                if x_layer >= 0 and x_layer < tiles_per_row:
                    if y_layer >= 0 and y_layer < rows:
                        image_modifier(x,y, special_blit)

            else:
                for Y in range(y - math.ceil(Brush_size / 2), y + math.ceil(Brush_size / 2) + 1):
                    for X in range(x - math.ceil(Brush_size / 2), x + math.ceil(Brush_size / 2) + 1):
                        if X >= 0 and X < tiles_per_row:
                            if Y >= 0 and Y < rows:
                                image_modifier(X,Y, special_blit)

    clock = pygame.time.Clock()

    hasLeftClickPressed = False    #Determine if left mouse is pressed down.

    WIN.fill((0,0,0))

    while Running:
        clock.tick(FPS)
        #print(clock.get_fps())
        for event in pygame.event.get():
                
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE : #Intoarcerea in meniu
                    Running = False
                elif event.unicode.lower() == 'p':    #Enable/Disable simple textures
                    TileClass.simple_textures_enabled = not TileClass.simple_textures_enabled

                    for x in range(rows):  #Redraw the whole map
                        for y in range(tiles_per_row):
                            tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                        #tiles.append(newLine)

                    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

                elif event.unicode.lower() == 'l':  #Enable/Disable GUIs
                    GUI.GUIs_enabled = not GUI.GUIs_enabled                

            if event.type == pygame.MOUSEBUTTONDOWN:    #Check if mouse was scrolled or pressed
                if event.button == 1:   #Left-click. Editor specific
                    mouse_pos = pygame.mouse.get_pos()
                    hasLeftClickPressed = True
                    if GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size:  
                        #Check if the mouse is inside the TextureGUI
                        #and check which texture is selected.

                        x_layer = (mouse_pos[0] - (WIDTH - GUI.Texture_x_size)) // (GUI.texture_size + GUI.texture_distance)
                        y_layer = mouse_pos[1] // (GUI.texture_size + GUI.texture_distance)
                    
                        index_to_use = None
                        if GUI.current_texture_screen == "Tiles":
                            index_to_use = TileClass.last_index
                        elif GUI.current_texture_screen == "Structures":
                            index_to_use = Structures.last_index
                        elif GUI.current_texture_screen == "Units":
                            index_to_use = Units.last_index
                        elif GUI.current_texture_screen == "Ores":
                            index_to_use = Ores.last_index

                        if (mouse_pos[0] - (WIDTH - GUI.Texture_x_size)) % (GUI.texture_size + GUI.texture_distance) < GUI.texture_distance:
                            break
                        elif mouse_pos[1] % (GUI.texture_size + GUI.texture_distance) < GUI.texture_distance:
                            break
                        else:
                            index = (GUI.max_x_pos * y_layer + x_layer) + (GUI.current_tab - 1) * GUI.texture_cap
                            if GUI.max_x_pos * y_layer > 0: index += y_layer
                            if index < index_to_use and index <= GUI.texture_cap * GUI.current_tab:
                                current_index = index
                                GUI.Draw_Textures_GUI((x_layer, y_layer))
                                print(GUI.texture_cap)

                    elif GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size - GUI.Tool_x_size:
                        #Check if the mouse is inside the ToolsGUI
                        #and check which texture is selected.
                        x_layer = (mouse_pos[0] - (WIDTH - GUI.Texture_x_size - GUI.Tool_x_size)) // (GUI.texture_size + GUI.texture_distance)
                        y_layer = mouse_pos[1] // (GUI.texture_size + GUI.texture_distance)

                        if (mouse_pos[0] - (WIDTH - GUI.Texture_x_size - GUI.Tool_x_size)) % (GUI.Tools_icon_size + GUI.Tools_icon_distance) < GUI.Tools_icon_distance:
                            break
                        elif mouse_pos[1] % (GUI.Tools_icon_size + GUI.Tools_icon_distance) < GUI.Tools_icon_distance:
                            break
                        else:
                            index = GUI.max_x_pos * y_layer + x_layer
                            if GUI.max_x_pos * y_layer > 0: index += y_layer
                            if index < GUI.last_icons_index:
                                name = GUI.icon_names[index][:-4]

                                if ToolsSelectedPositions.count((x_layer, y_layer)) > 0:
                                    ToolsSelectedPositions.remove((x_layer, y_layer))
                                    Editor_var_dict[name] = False
                                else:
                                    ToolsSelectedPositions.append((x_layer, y_layer))
                                    Editor_var_dict[name] = True

                                def find_img(image):    #Find and image to deselect
                                    new_x = 0
                                    new_y = 0
                                    newIndex = GUI.Tools_max_x_pos * new_y + new_x
                                    while newIndex < GUI.last_icons_index:
                                        if GUI.icon_names[newIndex][:-4] == image and ToolsSelectedPositions.count((new_x, new_y)) > 0:
                                            ToolsSelectedPositions.remove((new_x, new_y))
                                            break
                                        if new_x >= GUI.Tools_max_x_pos:
                                            new_x = 0
                                            new_y += 1
                                        else:
                                            new_x += 1
                                        newIndex = GUI.max_x_pos * new_y + new_x
                                        if GUI.Tools_max_x_pos * new_y > 0: newIndex += new_y

                                if name == "Fill":
                                    Editor_var_dict["FillAll"] = False
                                    Editor_var_dict["FillSame"] = False
                                    find_img("FillAll")
                                    find_img("FillSame")
                                elif name == "FillAll":
                                    Editor_var_dict["Fill"] = False
                                    Editor_var_dict["FillSame"] = False
                                    find_img("Fill")
                                    find_img("FillSame")
                                elif name == "FillSame":
                                    Editor_var_dict["Fill"] = False
                                    Editor_var_dict["FillAll"] = False
                                    find_img("Fill")
                                    find_img("FillAll")

                            else:
                                #Check if plus/minus sign for the brush is pressed.
                                minus_index = GUI.max_x_pos * GUI.minus_brush[1] + GUI.minus_brush[0]
                                if GUI.max_x_pos * GUI.minus_brush[1] > 0: minus_index += GUI.minus_brush[1]
                                plus_index = GUI.max_x_pos * GUI.plus_brush[1] + GUI.plus_brush[0]
                                if GUI.max_x_pos * GUI.plus_brush[1] > 0: plus_index += GUI.plus_brush[1]

                                if index == minus_index:
                                    if Brush_size - 1 < Brush_min:
                                        Brush_size = Brush_min
                                    else: Brush_size -= 1;

                                elif index == plus_index:
                                    if Brush_size + 1 > Brush_max:
                                        Brush_size = Brush_max
                                    else: Brush_size += 1;
                                
                            GUI.Draw_Tools_GUI(ToolsSelectedPositions, Brush_size)

                    else:  #Mouse is on the map, so check which tile is selected
                        x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
                        y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

                        if x_layer >= 0 and x_layer < tiles_per_row:
                            if y_layer >= 0 and y_layer < rows:
                                place_tile(tiles[y_layer][x_layer].image_name[:-4], True)

                if event.button == 4 or event.button == 5 and mouse_pos:

                    if GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size - GUI.Tool_x_size:
                        dmodifier = 0
                        if event.button == 4:
                            dmodifier = -1
                        elif event.button == 5:
                            dmodifier = 1

                        if GUI.current_tab + dmodifier >= 1 and GUI.current_tab + dmodifier <= GUI.tabs:
                            GUI.current_tab = GUI.current_tab + dmodifier
                            index = (GUI.current_tab - 1) * GUI.texture_cap
                            current_index = index
                            GUI.Draw_Textures_GUI((0,0))

                    if not (GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size - GUI.Tool_x_size):

                        modifier = 0
                        if event.button == 4:
                            modifier = 1
                        elif event.button == 5:
                            modifier = -1

                        #modifier = -1 * event.button + event.button

                        last_map_size_x = current_tile_length * tiles_per_row
                        last_map_size_y = current_tile_length * rows

                        #Update the zoom and tile length
                        CurrentCamera.zoom += 0.1 * modifier
                        CurrentCamera.Update_Camera_Zoom_Level()
                        current_tile_length = int(normal_tile_length * CurrentCamera.zoom)

                        map_size_x = current_tile_length * tiles_per_row
                        map_size_y = current_tile_length * rows

                        CurrentCamera.Check_Camera_Boundaries()
                        #TODO: Make a way to zoom in/out with minimal lag. This method is very bad but for now it works... kinda.
                        #Apparently it works well with low texture sizes.
                        try:
                            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))
                            CurrentCamera.Calculate_After_Zoom_Position(last_map_size_x, map_size_x, last_map_size_y, map_size_y)
                        except:     #if that failed, the surface is too big.
                            print("Can't zoom in further")

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:   #Left-click. Editor specific
                    hasLeftClickPressed = False

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if GUI.GUIs_enabled == False or (not (GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size) and not (mouse_pos[0] >= WIDTH - GUI.Texture_x_size - GUI.Tool_x_size)): 
                    if hasLeftClickPressed == True:
                        x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
                        y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

                        if x_layer >= 0 and x_layer < tiles_per_row:
                            if y_layer >= 0 and y_layer < rows:
                                place_tile(tiles[y_layer][x_layer].image_name[:-4], True)

            if GUI.GUIs_enabled == True: 
                for i in GUI_BUTTONS:
                    i.check_event(event)
                if GUI.current_texture_screen == "Ores":
                    for i in GUI.OreButtons:
                        i.check_event(event)
                if GUI.current_texture_screen == "Units" or GUI.current_texture_screen == "Structures":
                    for i in GUI.ControllerButtons:
                        i.check_event(event)

        #Check if user wants to change the camera's position
        x_pos = pygame.mouse.get_pos()[0]
        y_pos = pygame.mouse.get_pos()[1]

        if x_pos == 0:
            CurrentCamera.x -= CurrentCamera.camera_movement
        if y_pos == 0:
            CurrentCamera.y -= CurrentCamera.camera_movement
        if x_pos == WIDTH - 1:
            CurrentCamera.x += CurrentCamera.camera_movement
        if y_pos == HEIGHT - 1:
            CurrentCamera.y += CurrentCamera.camera_movement

        CurrentCamera.Check_Camera_Boundaries()

        #Render everything

        tempSurface = pygame.Surface((WIDTH, HEIGHT))
        tempSurface.blit(mapSurface, (0, 0), (CurrentCamera.x, CurrentCamera.y, WIDTH, HEIGHT))

        WIN.blit(tempSurface, (0, 0)) 

        if GUI.GUIs_enabled == True: 

            for i in GUI_BUTTONS:
                i.update(ButtonSurface)
            if GUI.current_texture_screen == "Units" or GUI.current_texture_screen == "Structures":
                for i in GUI.ControllerButtons:
                    i.update(GUI.PlacableSurface)
            if GUI.current_texture_screen == "Ores":
                for i in GUI.OreButtons:
                    i.update(GUI.PlacableSurface)

            WIN.blit(GUI.TextureSurface, (WIDTH - GUI.Texture_x_size, 0))
            WIN.blit(GUI.ToolsSurface, (WIDTH - GUI.Texture_x_size - GUI.Tool_x_size, 0))
            WIN.blit(ButtonSurface, (0,0))

            if GUI.current_texture_screen == "Ores" or GUI.current_texture_screen == "Units" or GUI.current_texture_screen == "Structures":
                WIN.blit(GUI.PlacableSurface, (0,0))

        pygame.display.update()

    #END