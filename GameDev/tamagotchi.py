# Tamagotchi class
class Tamagotchi:
    def __init__(self, name, age, energy, happiness):
        self.name = name
        self.age = age
        self.energy = energy
        self.happiness = happiness

    def feed(self):
        self.energy += 5
        if self.energy > 100:
            self.energy = 100
        print(f'{self.name} has been fed. Energy level: {self.energy}')

    def play(self):
        self.happiness += 5
        if self.happiness > 100:
            self.happiness = 100
        print(f'{self.name} has played. Happiness level: {self.happiness}')

    def wait(self):
        self.energy -= 1
        self.happiness -= 2
        if self.energy > 100:
            self.energy = 100
        if self.happiness < 0:
            self.happiness = 0

    def rest(self):
        self.energy += 3
        self.happiness -= 2
        if self.energy > 100:
            self.energy = 100
        if self.happiness < 0:
            self.happiness = 0
        print(f'{self.name} has rested. Energy level: {self.energy}, happiness level: {self.happiness}')

    def sleep(self):
        self.energy += 10
        self.happiness += 5
        if self.energy > 100:
            self.energy = 100
        if self.happiness > 100:
            self.happiness = 100
        print(f'{self.name} has slept. Energy level: {self.energy}, happiness level: {self.happiness}')

    def status(self):
        print(f'Name: {self.name}')
        print(f'Age: {self.age}')
        print(f'Energy: {self.energy}')
        print(f'Happiness: {self.happiness}')

# Game loop
def game_loop(tamagotchi):
    while True:
        if tamagotchi.energy <= 20 or tamagotchi.happiness <= 20:
            print(f'{tamagotchi.name} is too tired or unhappy and needs to sleep!')
            tamagotchi.sleep()
            continue
        print(f'{tamagotchi.name} is {tamagotchi.age} years old and has an energy level of {tamagotchi.energy} and a happiness level of {tamagotchi.happiness}')
        print('What would you like to do?')
        print('1. Feed')
        print('2. Play')
        print('3. Rest')
        print('4. View Status')
        action = input('Enter the number of the action you would like to take: ')
        if action == '1':
            tamagotchi.feed()
        elif action == '2':
            tamagotchi.play()
        elif action == '3':
            tamagotchi.rest()
        elif action == '4':
            tamagotchi.status()
        else:
            print('Invalid action')

# Create a tamagotchi and start the game loop
tamagotchi = Tamagotchi('Tammy', 1, 50, 50)
game_loop(tamagotchi)

eye_ball_blink_anim = [
    [
        [0,1,1,1,0],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,0,1,1],
        [1,1,1,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,1,1,1,0],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,0,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,0,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [1,1,0,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0]
    ]
]