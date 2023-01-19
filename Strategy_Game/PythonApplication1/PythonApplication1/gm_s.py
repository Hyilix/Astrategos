import pygame
import pickle
import os

import TileClass
import Structures
import Units
import Ores

pygame.init()
screen = pygame.display.Info()

rows = 40
tiles_per_row = 40

tiles = []

def gameplay(WIN, WIDTH, HEIGHT, FPS, Map_name) :
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

    CurrentCamera = Camera((0,0), 1, 3, 0.4)

    normal_tile_length = int(TileClass.base_texture_length * (WIDTH / HEIGHT))     #the length of a tile when the zoom is 1
    current_tile_length = normal_tile_length * CurrentCamera.zoom

    TileClass.resize_textures(current_tile_length)
    Structures.resize_textures(current_tile_length)
    Units.resize_textures(current_tile_length)
    Ores.resize_textures(current_tile_length)

    #The base surface of the map. Zooming in/out will use this surface.
    mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))

    def load_map(map_name):
        try:
            with open("Maps/info/" + map_name + ".txt", "rb") as infile:
                print("STARTED")
                tiles.clear()
                global rows
                global tiles_per_row
                rows = pickle.load(infile)
                tiles_per_row = pickle.load(infile)
                nonlocal mapSurfaceNormal 
                mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))
                for x in range(rows):
                    new_vec = []
                    for y in range(tiles_per_row):        
                        loaded_object = pickle.load(infile)
                        new_unit, new_structure = None, None
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

                        new_tile = TileClass.Tile(loaded_object["Position"],
                                                    loaded_object["Collidable"],
                                                    None,     #Image Class
                                                    loaded_object["Image_name"],
                                                    None,     #Special
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

        except:
            print("No such file exists")

    load_map(Map_name)

    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

    clock = pygame.time.Clock()

    global Running
    Running = True

    while Running:
        clock.tick(FPS)
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

                    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

                elif event.unicode.lower() == 'l':  #Enable/Disable GUIs
                    #GUI.GUIs_enabled = not GUI.GUIs_enabled      
                    print("No GUIs implemented for gameplay yet") 

            if event.type == pygame.MOUSEBUTTONDOWN:
                modifier = 0
                if event.button == 4:
                    modifier = 1
                elif event.button == 5:
                    modifier = -1
               
                last_map_size_x = current_tile_length * tiles_per_row
                last_map_size_y = current_tile_length * rows

                #Update the zoom and tile length
                CurrentCamera.zoom += 0.1 * modifier
                CurrentCamera.Update_Camera_Zoom_Level()
                current_tile_length = int(normal_tile_length * CurrentCamera.zoom)

                map_size_x = current_tile_length * tiles_per_row
                map_size_y = current_tile_length * rows

                CurrentCamera.Check_Camera_Boundaries()
                CurrentCamera.Calculate_After_Zoom_Position(last_map_size_x, map_size_x, last_map_size_y, map_size_y)
                #TODO: Make a way to zoom in/out with minimal lag. This method is very bad but for now it works... kinda.
                #Apparently it works well with low texture sizes.
                try:
                    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))
                except:     #if that failed, the surface is too big.
                    print("Can't zoom in further")

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

        pygame.display.update()