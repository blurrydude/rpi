class Tamagotchi:
    def __init__(self, name, age, energy, happiness):
        self.name = name
        self.age = age
        self.energy = energy
        self.hunger = energy
        self.happiness = happiness
        self.temperature = 72
        self.temp_high = 76
        self.temp_low = 62
        self.uncomfortable = False
    
    def check_temp(self):
        if self.temperature < self.temp_low:
            self.temp_low = self.temperature
        if self.temperature > self.temp_high:
            self.temp_high = self.temperature
        print(str(self.temperature)+' of '+str(self.temp_low)+'/'+str(self.temp_high))
        low_diff = self.temperature - self.temp_low
        temp_range = self.temp_high - self.temp_low
        if temp_range == 0:
            self.uncomfortable = False
            return
        if low_diff == 0 or low_diff / temp_range < 0.2:
            #I don't like it
            self.happiness -= 1
            self.uncomfortable = True

    def feed(self):
        self.happiness += 2
        self.hunger += 10
        if self.happiness > 100:
            self.happiness = 100
        if self.hunger > 100:
            self.hunger = 100

    def play(self):
        self.happiness += 5
        self.hunger -= 2
        if self.hunger < 10:
            self.happiness -= 2
        if self.hunger < 5:
            self.happiness -= 5
        if self.happiness > 100:
            self.happiness = 100
        if self.hunger < 0:
            self.hunger = 0

    def rest(self):
        self.energy += 3
        self.happiness -= 1
        self.hunger -= 2
        if self.hunger < 10:
            self.happiness -= 2
        if self.hunger < 5:
            self.happiness -= 5
        if self.energy > 100:
            self.energy = 100
        if self.happiness < 0:
            self.happiness = 0
        if self.hunger < 0:
            self.hunger = 0

    def wait(self):
        self.age = self.age + 1
        self.energy -= 1
        self.happiness -= 1
        self.hunger -= 2
        self.check_temp()
        if self.hunger < 10:
            self.happiness -= 2
        if self.hunger < 5:
            self.happiness -= 5
        if self.energy < 0:
            self.energy = 0
        if self.happiness < 0:
            self.happiness = 0
        if self.hunger < 0:
            self.hunger = 0

    def sleep(self):
        self.energy += 10
        self.happiness += 5
        self.hunger -= 2
        if self.hunger < 10:
            self.happiness -= 2
        if self.hunger < 5:
            self.happiness -= 5
        if self.energy > 100:
            self.energy = 100
        if self.happiness > 100:
            self.happiness = 100
        if self.hunger < 0:
            self.hunger = 0
