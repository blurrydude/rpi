from random import random

class Player:
    def __init__(self):
        self.health = 100
        self.hunger = 0
        self.thirst = 0
        self.condition = 100
        self.inventory = []
        self.x = 0
        self.y = 0

class Area:
    def __init__(self):
        self.name = "flat desert"
        self.has_water = False
        self.huntable = False
        self.rough = False
        self.can_rain = False
        self.can_snow = False

class Game:
    def __init__(self):
        self.turn = 0
        self.map = []

    def make_map(self):
        self.map = []
        for x in range(32):
            col = []
            for y in range(32):
                area = Area()
                # make area stuff
                col.append(area)
            self.map.append(col)

    def help_command(self):
        print("WAIT, INVENTORY (or INV), LOOK, TRAVEL, MAKE")
    
    def tick(self):
        command = input().lower()
        if command == "help":
            self.help_command()
        elif command == "wait":
            print("You wait.")
        else:
            print("That's not a command. Use HELP for more info")
        self.turn = self.turn + 1
        self.tick()

if __name__ == "__main__":
    game = Game()
    game.tick()