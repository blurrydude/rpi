from machine import Pin, PWM, I2C
from ssd1306 import SSD1306_I2C
from buzzer import Buzzer
from tamagotchi import Tamagotchi
import time
import math
import random

cycle_seconds = 60
display_sleep_seconds = 10
play_seconds = 5
feed_seconds = 5
sleep_seconds = 5
silent_start = True

pet = None
buzzer = Buzzer()
sensor_temp = machine.ADC(4)
rtc = machine.RTC()
conversion_factor = 3.3 / (65535)
button_g = Pin(16, Pin.IN, Pin.PULL_DOWN)
button_y = Pin(17, Pin.IN, Pin.PULL_DOWN)
button_b = Pin(18, Pin.IN, Pin.PULL_DOWN)
button_r = Pin(19, Pin.IN, Pin.PULL_DOWN)
button_r_pressed = False
button_g_pressed = False
button_b_pressed = False
button_y_pressed = False
current_screen = 'main'

#Celsius = (Fahrenheit – 32) * 5/9
#Fahrenheit = (Celsius * 9/5) + 32

def get_random_name():
    male_names = ['Max', 'Toby', 'Charlie', 'Leo', 'Rocky', 'Bear', 'Duke', 'Cooper']
    female_names = ['Daisy', 'Molly', 'Sadie', 'Lola', 'Lucy', 'Lily', 'Roxy', 'Mia']
    
    names = male_names + female_names
    return random.choice(names)

def rando_text(x, y, l):
    p = x
    while p < l:
        roll = random.randint(1,100)
        if roll > 80:
            oled.hline(p,y,2,1)
            oled.hline(p,y+1,2,1)
            p = p + 3
        elif roll > 70:
            oled.hline(p,y,1,1)
            oled.hline(p,y+1,2,1)
            p = p + 3
        elif roll > 60:
            oled.hline(p+1,y,1,1)
            oled.hline(p,y+1,2,1)
            p = p + 3
        elif roll > 50:
            oled.hline(p,y,2,1)
            oled.hline(p,y+1,1,1)
            p = p + 3
        elif roll > 40:
            oled.hline(p,y,2,1)
            oled.hline(p+1,y+1,1,1)
            p = p + 3
        elif roll > 30:
            oled.hline(p,y,1,1)
            oled.hline(p,y+1,1,1)
            p = p + 2
        else:
            p = p + 2

def post_screen():
    oled.fill(0)
    oled.hline(7,1,1,1)
    oled.hline(6,2,3,1)
    oled.hline(5,3,5,1)
    
    oled.hline(4,4,1,1)
    oled.hline(3,5,3,1)
    oled.hline(2,6,5,1)
    
    oled.hline(10,4,1,1)
    oled.hline(9,5,3,1)
    oled.hline(8,6,5,1)
    
    oled.hline(1,7,13,1)
    
    oled.hline(16,1,1,1)
    oled.hline(15,2,3,1)
    oled.hline(15,3,3,1)
    
    oled.hline(15,5,1,1)
    oled.hline(17,5,1,1)
    oled.hline(15,6,3,1)
    oled.hline(15,7,1,1)
    oled.hline(17,7,1,1)
    
    oled.hline(19,2,1,1)
    oled.hline(21,2,1,1)
    oled.hline(19,3,3,1)
    
    oled.hline(23,2,2,1)
    oled.hline(23,3,2,1)
    
    oled.hline(26,2,2,1)
    oled.hline(26,3,1,1)
    
    oled.hline(29,1,1,1)
    oled.hline(29,3,1,1)
    
    oled.hline(31,2,2,1)
    oled.hline(31,3,2,1)
    
    oled.hline(34,2,2,1)
    oled.hline(34,3,2,1)
    
    oled.hline(37,2,2,1)
    oled.hline(37,3,2,1)
    
    oled.hline(19,6,2,1)
    oled.hline(19,7,2,1)
    
    oled.hline(22,6,2,1)
    oled.hline(22,7,2,1)
    oled.hline(23,8,1,1)
    
    oled.hline(25,6,2,1)
    oled.hline(25,7,2,1)
    
    oled.hline(28,6,2,1)
    oled.hline(29,7,1,1)
    
    oled.hline(31,6,2,1)
    oled.hline(31,7,1,1)
    
    oled.hline(34,6,2,1)
    oled.hline(34,7,2,1)
    
    oled.hline(37,6,2,1)
    oled.hline(37,7,2,1)
    
    oled.hline(41,5,1,1)
    oled.hline(40,6,2,1)
    oled.hline(40,7,2,1)
    
    oled.hline(44,6,1,1)
    oled.hline(43,7,2,1)
    
    rando_text(1,12,50)
    rando_text(1,15,50)
    rando_text(1,18,56)
    rando_text(1,21,48)
    
    rando_text(1,27,28)
    rando_text(1,30,28)
    rando_text(1,33,42)
    rando_text(1,36,36)
    rando_text(1,39,16)
    
    rando_text(1,52,30)
    rando_text(1,55,56)
    
    oled.show()
    if silent_start is not True:
        buzzer.play_note('b',0.3)
        time.sleep(0.05)
        buzzer.play_note('b',0.3)
        buzzer.play_note('a',0.2)

        time.sleep(1.5)

        buzzer.play_note('e2',0.3)
        time.sleep(0.05)
        buzzer.play_note('e2',0.3)
        buzzer.play_note('c2',0.2)

        time.sleep(1.5)
        buzzer.play_note('b5',0.2)

def get_temp():
    reading = sensor_temp.read_u16() * conversion_factor
    temperature_c = 27 - (reading - 0.706)/0.001721
    temperature_f = (temperature_c * 9/5) + 32
    pet.temperature = temperature_f
    return str(temperature_f)+' F'

def get_time():
    t = rtc.datetime()
    return "{}:{:02d}".format(t[4], t[5])

def get_datetime():
    t = rtc.datetime()
    return "{}/{}/{} {}:{:02d}:{:02d}".format(t[1], t[2], t[0], t[4], t[5], t[6])

def display_text(text):
    oled.fill(0)
    for i in range(len(text)):
        y = math.floor(i/16)
        x = i-(y*16)
        oled.text(text[i],x*8,y*8)
    oled.show()

def handle_r_button():
    global current_screen
    if button_r_pressed:
        print('red pressed')
    else:
        print('red released')
        #show_temp()
        if current_screen == 'main':
            show_menu()
        else:
            current_screen = 'main'
            show_pet_status()

def show_menu():
    global current_screen
    oled.fill(0)
    current_screen = 'menu'
    oled.text('R - Return',0,0)
    oled.text('G - Stats',0,10)
    oled.text('B - Settings',0,20)
    oled.text('Y - Reset',0,30)
    oled.show()
    
def handle_g_button():
    global current_screen
    global pet
    if button_g_pressed:
        print('green pressed')
    else:
        print('green released')
        #post_screen()
        if current_screen == 'main':
            feed_pet()
        if current_screen == 'menu':
            current_screen = 'status'
            show_pet_status_detail()
        if current_screen == 'confirm_reset':
            pet = Tamagotchi(get_random_name(),0,100,100)
            oled.fill(0)
            oled.text("You've adopted",0,0)
            oled.text('a new pet named',0,10)
            oled.text(pet.name+'.',0,20)
            oled.show()
            time.sleep(3)
            current_screen = 'main'
            show_pet_status()
            

def feed_pet():
    display_text('Feeding pet...')
    # do some cool animation
    for _ in range(feed_seconds):
        display_text('Feeding pet')
        time.sleep(0.25)
        display_text('Feeding pet.')
        time.sleep(0.25)
        display_text('Feeding pet..')
        time.sleep(0.25)
        display_text('Feeding pet...')
        time.sleep(0.25)
        pet.feed()
    display_text('Pet fed.')
    time.sleep(2)
    show_pet_status()

def handle_b_button():
    if button_b_pressed:
        print('blue pressed')
    else:
        print('blue released')
        #display_text('Blue. Good Job.')
        if current_screen == 'main':
            tuck_pet()
def tuck_pet():
    display_text('Goodnight, '+pet.name)
    time.sleep(2)
    # do some cool animation
    for _ in range(sleep_seconds):
        display_text('Zzz')
        time.sleep(0.25)
        display_text('Zzzzz')
        time.sleep(0.25)
        display_text('Zzzzzz.')
        time.sleep(0.25)
        display_text('Zzzzzz...')
        time.sleep(0.25)
        pet.sleep()
    display_text('Pet rested.')
    time.sleep(2)
    show_pet_status()
        
def handle_y_button():
    global current_screen
    if button_y_pressed:
        print('yellow pressed')
    else:
        print('yellow released')
        #display_text('they call me    mellow yellow')
        if current_screen == 'main':
            play()
        if current_screen == 'menu':
            current_screen = 'confirm_reset'
            confirm_reset()

def confirm_reset():
    oled.fill(0)
    oled.text('Are you sure you',0,0)
    oled.text('want to reset',0,10)
    oled.text(pet.name+'?',0,20)
    oled.text('R - CANCEL',0,40)
    oled.text('G - CONFIRM',0,50)
    oled.show()

def play():
    for _ in range(play_seconds):
        display_text('Fun')
        time.sleep(0.25)
        display_text('Fun fun')
        time.sleep(0.25)
        display_text('Fun fun fun')
        time.sleep(0.25)
        display_text('Fun fun fun                                                yay!')
        time.sleep(0.25)
        pet.play()
    display_text('That was...                             fun')
    time.sleep(2)
    show_pet_status()

def show_temp():
    text_to_display = get_temp()
    while len(text_to_display) < 16:
        text_to_display = text_to_display + ' '
    text_to_display = text_to_display + get_time()
    display_text(text_to_display)

def show_pet_status():
    alerts = []
    
    temp = get_temp()
    now = get_time()
    if pet.energy < 20:
        alerts.append('tired')
    if pet.happiness < 20:
        alerts.append('lonely')
    if pet.hunger < 20:
        alerts.append('hungry')
    if pet.uncomfortable:
        alerts.append('uncomfortable')
    if len(alerts) == 0:
        if pet.happiness > 80:
            alerts.append('elated')
        elif pet.happiness > 70:
            alerts.append('happy')
        elif pet.happiness > 50:
            alerts.append('content')
        elif pet.happiness > 40:
            alerts.append('coping')
    oled.fill(0)
    oled.text(now,0,0)
    oled.text(temp,0,10)
    oled.text(pet.name + ' is',0,20)
    i = 3
    for alert in alerts:
        text = alert
        if i < len(alerts) - 1:
            text = text + ' and'
        oled.text(text, 0, i * 10)
        i = i + 1
    oled.show()

def show_pet_status_detail():
    oled.fill(0)
    oled.text(pet.name,0,0)
    oled.text('Age: '+str(pet.age),0,10)
    oled.text('Energy: '+str(pet.energy),0,20)
    oled.text('Happiness: '+str(pet.happiness),0,30)
    oled.text('Belly: '+str(pet.hunger),0,40)
    oled.text('Temp: '+get_temp(),0,50)
    oled.show()

#print('set up i2c')
pet = Tamagotchi(get_random_name(),0,100,100)
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=200000)
devices = i2c.scan()
if len(devices) == 0:
    print('bad')
else:
    #print('set up oled')
    oled = SSD1306_I2C(128,64,i2c)
    post_screen()
    delay_cycle = 0
    since_last_press = 0
    time.sleep(1)
    show_pet_status()
    while True:
        delay_cycle = delay_cycle + 1
        r_pressed = button_r.value() > 0
        g_pressed = button_g.value() > 0
        b_pressed = button_b.value() > 0
        y_pressed = button_y.value() > 0
        if r_pressed != button_r_pressed:
            button_r_pressed = r_pressed
            since_last_press = 0
            handle_r_button()
        if g_pressed != button_g_pressed:
            button_g_pressed = g_pressed
            since_last_press = 0
            handle_g_button()
        if b_pressed != button_b_pressed:
            button_b_pressed = b_pressed
            since_last_press = 0
            handle_b_button()
        if y_pressed != button_y_pressed:
            button_y_pressed = y_pressed
            since_last_press = 0
            handle_y_button()
        if since_last_press > 6000:
            since_last_press = 0
        if display_sleep_seconds > 0 and delay_cycle == display_sleep_seconds * 100:
            oled.fill(0)
            oled.show()
        if delay_cycle >= cycle_seconds * 100:
            delay_cycle = 0
            if current_screen == 'main':
                pet.wait()
                show_pet_status()
                
            #print(str(reading))
        time.sleep(0.01)
    #display_text('1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF')


