from datetime import datetime, timedelta
import math
from random import randint, random
import pygame
from mapgen import MapMaker
from models import TileType, Worker, MouseMode
pygame.init()

class Game:
    def __init__(self):
        self.tile_size = 8
        self.screen_size = (1024, 768)
        self.screen = pygame.display.set_mode([self.screen_size[0],self.screen_size[1]])
        self.running = True
        self.last_tick = datetime.now()
        self.gametime = 0
        maker = MapMaker()
        self.map = maker.gen_map()
        self.map_size = self.map.image.size
        self.view_pos = (0,0)
        self.view_max = (self.screen_size[0]/self.tile_size,self.screen_size[1]/self.tile_size)
        self.last_mouse_pos = (0,0)
        self.last_mouse_press = False
        self.unit_to_place = None
        self.structure_to_place = None
        self.unit_to_move = None
        self.mouse_mode = MouseMode.STANDBY
        self.fonts = [
            pygame.font.SysFont(None, 16),
            pygame.font.SysFont(None, 20),
            pygame.font.SysFont(None, 24),
            pygame.font.SysFont(None, 32)
        ]
        self.text_elements = {
            "notification": TextElement(self.screen, 20, 20, self.fonts[3], "", shadow=True, show=False)
        }
        self.workers = []
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
        
        if pressed_keys[pygame.K_c] and self.mouse_mode == MouseMode.STANDBY:
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
            self.move_view(dx*-1,dy*-1)
        self.last_mouse_pos = mouse_pos

    def handle_mouse_left(self, pos):
        if self.mouse_mode == MouseMode.PLACE_UNIT and self.unit_to_place is not None:
            self.unit_to_place.x = math.floor(pos[0]/8) + self.view_pos[0]
            self.unit_to_place.y = math.floor(pos[1]/8) + self.view_pos[1]
            self.workers.append(self.unit_to_place)
        
        self.mouse_mode = MouseMode.STANDBY

    def update(self):
        if self.last_tick < datetime.now() + timedelta(seconds=1):
            self.gametime = self.gametime + 1
        for tile in self.map.tiles:
            for structure in tile.structures:
                structure.update(self.gametime)
    
    def in_view(self, tile):
        return tile.x >= self.view_pos[0] and tile.y >= self.view_pos[1] and tile.x <= self.view_pos[0] + self.view_max[0] and tile.y <= self.view_pos[1] + self.view_max[1]

    def tile_index(self, x, y):
        return x + (y * self.map_size[0])

    def draw(self):
        self.screen.fill((0, 0, 0))
        for tile in self.map.tiles:
            if self.in_view(tile) is False:
                continue
            surf = pygame.Surface((self.tile_size, self.tile_size))
            if tile.t == TileType.GRASS:
                surf.fill((0, 255, 0))
            if tile.t == TileType.WATER:
                surf.fill((0, 0, 255))
            if tile.t == TileType.SNOW:
                surf.fill((255, 255, 255))
            if tile.t == TileType.MOUNTAIN:
                surf.fill((196, 196, 196))
            if tile.t == TileType.SAND:
                surf.fill((255, 196, 0))
            self.screen.blit(surf,((tile.x-self.view_pos[0])*self.tile_size,(tile.y-self.view_pos[1])*self.tile_size))
        
        for worker in self.workers:
            if self.in_view(worker) is False:
                continue
            pygame.draw.circle(self.screen, (255, 0, 0), ((worker.x-self.view_pos[0])*self.tile_size, (worker.y-self.view_pos[1])*self.tile_size), 10)
        
        #UI

        #mouse
        if self.mouse_mode == MouseMode.PLACE_UNIT:
            pygame.draw.circle(self.screen, (255, 0, 0), (self.last_mouse_pos[0], self.last_mouse_pos[1]), 10)

class TextElement:
    def __init__(self, screen, x, y, font, text, color=(255,255,255), shadow=False, show=True):
        self.screen = screen
        self.x = x
        self.y = y
        self.show = show
        self.font = font
        self.display_shadow = shadow
        self.text = self.font.render(text, True, color)
        self.shadow = self.font.render(text, True, (0,0,0))
    
    def update_text(self, text):
        self.text = self.fonts[self.font].render(text, True, self.color)
        self.shadow = self.fonts[self.font].render(text, True, (0,0,0))
    
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
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
        game.input()
        game.update()
        game.draw()
        pygame.display.flip()

    pygame.quit()
