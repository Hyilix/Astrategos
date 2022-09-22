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

    def Check_Camera_Boundaries(self, WIDTH, HEIGHT, current_tile_length, tiles_per_row, rows):     #Check if camera is within the boundaries of the map. If not, bring it there
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

    def render_tiles_in_camera(self, tiles, current_tile_length, WIDTH, HEIGHT, tiles_per_row, rows):   #Render all the tiles that the camera can "see".
        i = self.x // current_tile_length
        first_i = i
        while i <= (self.x + WIDTH) // current_tile_length and i < tiles_per_row:
            j = self.y // current_tile_length
            first_j = j
            while j <= (self.y + HEIGHT) // current_tile_length and j < rows:
                tiles[i][j].DrawImage(WIN, (current_tile_length, current_tile_length), self.x % current_tile_length, self.y % current_tile_length, first_i, first_j)
                j += 1
            i += 1
