from datetime import datetime, timedelta
import math
from random import randint, random
import pygame
from mapgen import MapMaker
from models import TileType, Worker, MouseMode, Tile, ResourceType
pygame.init()

class Game:
    def __init__(self):
        self.tile_size = 16
        self.screen_size = (1024, 768)
        self.screen = pygame.display.set_mode([self.screen_size[0],self.screen_size[1]])
        self.running = True
        self.last_tick = datetime.now()
        self.gametime = 0
        self.fps = 0
        maker = MapMaker()
        self.map = maker.gen_map()
        self.map_size = self.map.image.size
        self.view_pos = (0,0)
        self.view_max = (math.floor(self.screen_size[0]/self.tile_size),math.floor(self.screen_size[1]/self.tile_size))
        self.last_mouse_pos = (0,0)
        self.last_mouse_press = False
        self.unit_to_place = None
        self.structure_to_place = None
        self.unit_to_move = None
        self.mouse_mode = MouseMode.STANDBY
        self.mouse_dragging = False
        self.show_map = True
        self.show_resources = True
        self.fonts = [
            pygame.font.SysFont(None, 16),
            pygame.font.SysFont(None, 20),
            pygame.font.SysFont(None, 24),
            pygame.font.SysFont(None, 32)
        ]
        self.text_elements = {
            "notification": TextElement(self.screen, 20, 20, self.fonts[3], "", shadow=True, show=False),
            "fps": TextElement(self.screen, 20, 4, self.fonts[2], "0 fps", shadow=True, show=True)
        }
        self.workers = []
        self.surfaces = {
            "grass": pygame.Surface((self.tile_size, self.tile_size)),
            "water": pygame.Surface((self.tile_size, self.tile_size)),
            "mountain": pygame.Surface((self.tile_size, self.tile_size)),
            "snow": pygame.Surface((self.tile_size, self.tile_size)),
            "iron": pygame.Surface((self.tile_size-2, self.tile_size-2)),
            "copper": pygame.Surface((self.tile_size-2, self.tile_size-2)),
            "gold": pygame.Surface((self.tile_size-2, self.tile_size-2))
        }
        self.surfaces["grass"].fill((0,255,0))
        self.surfaces["water"].fill((0,0,255))
        self.surfaces["mountain"].fill((128,128,128))
        self.surfaces["snow"].fill((255,255,255))
        self.surfaces["iron"].fill((128, 128, 255))
        self.surfaces["copper"].fill((196, 0, 0))
        self.surfaces["gold"].fill((200, 255, 0))
        #self.bg = pygame.image.fromstring(self.map.image.tobytes(),self.map.image.size,self.map.image.mode).convert()
    
    def move_view(self, dx, dy):
        self.view_pos = (
            min(self.map_size[0]-self.view_max[0],max(0,self.view_pos[0]+dx)),
            min(self.map_size[1]-self.view_max[1],max(0,self.view_pos[1]+dy))
        )

    def input(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_UP]:
            self.move_view(0,-1)
        if pressed_keys[pygame.K_DOWN]:
            self.move_view(0,1)
        if pressed_keys[pygame.K_LEFT]:
            self.move_view(-1,0)
        if pressed_keys[pygame.K_RIGHT]:
            self.move_view(1,0)
        if pressed_keys[pygame.K_m]:
            self.show_map = self.show_map == False
        if pressed_keys[pygame.K_r]:
            self.show_resources = self.show_resources == False
        
        if pressed_keys[pygame.K_c] and self.mouse_mode == MouseMode.STANDBY:
            self.text_elements["notification"].update_text("Place Worker Unit")
            self.text_elements["notification"].show = True
            self.mouse_mode = MouseMode.PLACE_UNIT
            self.unit_to_place = Worker()
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()

        change = False
        if self.last_mouse_press != mouse_press[0]:
            self.last_mouse_press = mouse_press[0]
            change = True
        if change is True and self.mouse_mode != MouseMode.STANDBY and mouse_press[0] is True:
            self.handle_mouse_left(mouse_pos)
        elif mouse_press[0] is True:
            dx = round((mouse_pos[0] - self.last_mouse_pos[0]) / self.tile_size)
            dy = round((mouse_pos[1] - self.last_mouse_pos[1]) / self.tile_size)
            if dx != 0 and dy != 0:
                self.move_view(dx*-1,dy*-1)
                self.mouse_dragging = True
        elif change is True and self.mouse_dragging is False and self.mouse_mode == MouseMode.STANDBY and mouse_press[0] is False:
            self.handle_standby_mouse_up(mouse_pos)
        if change is True and self.mouse_dragging is True and mouse_press[0] is False:
            self.mouse_dragging = False
        self.last_mouse_pos = mouse_pos

    def handle_standby_mouse_up(self, pos):
        map_pos = (
            math.floor(pos[0]/self.tile_size)+self.view_pos[0],
            math.floor(pos[1]/self.tile_size)+self.view_pos[1]
        )
        print("handle_standby_mouse_up pos:"+str(pos)+" map_pos:"+str(map_pos))
        handled = False
        for worker in self.workers:
            if worker.x == map_pos[0] and worker.y == map_pos[1]:
                self.unit_to_move = worker
                self.mouse_mode = MouseMode.MOVE_UNIT_TO
                self.text_elements["notification"].update_text("Click to move worker unit")
                self.text_elements["notification"].show = True
                handled = True
                break
        if handled is False:
            tile = game.get_tile(map_pos[0], map_pos[1])
            print("clicked tile: ("+str(map_pos)+") "+str(tile.t))
        

    def handle_mouse_left(self, pos):
        map_pos = (
            math.floor(pos[0]/self.tile_size) + self.view_pos[0],
            math.floor(pos[1]/self.tile_size) + self.view_pos[1]
        )
        if self.mouse_mode == MouseMode.PLACE_UNIT and self.unit_to_place is not None:
            self.unit_to_place.x = map_pos[0]
            self.unit_to_place.y = map_pos[1]
            self.workers.append(self.unit_to_place)
            self.unit_to_place = None
            self.text_elements["notification"].show = False
        
        if self.mouse_mode == MouseMode.MOVE_UNIT_TO and self.unit_to_move is not None:
            self.unit_to_move.walk_target = map_pos
            self.text_elements["notification"].show = False
        self.mouse_mode = MouseMode.STANDBY
    
    def get_tile(self, x, y) -> Tile:
        return self.map.tiles[y][x]

    def update(self):
        if self.last_tick < datetime.now() + timedelta(seconds=1):
            self.gametime = self.gametime + 1
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles)):
                tile = self.map.tiles[y][x]
                for structure in tile.structures:
                    structure.update(self.gametime)
        for worker in self.workers:
            worker.update(self)
    
    def in_view(self, tile):
        return tile.x >= self.view_pos[0] and tile.y >= self.view_pos[1] and tile.x <= self.view_pos[0] + self.view_max[0] and tile.y <= self.view_pos[1] + self.view_max[1]

    def tile_index(self, x, y):
        return x + (y * self.map_size[0])

    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.show_map is True:
            for y in range(self.view_pos[1],self.view_pos[1]+math.floor(self.screen_size[1]/self.tile_size)):
                for x in range(self.view_pos[0],self.view_pos[0]+math.floor(self.screen_size[0]/self.tile_size)):
                    tile = self.map.tiles[y][x]
                    if tile.t == TileType.GRASS:
                        surf = self.surfaces["grass"]
                    if tile.t == TileType.WATER:
                        surf = self.surfaces["water"]
                    if tile.t == TileType.SNOW:
                        surf = self.surfaces["snow"]
                    if tile.t == TileType.MOUNTAIN:
                        surf = self.surfaces["mountain"]
                    if tile.t == TileType.SAND:
                        surf = self.surfaces["sand"]
                    self.screen.blit(surf,((tile.x-self.view_pos[0])*self.tile_size,(tile.y-self.view_pos[1])*self.tile_size))

        if self.show_resources is True:
            for y in range(self.view_pos[1],self.view_pos[1]+math.floor(self.screen_size[1]/self.tile_size)):
                for x in range(self.view_pos[0],self.view_pos[0]+math.floor(self.screen_size[0]/self.tile_size)):
                    tile = self.map.tiles[y][x]
                    if tile.r == ResourceType.IRON:
                        rsurf = self.surfaces["iron"]
                        self.screen.blit(rsurf,((tile.x-self.view_pos[0])*self.tile_size+1,(tile.y-self.view_pos[1])*self.tile_size+1))
                    if tile.r == ResourceType.COPPER:
                        rsurf = self.surfaces["copper"]
                        self.screen.blit(rsurf,((tile.x-self.view_pos[0])*self.tile_size+1,(tile.y-self.view_pos[1])*self.tile_size+1))
                    if tile.r == ResourceType.GOLD:
                        rsurf = self.surfaces["gold"]
                        self.screen.blit(rsurf,((tile.x-self.view_pos[0])*self.tile_size+1,(tile.y-self.view_pos[1])*self.tile_size+1))

            for y in range(self.view_pos[1],self.view_pos[1]+math.floor(self.screen_size[1]/self.tile_size)):
                for x in range(self.view_pos[0],self.view_pos[0]+math.floor(self.screen_size[0]/self.tile_size)):
                    tile = self.map.tiles[y][x]
                    if tile.tree is True:
                        pygame.draw.circle(self.screen, (0, 128, 0), ((tile.x-self.view_pos[0])*self.tile_size+(self.tile_size/2), (tile.y-self.view_pos[1])*self.tile_size+(self.tile_size/2)), ((self.tile_size/4)*3))
        
        for worker in self.workers:
            if self.in_view(worker) is False:
                continue
            pygame.draw.circle(self.screen, (196, 128, 0), ((worker.x-self.view_pos[0])*self.tile_size+(self.tile_size/2), (worker.y-self.view_pos[1])*self.tile_size+(self.tile_size/2)), (self.tile_size/3))
        
        #UI
        for key in self.text_elements:
            self.text_elements[key].draw()

        #mouse
        if self.mouse_mode == MouseMode.PLACE_UNIT:
            pygame.draw.circle(self.screen, (128, 128, 0), (self.last_mouse_pos[0], self.last_mouse_pos[1]), math.floor(self.tile_size/2)+2)
        if self.mouse_mode == MouseMode.MOVE_UNIT_TO:
            pygame.draw.circle(self.screen, (0, 128, 0), (self.last_mouse_pos[0], self.last_mouse_pos[1]), math.floor(self.tile_size/3)+2)

class TextElement:
    def __init__(self, screen, x, y, font, text, color=(255,255,255), shadow=False, show=True):
        self.screen = screen
        self.x = x
        self.y = y
        self.show = show
        self.font = font
        self.color = color
        self.display_shadow = shadow
        self.text = self.font.render(text, True, color)
        self.shadow = self.font.render(text, True, (0,0,0))
    
    def update_text(self, text):
        self.text = self.font.render(text, True, self.color)
        self.shadow = self.font.render(text, True, (0,0,0))
    
    def draw(self):
        if self.show is False:
            return
        if self.display_shadow is True:
            self.screen.blit(self.shadow, (self.x+1, self.y-1))
            self.screen.blit(self.shadow, (self.x+1, self.y+1))
            self.screen.blit(self.shadow, (self.x-1, self.y-1))
            self.screen.blit(self.shadow, (self.x-1, self.y+1))
        self.screen.blit(self.text, (self.x, self.y))


if __name__ == "__main__":
    game = Game()
    pygame.mouse.set_visible(True)
    last_second = datetime.now()
    frame = 0
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
        game.input()
        game.update()
        game.draw()
        pygame.display.flip()
        if last_second < datetime.now() - timedelta(seconds=1):
            last_second = datetime.now()
            fps = frame
            frame = 0
            game.fps = fps
            game.text_elements["fps"].update_text(str(fps)+" fps")
        else:
            frame = frame + 1

    pygame.quit()
