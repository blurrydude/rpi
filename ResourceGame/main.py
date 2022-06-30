from datetime import datetime, timedelta
from random import randint, random
import pygame
from mapgen import MapMaker
from models import TileType
pygame.init()

class WaterPump:
    def __init__(self, tile):
        self.tile = tile
        self.last_pump = 0
        self.gallons_stored = 0
        self.capacity = 5000
        self.speed = 2
    
    def update(self, gametime):
        if self.gallons_stored < self.capacity and gametime - self.last_pump > (60 / self.speed):
            self.last_pump = gametime
            self.gallons_stored = self.gallons_stored + 1

class Mine:
    def __init__(self, tile, rtype):
        self.tile = tile
        self.last_mine = 0
        self.ore_stored = 0
        self.capacity = 500
        self.speed = 10
        self.resource_type = rtype
    
    def update(self, gametime):
        if self.ore_stored < self.capacity and self.tile.q > 0 and gametime - self.last_mine > (60 / self.speed):
            self.last_mine = gametime
            self.ore_stored = self.ore_stored + 1
            self.tile.q = self.tile.q - 1

class Worker:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, gametime):
        pass

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
        self.fonts = [
            pygame.font.SysFont(None, 16),
            pygame.font.SysFont(None, 20),
            pygame.font.SysFont(None, 24),
            pygame.font.SysFont(None, 32)
        ]
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
        if pressed_keys[pygame.K_w]:
            self.workers.append(Worker(randint(0,self.map_size[0]),randint(0,self.map_size[1])))
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()
        if self.last_mouse_press != mouse_press[0]:
            self.last_mouse_press = mouse_press[0]
        elif mouse_press[0] is True:
            dx = round((mouse_pos[0] - self.last_mouse_pos[0]) / self.tile_size)
            dy = round((mouse_pos[1] - self.last_mouse_pos[1]) / self.tile_size)
            self.move_view(dx*-1,dy*-1)
        self.last_mouse_pos = mouse_pos

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
        txt = self.fonts[3].render('hello', True, (255,255,255))
        shdw = self.fonts[3].render('hello', True, (0,0,0))
        self.screen.blit(shdw, (21, 21))
        self.screen.blit(shdw, (19, 19))
        self.screen.blit(shdw, (19, 21))
        self.screen.blit(shdw, (21, 19))
        self.screen.blit(txt, (20, 20))

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
