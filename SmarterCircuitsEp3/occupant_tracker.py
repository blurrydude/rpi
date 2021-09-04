import json
import random

class SmarterHouse:
    def __init__(self):
        self.rooms = []
    
    def add_room(self, room):
        room.house = self
        self.rooms.append(room)

class SmarterRoom:
    def __init__(self, label):
        self.label = label
        self.portals = []
        self.house = None
        self.occupants = 0
    
    def add_portal(self, portal):
        self.portals.append(portal)
    
    def occupant_leaving(self):
        if self.occupants > 0:
            self.occupants = self.occupants - 1
    
    def occupant_entering(self):
        self.occupants = self.occupants + 1

class SmarterPortal:
    def __init__(self, inner, outer):
        self.outer_room = outer
        self.inner_room = inner
    
    def traverse(self, direction):
        if direction == "in":
            if self.inner_room is not None:
                self.inner_room.occupant_entering()
            if self.outer_room is not None:
                self.outer_room.occupant_leaving()
        if direction == "out":
            if self.inner_room is not None:
                self.inner_room.occupant_leaving()
            if self.outer_room is not None:
                self.outer_room.occupant_entering()

house = SmarterHouse()

living_room = SmarterRoom("Livingroom")
dining_room = SmarterRoom("Dining Room")
day_room = SmarterRoom("Day Room")
deck = SmarterRoom("Deck")
game_room = SmarterRoom("Game Room")
kitchen = SmarterRoom("Kitchen")
stairway = SmarterRoom("Stairway")
garage = SmarterRoom("Garage")
laundry = SmarterRoom("Laundry Room")
storage = SmarterRoom("Storage Room")
shop = SmarterRoom("Shop")
hallway = SmarterRoom("Hallway")
gym = SmarterRoom("Gym")
library = SmarterRoom("Library")
guest_bath = SmarterRoom("Guest Bath")
bedroom = SmarterRoom("Bedroom")
master_bath = SmarterRoom("Master Bath")

front_door = SmarterPortal(living_room, None)
living_room.add_portal(front_door)

lr_to_hw = SmarterPortal(living_room, hallway)
living_room.add_portal(lr_to_hw)
hallway.add_portal(lr_to_hw)

hw_to_gym = SmarterPortal(gym, hallway)
gym.add_portal(hw_to_gym)
hallway.add_portal(hw_to_gym)

hw_to_lb = SmarterPortal(library, hallway)
library.add_portal(hw_to_lb)
hallway.add_portal(hw_to_lb)

hw_to_br = SmarterPortal(bedroom, hallway)
bedroom.add_portal(hw_to_br)
hallway.add_portal(hw_to_br)

br_to_mb = SmarterPortal(master_bath, bedroom)
master_bath.add_portal(br_to_mb)
bedroom.add_portal(br_to_mb)

lr_to_kn = SmarterPortal(kitchen, living_room)
kitchen.add_portal(lr_to_kn)
living_room.add_portal(lr_to_kn)

lr_to_dr = SmarterPortal(dining_room, living_room)
dining_room.add_portal(lr_to_dr)
living_room.add_portal(lr_to_dr)

dr_to_kn = SmarterPortal(kitchen, dining_room)
kitchen.add_portal(dr_to_kn)
dining_room.add_portal(dr_to_kn)

dr_to_day = SmarterPortal(dining_room, day_room)
dining_room.add_portal(dr_to_day)
day_room.add_portal(dr_to_day)

day_to_deck = SmarterPortal(day_room, deck)
day_room.add_portal(day_to_deck)
deck.add_portal(day_to_deck)

dr_to_gr = SmarterPortal(game_room, dining_room)
game_room.add_portal(dr_to_gr)
dining_room.add_portal(dr_to_gr)

gr_to_deck = SmarterPortal(game_room, deck)
game_room.add_portal(gr_to_deck)
deck.add_portal(gr_to_deck)

deck_to_back = SmarterPortal(deck, None)
deck.add_portal(deck_to_back)

deck_to_side = SmarterPortal(deck, None)
deck.add_portal(deck_to_side)

kn_to_sw = SmarterPortal(kitchen, stairway)
kitchen.add_portal(kn_to_sw)
stairway.add_portal(kn_to_sw)

sw_to_gg = SmarterPortal(stairway, garage)
stairway.add_portal(sw_to_gg)
garage.add_portal(sw_to_gg)

gg_to_ly = SmarterPortal(laundry, garage)
laundry.add_portal(gg_to_ly)
garage.add_portal(gg_to_ly)

gg_to_sr = SmarterPortal(storage, garage)
storage.add_portal(gg_to_sr)
garage.add_portal(gg_to_sr)

gg_to_b1 = SmarterPortal(garage, None)
garage.add_portal(gg_to_b1)

gg_to_b2 = SmarterPortal(garage, None)
garage.add_portal(gg_to_b2)

house.add_room(living_room)
house.add_room(dining_room)
house.add_room(day_room)
house.add_room(deck)
house.add_room(game_room)
house.add_room(kitchen)
house.add_room(garage)
house.add_room(stairway)
house.add_room(laundry)
house.add_room(storage)
house.add_room(shop)
house.add_room(hallway)
house.add_room(gym)
house.add_room(library)
house.add_room(guest_bath)
house.add_room(bedroom)
house.add_room(master_bath)

# doors = [
#     front_door,
#     lr_to_hw,
#     hw_to_gym,
#     hw_to_lb,
#     hw_to_br,
#     br_to_mb,
#     lr_to_kn,
#     lr_to_dr,
#     dr_to_day,
#     dr_to_gr,
#     dr_to_kn,
#     kn_to_sw,
#     sw_to_gg,
#     gg_to_ly,
#     gg_to_sr,
#     gg_to_b1,
#     gg_to_b2
#     ]

pointer = living_room

def walk():
    global pointer
    roll = random.randint(0,len(pointer.portals)-1)
    while pointer.portals[roll].outer_room is None:
        roll = random.randint(0,len(pointer.portals)-1)
    if pointer is pointer.portals[roll].outer_room:
        pointer.portals[roll].traverse("in")
        pointer = pointer.portals[roll].inner_room
    else:
        pointer.portals[roll].traverse("out")
        pointer = pointer.portals[roll].outer_room

print(pointer.label)
for i in range(15):
    walk()
    print(pointer.label)
print("---last state---")
for room in house.rooms:
    print(room.label+" = "+str(room.occupants))