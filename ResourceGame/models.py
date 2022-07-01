from enum import Enum

class Map:
    def __init__(self, img, tiles):
        self.image = img
        self.tiles = tiles
        self.trees = []

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.t = TileType.GRASS
        self.r = ResourceType.NONE
        self.q = 0
        self.tree = False
        self.structures = []

class ResourceType(Enum):
    NONE = 0,
    WATER = 1,
    STONE = 2,
    IRON = 3,
    COPPER = 4,
    GOLD = 5,
    LUMBER = 6

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
        self.prefs = {
            "N":  [(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)],
            "E":  [(1,0),(1,-1),(1,1),(0,-1),(0,1)],
            "S":  [(0,1),(1,1),(-1,1),(1,0),(-1,0)],
            "W":  [(-1,0),(-1,1),(-1,-1),(0,1),(0,-1)],
            "EN": [(1,-1),(0,-1),(1,0),(-1,-1),(1,1)],
            "ES": [(1,1),(1,0),(0,1),(1,-1),(-1,1)],
            "WN": [(-1,-1),(-1,0),(0,-1),(-1,1),(1,-1)],
            "WS": [(-1,1),(0,1),(-1,0),(1,1),(-1,-1)],
        }

    def update(self, game):
        if self.walk_target is None:
            return
        
        dir = ""
        if self.x < self.walk_target[0]:
            dir = dir + "E"
        elif self.x > self.walk_target[0]:
            dir = dir + "W"
        if self.y < self.walk_target[1]:
            dir = dir + "S"
        elif self.y > self.walk_target[1]:
            dir = dir + "N"
        if dir == "":
            self.walk_target = None
        prefs = self.prefs[dir]
        for pref in prefs:
            next_x = pref[0]+self.x
            next_y = pref[1]+self.y
            next_tile = game.get_tile(next_x, next_y)
            if next_tile.t not in [TileType.WATER, TileType.SNOW]:
                print(dir+" walk next "+str(next_x)+","+str(next_y)+" "+str(next_tile.t))
                self.x = next_x
                self.y = next_y
                break
        if self.x == self.walk_target[0] and self.y == self.walk_target[1]:
            print("done walking")
            self.walk_target = None
