import TileClass
import Structures
import Units

import pygame

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

current_zoom = 1
camera_movement = 15

class Camera:
    def __init__(self, position, zoom, max_zoom, min_zoom):
        self.x = position[0]
        self.y = position[1]
        self.zoom = zoom
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom

        self.center_x = (self.x + WIDTH // 2) * current_tile_length
        self.center_y = (self.y + HEIGHT // 2) * current_tile_length

        #make sure the zoom is insde [min_zoom, max_zoom]
        if min_zoom > zoom:
            self.zoom = self.min_zoom

        if zoom > max_zoom:
            self.zoom = self.max_zoom

    def Update_camera(self):
        self.zoom = current_zoom

        if self.min_zoom > self.zoom:
            self.zoom = self.min_zoom
            return True     #This indicates that something happened

        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom
            return True

        return False        #This indicates that nothing happened, just like in 1989....

    def Update_center(self):
        self.center_x = (self.x + WIDTH // 2) * current_tile_length
        self.center_y = (self.y + HEIGHT // 2) * current_tile_length

CurrentCamera = Camera((0,0), current_zoom, 1.3, 0.6)

normal_tile_length = 68 * WIDTH // HEIGHT     #the length of a tile when the zoom is 1
current_tile_length = normal_tile_length * current_zoom

TileClass.resize_textures(current_tile_length)
Structures.resize_textures(current_tile_length)
Units.resize_textures(current_tile_length)

rows = 80
tiles_per_row = 80

tiles = []

for x in range(rows):       #Create the map with empty tiles
    newLine = []
    for y in range(tiles_per_row):
        newLine.append(TileClass.Tile((x, y), False, TileClass.empty_image_name, None, None, None))
    tiles.append(newLine)

#For testing purposes, 2 tiles have been modified.
tiles[2][2].structure = Structures.Core((2, 2), None)
tiles[3][3].unit = Units.Marine((3, 3), None)

FPS = 60

clock = pygame.time.Clock()

Running = True

WIN.fill((0,0,0))

def Check_Camera():     #Check if camera is within the boundaries of the map. If not, bring it there
    if CurrentCamera.x - camera_movement < - WIDTH // 2:
        CurrentCamera.x  = 0 - WIDTH // 2
    if CurrentCamera.y - camera_movement < - HEIGHT // 2:
        CurrentCamera.y = 0 - HEIGHT // 2
    if CurrentCamera.x + camera_movement + WIDTH // 2 > tiles_per_row * current_tile_length:
        CurrentCamera.x = tiles_per_row * current_tile_length - WIDTH // 2
    if CurrentCamera.y + camera_movement + HEIGHT // 2 > rows * current_tile_length:
        CurrentCamera.y = rows * current_tile_length - HEIGHT // 2

def render_tiles_in_camera():   #Render all the tiles that the camera can "see".
    i = CurrentCamera.x // current_tile_length
    first_i = i
    while i <= (CurrentCamera.x + WIDTH) // current_tile_length and i < tiles_per_row:
        j = CurrentCamera.y // current_tile_length
        first_j = j
        while j <= (CurrentCamera.y + HEIGHT) // current_tile_length and j < rows:
            tiles[i][j].DrawImage(WIN, (current_tile_length, current_tile_length), CurrentCamera.x % current_tile_length, CurrentCamera.y % current_tile_length, first_i, first_j)
            j += 1
        i += 1

while Running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.MOUSEBUTTONDOWN:    #Check if mouse was scrolled
            modifier = 0
            if event.button == 4:
                modifier = 1
            if event.button == 5:
                modifier = -1
               
            #Update the zoom and tile length
            current_zoom += 0.1 * modifier
            camera_moved = CurrentCamera.Update_camera()
            current_zoom = CurrentCamera.zoom
            current_tile_length = int(normal_tile_length * CurrentCamera.zoom)

            if camera_moved == False:   #If camera can be moved (Check Update_camera() function), update it's position to stay centered.
                CurrentCamera.x = CurrentCamera.x + current_tile_length * modifier
                CurrentCamera.y = CurrentCamera.y + current_tile_length * modifier

            TileClass.resize_textures(current_tile_length)
            Structures.resize_textures(current_tile_length)
            Units.resize_textures(current_tile_length)
            Check_Camera()

    #Check if user wants to change the camera's position
    x_pos = pygame.mouse.get_pos()[0]
    y_pos = pygame.mouse.get_pos()[1]

    if x_pos == 0:
        CurrentCamera.x -= camera_movement
    if y_pos == 0:
        CurrentCamera.y -= camera_movement
    if x_pos == WIDTH - 1:
        CurrentCamera.x += camera_movement
    if y_pos == HEIGHT - 1:
        CurrentCamera.y += camera_movement

    Check_Camera()

    #Render everything
    WIN.fill((0,0,0))
    render_tiles_in_camera()
      
    pygame.display.update()

#END
pygame.quit()