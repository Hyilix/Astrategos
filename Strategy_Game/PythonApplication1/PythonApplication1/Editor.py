import TileClass
import Structures
import Units
import Connection_Screen

import pygame

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

#PUT this here to test my shit
#Mark as Comment if needed
Connection_Screen.connection_screen(WIN,WIDTH,HEIGHT,FPS,0)

current_zoom = 1
camera_movement = 15

class Camera:
    def __init__(self, position, zoom, max_zoom, min_zoom):
        self.x = position[0]
        self.y = position[1]
        self.zoom = zoom
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom

        #make sure the zoom is insde [min_zoom, max_zoom]
        if min_zoom > zoom:
            self.zoom = self.min_zoom

        if zoom > max_zoom:
            self.zoom = self.max_zoom

    def Update_camera(self):
        self.zoom = current_zoom

        if self.min_zoom > self.zoom:
            self.zoom = self.min_zoom

        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

CurrentCamera = Camera((0,0), current_zoom, 1.3, 0.6)

normal_tile_length = 68 * WIDTH // HEIGHT     #the length of a tile when the zoom is 1
current_tile_length = normal_tile_length * current_zoom

TileClass.resize_textures(current_tile_length)
Structures.resize_textures(current_tile_length)
Units.resize_textures(current_tile_length)

rows = 80
tiles_per_row = 80

tiles = []

for x in range(rows):
    newLine = []
    for y in range(tiles_per_row):
        newLine.append(TileClass.Tile((x, y), False, TileClass.empty_image_name, None, None, None))
    tiles.append(newLine)

tiles[2][2].structure = Structures.Core((2, 2), None)
tiles[3][3].unit = Units.Marine((3, 3), None)


clock = pygame.time.Clock()

Running = True

WIN.fill((0,0,0))

def Check_Camera():
    if CurrentCamera.x - camera_movement < 0:
        CurrentCamera.x = 0
    if CurrentCamera.y - camera_movement < 0:
        CurrentCamera.y = 0
    if (CurrentCamera.x + WIDTH) > tiles_per_row * current_tile_length:
        CurrentCamera.x = tiles_per_row * current_tile_length - WIDTH
    if CurrentCamera.y + camera_movement + HEIGHT > rows * current_tile_length:
        CurrentCamera.y = rows * current_tile_length - HEIGHT

def render_tiles_in_camera():
    counter = 0
    i = CurrentCamera.x // current_tile_length
    first_i = i
    while i <= (CurrentCamera.x + WIDTH) // current_tile_length and i < tiles_per_row:
        j = CurrentCamera.y // current_tile_length
        first_j = j
        while j <= (CurrentCamera.y + HEIGHT) // current_tile_length and j < rows:
            tiles[i][j].DrawImage(WIN, (current_tile_length, current_tile_length), CurrentCamera.x % current_tile_length, CurrentCamera.y % current_tile_length, first_i, first_j)
            j += 1
            counter += 1
        i += 1
    #print(counter)

while Running:
    clock.tick(FPS)
    #print(clock.get_fps())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            modifier = 0
            if event.button == 4:
                modifier = 1
            if event.button == 5:
                modifier = -1

            current_zoom += 0.1 * modifier
            CurrentCamera.Update_camera()
            current_zoom = CurrentCamera.zoom
            current_tile_length = int(normal_tile_length * CurrentCamera.zoom)

            TileClass.resize_textures(current_tile_length)
            Structures.resize_textures(current_tile_length)
            Units.resize_textures(current_tile_length)
            Check_Camera()

    #Check if user wants to change the camera's position
    x_pos = pygame.mouse.get_pos()[0]
    y_pos = pygame.mouse.get_pos()[1]

    if x_pos == 0:
        if CurrentCamera.x - camera_movement < 0:
            CurrentCamera.x = 0
        else:
            CurrentCamera.x -= camera_movement
    if y_pos == 0:
        if CurrentCamera.y - camera_movement < 0:
            CurrentCamera.y = 0
        else:
            CurrentCamera.y -= camera_movement
    if x_pos == WIDTH - 1:
        if (CurrentCamera.x + camera_movement + WIDTH) > tiles_per_row * current_tile_length:
            CurrentCamera.x = tiles_per_row * current_tile_length - WIDTH
        else:
            CurrentCamera.x += camera_movement
    if y_pos == HEIGHT - 1:
        if CurrentCamera.y + camera_movement + HEIGHT > rows * current_tile_length:
            CurrentCamera.y = rows * current_tile_length - HEIGHT
        else:
            CurrentCamera.y += camera_movement

    #Render everything
    WIN.fill((0,0,0))
    render_tiles_in_camera()
      
    pygame.display.update()
pygame.quit()