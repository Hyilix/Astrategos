import TileClass
import Structures
import Units
import GUI

import pygame

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

GUI.Initialize_Editor_GUIs()
GUI.Draw_Textures_GUI((0,0))
GUI.Draw_Tools_GUI([(0,0),(1,0)])

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

CurrentCamera = Camera((0,0), 1, 3, 0.6)

normal_tile_length = int(TileClass.base_texture_length * (WIDTH / HEIGHT))     #the length of a tile when the zoom is 1
current_tile_length = normal_tile_length * CurrentCamera.zoom

TileClass.resize_textures(current_tile_length)
Structures.resize_textures(current_tile_length)
Units.resize_textures(current_tile_length)

rows = 100
tiles_per_row = 100

tiles = []

#The base surface of the map. Zooming in/out will use this surface.
mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))

for x in range(rows):  #Create the map with empty tiles
    newLine = []
    for y in range(tiles_per_row):
        newTile = TileClass.Tile((y, x), False, TileClass.empty_image_name, None, None, None)
        newLine.append(newTile)
        newTile.DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
    tiles.append(newLine)

#For testing purposes, 2 tiles have been modified. Each modification has to be updated.
tiles[1][2].structure = Structures.Core((2, 1), None)
tiles[1][2].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))

tiles[3][3].unit = Units.Marine((3, 3), None)
tiles[3][3].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))

mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

current_index = 0
max_index = TileClass.last_index

FPS = 60

clock = pygame.time.Clock()

Running = True

hasLeftClickPressed = False    #Determine if left mouse is pressed down.

WIN.fill((0,0,0))

while Running:
    clock.tick(FPS)
    #print(clock.get_fps())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.KEYDOWN:
            if event.unicode.lower() == 'p':    #Enable/Disable simple textures
                TileClass.simple_textures_enabled = not TileClass.simple_textures_enabled

                for x in range(rows):  #Redraw the whole map
                    for y in range(tiles_per_row):
                        tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                    tiles.append(newLine)

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
                    
                    if (mouse_pos[0] - (WIDTH - GUI.Texture_x_size)) % (GUI.texture_size + GUI.texture_distance) < GUI.texture_distance:
                        break
                    elif mouse_pos[1] % (GUI.texture_size + GUI.texture_distance) < GUI.texture_distance:
                        break
                    else:
                        index = GUI.max_x_pos * y_layer + x_layer
                        if GUI.max_x_pos * y_layer > 0: index += 1
                        print(index)
                        if index < TileClass.last_index:
                            current_index = index
                            GUI.Draw_Textures_GUI((x_layer, y_layer))

                elif GUI.GUIs_enabled == True and mouse_pos[0] <= WIDTH // 5:
                    x_layer = mouse_pos[0] // (GUI.texture_size + GUI.texture_distance)
                    y_layer = mouse_pos[1] // (GUI.texture_size + GUI.texture_distance)

                    if mouse_pos[0] % (GUI.Tools_icon_size + GUI.Tools_icon_distance) < GUI.Tools_icon_distance:
                        break
                    elif mouse_pos[1] % (GUI.Tools_icon_size + GUI.Tools_icon_distance) < GUI.Tools_icon_distance:
                        break
                    else:
                        print("x")

                else:  #Mouse is on the map, so check which tile is selected
                    x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
                    y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

                    print(x_layer, y_layer)

                    if x_layer >= 0 and x_layer < tiles_per_row:
                        if y_layer >= 0 and y_layer < rows:
                            tiles[y_layer][x_layer].image_name = TileClass.avalible_textures[current_index]
                            tiles[y_layer][x_layer].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

            modifier = 0
            if event.button == 4:
                modifier = 1
            elif event.button == 5:
                modifier = -1
            else: continue
               
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
                print("hello")

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:   #Left-click. Editor specific
                hasLeftClickPressed = False
                print("NO")

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if not (GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size): 
                if hasLeftClickPressed == True:
                    x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
                    y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

                    print(x_layer, y_layer)

                    if x_layer >= 0 and x_layer < tiles_per_row:
                        if y_layer >= 0 and y_layer < rows:
                            tiles[y_layer][x_layer].image_name = TileClass.avalible_textures[current_index]
                            tiles[y_layer][x_layer].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))


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
        WIN.blit(GUI.TextureSurface, (WIDTH - GUI.Texture_x_size, 0))
        WIN.blit(GUI.ToolsSurface, (0, 0))
    pygame.display.update()

#END
pygame.quit()