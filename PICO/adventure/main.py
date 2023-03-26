#from SmarterCircuits import Display, Button
import time
import random

class Player:
    def __init__(self, game):
        self.game = game
        self.health = 100
        self.hydration = 100
        self.nourishment = 100
        self.energy = 100
        self.inventory = [
            self.game.item_factory.knife()
        ]
        self.temperature = 98.8
    
    def sweep_inventory(self):
        to_sweep = []
        for item in self.inventory:
            if item.sweep:
                to_sweep.append(item)
            
        for item in to_sweep:
            self.inventory.remove(item)
    
    def inventory_contains_item(self, itemname):
        for item in self.inventory:
            if item.name == itemname:
                return True
        return False
    
    def inventory_contains_weapon(self):
        for item in self.inventory:
            if item.is_weapon:
                return True
        return False
    
    def inventory_contains_pole(self):
        for item in self.inventory:
            if item.is_fishing_pole:
                return True
        return False

class Scene:
    def __init__(self, type="woods", resources=[]):
        self.resources = resources
        self.type = type

class Action:
    def __init__(self):
        self.health_mod = 0
        self.hydration_mod = 0
        self.nourishment_mod = 0
        self.enery_mod = 0
        self.create_item = None

class Item:
    def __init__(self, name="widget", 
                 health_mod=0, hydration_mod=0, nourishment_mod=0, enery_mod=0, 
                 uses=1, weight=1, storage=0,
                 equipable=False,consumable=False,stackable=False,
                 insulation=0,waterproof=False,is_weapon=False,
                 weapon_damage=0,weapon_accuracy=0,
                 is_fishing_pole=False,is_trap=False):
        self.health_mod = health_mod
        self.hydration_mod = hydration_mod
        self.nourishment_mod = nourishment_mod
        self.enery_mod = enery_mod
        self.uses = uses
        self.weight = weight
        self.storage = storage
        self.equipable = equipable
        self.consumable = consumable
        self.insulation = insulation
        self.waterproof = waterproof
        self.is_weapon = is_weapon
        self.stackable = stackable
        self.weapon_damage = weapon_damage
        self.weapon_accuracy = weapon_accuracy
        self.is_fishing_pole = is_fishing_pole
        self.is_trap = is_trap
        self.name = name
        self.sweep = False

    def use(self, user):
        if self.consumable:
            self.uses = self.uses - 1
        if self.health_mod != 0:
            user.health = user.health + self.health_mod
        if self.hydration_mod != 0:
            user.hydration = user.hydration + self.hydration_mod
        if self.nourishment_mod != 0:
            user.nourishment = user.nourishment + self.nourishment_mod
        if self.enery_mod != 0:
            user.enery = user.enery + self.enery_mod

        self.check_consumed()
    
    def check_consumed(self):
        if self.uses <= 0:
            self.sweep = True

class ItemFactory:
    def __init__(self):
        pass

    def dead_bird(self):
        return Item("dead bird",hydration_mod=1,nourishment_mod=5,enery_mod=-1)

    def dead_rabbit(self):
        return Item("dead rabbit",0,2,10,-2,1,2,0,False,True,False,0,False,False,0,0,False,False)

    def knife(self):
        return Item("knife",0,0,0,0,1,1,0,False,False,False,0,False,True,2,1,False,False)

class Game:
    def __init__(self, debug=False):
        self.item_factory = ItemFactory()
        self.day = 0
        self.debug = debug
        self.temperature = 65
        self.humidity = 35
        self.weather_intensity = 0
        self.time_of_day = 12
        self.scenes = []
        self.player = Player(self)
        self.refresh_scenes()
        self.current_scene = random.choice(self.scenes)

    def refresh_scenes(self):
        self.scenes = [
            Scene("in the woods",["wood"]),
            Scene("at a riverbank",["wood","water","fish"]),
            Scene("on a hill",[]),
            Scene("in a clearing",["wood","rabbit"]),
            Scene("on a path",["wood"]),
            Scene("in a meadow",["rabbit","bird"])
        ]

    def time_of_day_light(self):
        if self.time_of_day > 3 and self.time_of_day <= 7:
            return 1
        if self.time_of_day > 7 and self.time_of_day <= 10:
            return 2
        if self.time_of_day > 10 and self.time_of_day <= 14:
            return 3
        if self.time_of_day > 14 and self.time_of_day <= 17:
            return 2
        if self.time_of_day > 17 and self.time_of_day <= 20:
            return 1
        if self.time_of_day > 20 and self.time_of_day <= 0:
            return 0
        if self.time_of_day > 0 and self.time_of_day <= 3:
            return 0

    def time_of_day_word(self):
        if self.time_of_day > 3 and self.time_of_day <= 7:
            return "early morning"
        if self.time_of_day > 7 and self.time_of_day <= 10:
            return "morning"
        if self.time_of_day > 10 and self.time_of_day <= 14:
            return "midday"
        if self.time_of_day > 14 and self.time_of_day <= 17:
            return "early evening"
        if self.time_of_day > 17 and self.time_of_day <= 20:
            return "evening"
        if self.time_of_day > 20 and self.time_of_day <= 7:
            return "night"
        if self.time_of_day > 0 and self.time_of_day <= 3:
            return "deep night"
    
    def line(self):
        print("##########################################")

    def display_scene(self, message=""):
        self.clear_screen()
        self.line()
        print(f"It is currently {self.time_of_day_word()}.")
        print(f"You are {self.current_scene.type}.")
        if len(self.current_scene.resources) == 0:
            print("There is nothing of interest or use here.")
        else:
            print("The following resources are in the area:")
            for res in self.current_scene.resources:
                print(f"    {res}")
        self.line()
        if len(message) > 1:
            print(message)
            self.line()
        print("What would you like to do?")

    def clear_screen(self):
        if self.debug:
            return
        self.move_cursor(0,0)
        for i in range(100):
            print("                                                                                                          ")
        self.move_cursor(0,0)

    def move_cursor(self, y, x):
        print("\033[%d;%dH" % (y, x))
    
    def pick_hunt(self, animals, message=""):
        self.clear_screen()
        if message != "":
            self.line
            print(message)
        self.line()
        print("Animals in the area:")
        for animal in animals:
            print(f"    {animal}")
        print("Which animal would you like to hunt?")
        choice = input()
        print(f"choice:{choice}")
        if choice == 'back':
            self.display_scene()
        if choice not in animals:
            self.pick_hunt(animals,"That is not a valid choice. Type 'back' to cancel.")
            return
        self.hunt_animal(choice)

    def hunt(self):
        has_weapon = self.player.inventory_contains_weapon()
        if has_weapon is False:
            self.display_scene("You have no weapon.")
            return
        animals = []
        if "rabbit" in self.current_scene.resources:
            animals.append("rabbit")
        if "bird" in self.current_scene.resources:
            animals.append("bird")
        if len(animals) == 0:
            self.display_scene("There are no animals here to hunt.")
            return
        if len(animals) == 1:
            self.hunt_animal(animals[0])
            return
        self.pick_hunt(animals)

    def pick_hunting_weapon(self, animal, weapons, message=""):
        self.clear_screen()
        if message != "":
            self.line
            print(message)
        self.line()
        print("Weapons on hand:")
        for weapon in weapons:
            print(f"    {weapon}")
        print("Which weapon would you like to use?")
        choice = input()
        print(f"choice:{choice}")
        if choice == 'back':
            self.display_scene()
        if choice not in weapons:
            self.pick_hunt(weapons,"That is not a valid choice. Type 'back' to cancel.")
            return
        self.hunt_animal_with_weapon(animal, choice)

    def hunt_animal(self, animal):
        weapons = []
        for item in self.player.inventory:
            if item.is_weapon:
                weapons.append(item.name)
        weapon_count = len(weapons)
        if weapon_count == 0:
            self.display_scene("Not sure how you got here, but you have no weapon.")
            return
        if weapon_count == 1:
            self.hunt_animal_with_weapon(animal, weapons[0])
            return
        self.pick_hunting_weapon(animal, weapons)
    
    def hunt_animal_with_weapon(self, animal, weapon):
        weapon_item = None
        for item in self.player.inventory:
            if item.name == weapon:
                weapon_item = item
                break
        if weapon_item is None:
            self.display_scene("Bad juju... not sure how that happened.")
        
        self.pass_time()

        reward = None
        difficulty = 0
        if self.player.energy < 30:
            difficulty = difficulty + 2
        if self.player.health < 30:
            difficulty = difficulty + 2
        difficulty = difficulty + (3 - self.time_of_day_light())
        if animal == "rabbit":
            difficulty = difficulty + 2
            reward = self.item_factory.dead_rabbit()
        if animal == "bird":
            difficulty = difficulty + 3
            reward = self.item_factory.dead_bird()
        
        roll = random.randint(1,12)
        roll + weapon_item.weapon_accuracy
        if roll >= difficulty:
            self.player.inventory.append(reward)
            roll = random.randint(1,12)
            if roll < 3:
                self.current_scene.resources.remove(animal)
                worse = " but scared the rest away."
            self.display_scene(f"Congratulation. You bagged a {reward.name}{worse}.")
            return
        worse = ""
        roll = random.randint(1,12)
        if roll < 3:
            self.current_scene.resources.remove(animal)
            worse = " and you scared them all away."
        self.display_scene(f"You failed to hunt a {animal}{worse}.")
    
    def pass_time(self, hours = 1):
        self.time_of_day = self.time_of_day + hours
        if self.time_of_day > 23:
            self.time_of_day = 0
            self.day = self.day + 1
    
    def activity(self, difficulty):
        self.player.energy = self.player.energy - difficulty
        self.player.hydration = self.player.hydration - difficulty * 2
        self.player.nourishment = self.player.nourishment - difficulty * 3

    def travel(self):
        if self.player.energy < 10:
            self.display_scene("You are too tired to travel.")
        if self.player.health < 10:
            self.display_scene("You are in no condition to travel.")
        if self.time_of_day_light() == 0:
            self.display_scene("It is too dark to travel.")
        eta = random.randint(1,4)
        self.pass_time(eta)
        self.activity(eta*2)
        self.refresh_scenes()
        self.current_scene = random.choice(self.scenes)
        self.display_scene(f"You traveled for {eta} hours.")
    
    def display_inventory(self, message = ""):
        items = []
        stackable_items = {}
        weights = {}
        total_weight = 0
        for item in self.player.inventory:
            weights[item.name] = item.weight
            total_weight = total_weight + item.weight
            if item.stackable is False:
                items.append(item.name)
                continue
            if item.name not in items.keys():
                items[item.name] = 0
        self.clear_screen()
        self.line()
        print(f"Inventory ----- total weight carried: {total_weight}")
        self.line()
        for item in items:
            print(f"    1 x {item} ({weights[item]} lbs)")
        for item in stackable_items:
            amount = items[item]
            print(f"    {amount} x {item} ({(weights[item]*amount)} lbs)")
        self.line()
        if len(message) > 1:
            print(message)
            self.line()
        print("What would you like to do?")
    
    def display_stats(self):
        self.clear_screen()
        self.line()
        print("Stats")
        self.line()
        print(f"Health: {self.player.health}")
        print(f"Energy: {self.player.energy}")
        print(f"Hydration: {self.player.hydration}")
        print(f"Nourishment: {self.player.nourishment}")
        print(f"Temperature: {self.player.temperature}")
        self.line()
        print("What would you like to do?")

    def display_help(self):
        self.clear_screen()
        todlight = self.time_of_day_light()
        self.line()
        print("Available Actions")
        self.line()
        print("look")
        print("stats")
        if "wood" in self.current_scene.resources and todlight > 0:
            print("gather wood")
        if "fish" in self.current_scene.resources and todlight > 0 and self.player.inventory_contains_pole():
            print("fish")
        if "bird" in self.current_scene.resources or "rabbit" in self.current_scene.resources:
            print("hunt")
        if self.player.health >= 10 and self.player.energy >= 10 and todlight > 0:
            print("travel")
        
        self.line()
        print("What would you like to do?")
    
    def gather(self, resource):


    def handle_command(self, command):
        if command == "look":
            self.display_scene()
        if command == "stats":
            self.display_stats()
        elif command == "hunt":
            self.hunt()
        elif command == "travel":
            self.travel()
        elif command == "inv" or command == "inventory":
            self.display_inventory()
        elif command == "help":
            self.display_help()
        elif command == "quit" or command == "exit":
            exit()
        elif command == "debug":
            self.debug = self.debug is False
            state = "disabled"
            if self.debug:
                state = "enabled"
            self.display_scene(f"Debugging {state}")
        else:
            self.display_scene("That is not a valid action. Type 'help' for available actions.")

    #def do_action(self, action):

if __name__ == "__main__":
    # initialize the display and buttons
    # screen = Display()
    
    # red_button = Button(16)
    # green_button = Button(17)
    # blue_button = Button(18)

    game = Game(True)

    game.display_scene()
    while True:
        command = input()
        print(f"command: {command}")

        game.handle_command(command)
