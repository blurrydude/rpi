from enum import Enum

class Map:
    def __init__(self, img, tiles):
        self.image = img
        self.tiles = tiles

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.t = TileType.GRASS
        self.r = ResourceType.NONE
        self.q = 0
        self.structures = []

class ResourceType(Enum):
    NONE = 0,
    WATER = 1,
    STONE = 2,
    IRON = 3,
    COPPER = 4

class TileType(Enum):
    WATER = 0,
    SAND = 1,
    GRASS = 2,
    MOUNTAIN = 3,
    SNOW = 4

class MouseMode(Enum):
    STANDBY = 0,
    PLACE_UNIT = 1,
    PLACE_BUILDING = 2,
    MOVE_UNIT_TO = 3

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
    def __init__(self):
        self.x = 0
        self.y = 0
        self.walk_target = None

    def update(self, game):
        if self.walk_target is None:
            return
        
        left_x = right_x = next_x = self.x
        left_y = right_y = next_y = self.y
        
        if next_x < self.walk_target[0]:
            next_x = next_x + 1
            left_x = left_x + 1
        elif next_x > self.walk_target[0]:
            next_x = next_x - 1
            right_x = right_x - 1
        if next_y < self.walk_target[1]:
            next_y = next_y + 1
            left_y = left_y + 1
        elif next_y > self.walk_target[1]:
            next_y = next_y - 1
            right_y = right_y - 1
        next_tile = game.get_tile(next_x, next_y)
        left_tile = game.get_tile(left_x, left_y)
        right_tile = game.get_tile(right_x, right_y)
        if next_tile.t not in [TileType.WATER, TileType.SNOW]:
            self.x = next_x
            self.y = next_y
        elif left_tile.t not in [TileType.WATER, TileType.SNOW]:
            self.x = left_x
            self.y = left_y
        elif right_tile.t not in [TileType.WATER, TileType.SNOW]:
            self.x = right_x
            self.y = right_y
        else:
            self.walk_target = None
        if self.x == self.walk_target[0] and self.y == self.walk_target[1]:
            self.walk_target = None
