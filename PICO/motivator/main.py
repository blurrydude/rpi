import random
from machine import Pin, PWM, I2C, RTC
from buzzer import Buzzer
from sensor import Sensor
from display import Display
from buttons import Buttons
import time

motivations = []
fight = []
buzzer = Buzzer()
sensor = Sensor()
display = Display()
buttons = Buttons()
rtc = RTC()
current_screen = 'main'
screen_text = {
    "main": [
        "R - Log",
        "G - Motivate",
        "B - Stats",
        "Y - Craving"
    ],
    "log": [
        "R - Cigarette",
        "G - Food",
        "B - Water",
        "Y - Exercise"
    ]
}
log = []
temp_amount = 0
temp_type = ''
bad_type = 'cigarette'
bad_type_proper = 'Cigarette'

def load_data():
    global bad_type
    global bad_type_proper
    global motivations
    global fight
    global screen_text
    file = open("config.txt", 'r')
    content = file.read()
    file.close()
    lines = content.replace('\r','').split('\n')
    bad_type_proper = lines[0].split('=')[1]
    bad_type = bad_type_proper.lower()
    print("bad_type_proper: "+bad_type_proper)
    print("bad_type: "+bad_type)
    pointer = 2
    while lines[pointer] != 'end':
        motivations.append(lines[pointer])
        print("motivation: "+lines[pointer])
        pointer = pointer + 1
    pointer = pointer + 2
    while lines[pointer] != 'end':
        fight.append(lines[pointer])
        print("fight: "+lines[pointer])
        pointer = pointer + 1
    screen_text['log'][0] = 'R - '+bad_type_proper

def save_log():
    file = open('log.txt','w')
    for entry in log:
        file.write(entry["time"]+"|"+entry["type"]+"|"+str(entry["amount"]))
    file.close()

def load_log():
    global log
    file = open("log.txt", 'r')
    content = file.read()
    file.close()
    lines = content.replace('\r','').split('\n')
    for line in lines:
        data = line.split('|')
        log.append({"time":data[0],"type":data[1],"amount":int(data[2])})

def get_time():
    t = rtc.datetime()
    return "{}:{:02d}".format(t[4], t[5])

def get_datetime():
    t = rtc.datetime()
    return "{}/{}/{} {}:{:02d}:{:02d}".format(t[1], t[2], t[0], t[4], t[5], t[6])

def show_screen_text():
    display.display_text(screen_text[current_screen])

def show_stats(message):
    global current_screen
    current_screen = 'stats'
    bads = 0
    food = 0
    water = 0
    exercise = 0
    for data in log:
        if data["type"] == bad_type:
            bads = bads + data["amount"]
        if data["type"] == 'food':
            food = food + data["amount"]
        if data["type"] == 'water':
            water = water + data["amount"]
        if data["type"] == 'exercise':
            exercise = exercise + data["amount"]
    display.display_text([
        bad_type_proper+": "+str(bads),
        "Food: "+str(food),
        "Water: "+str(water),
        "Exercise: "+str(exercise),
        " ",
        message,
        " ",
        "R - Main Menu"
    ])

def log_thing(type, quantity):
    global log
    log.append({"time":get_datetime(),"type":type,"amount":quantity})
    save_log()

def show_adjust(start):
    global temp_amount
    global current_screen
    temp_amount = start
    current_screen = 'adjust'
    display.display_text([
        "How much "+temp_type+"?",
        " ",
        "-B "+str(temp_amount)+" Y+",
        " ",
        "R - Cancel",
        "G - Confirm"
    ], True)

def motivate():
    display.display_text(random.choice(motivations))
    time.sleep(10)
    show_screen_text()

def fight_craving():
    display.display_text(random.choice(fight))
    time.sleep(10)
    show_screen_text()

def press_red():
    global current_screen
    global temp_amount
    global temp_type
    if display.asleep:
        display.wake()
        return
    if current_screen == 'main':
        current_screen = 'log'
        show_screen_text()
        return
    if current_screen == 'log':
        temp_type = bad_type
        show_adjust(1)
        return
    current_screen = 'main'
    show_screen_text()

def press_green():
    global current_screen
    global temp_amount
    global temp_type
    if display.asleep:
        display.wake()
        return
    if current_screen == 'main':
        motivate()
        return
    if current_screen == 'log':
        temp_type = "food"
        show_adjust(16)
        return
    if current_screen == 'adjust':
        log_thing(temp_type,temp_amount)
        show_stats(temp_type+" logged")
        return

def press_blue():
    global current_screen
    global temp_amount
    global temp_type
    if display.asleep:
        display.wake()
        return
    if current_screen == 'main':
        show_stats("")
        return
    if current_screen == 'log':
        temp_type = "water"
        show_adjust(16)
        return
    if current_screen == 'adjust':
        adj = 0
        if temp_type == bad_type:
            adj = 1
        if temp_type == "water":
            adj = 8
        if temp_type == "food":
            adj = 8
        if temp_type == "exercise":
            adj = 10
        if temp_amount - adj < 0:
            return
        show_adjust(temp_amount - adj)

def press_yellow():
    global current_screen
    global temp_amount
    global temp_type
    if display.asleep:
        display.wake()
        return
    if current_screen == 'main':
        fight_craving()
        return
    if current_screen == 'log':
        temp_type = "exercise"
        show_adjust(20)
        return
    if current_screen == 'adjust':
        if temp_type == bad_type:
            show_adjust(temp_amount + 1)
            return
        if temp_type == "water":
            show_adjust(temp_amount + 8)
            return
        if temp_type == "food":
            show_adjust(temp_amount + 8)
            return
        if temp_type == "exercise":
            show_adjust(temp_amount + 5)
            return

buttons.button_up_r = press_red
buttons.button_up_g = press_green
buttons.button_up_b = press_blue
buttons.button_up_y = press_yellow

load_data()
load_log()

show_screen_text()

while True:
    input = buttons.update()
    display.update(input)
    time.sleep(0.01)
#display_text('1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF')
