from enum import Enum

from matplotlib import image

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