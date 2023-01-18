from machine import Pin, PWM, I2C, RTC
from buzzer import Buzzer
from sensor import Sensor
from display import Display
from buttons import Buttons
import time
import math
import random

buzzer = Buzzer()
sensor = Sensor()
display = Display()
buttons = Buttons()
rtc = RTC()
current_screen = 'main'





def get_time():
    t = rtc.datetime()
    return "{}:{:02d}".format(t[4], t[5])

def get_datetime():
    t = rtc.datetime()
    return "{}/{}/{} {}:{:02d}:{:02d}".format(t[1], t[2], t[0], t[4], t[5], t[6])



def show_menu():
    global current_screen
    oled.fill(0)
    current_screen = 'menu'
    oled.text('R - Return',0,0)
    oled.text('G - Stats',0,10)
    oled.text('B - Settings',0,20)
    oled.text('Y - Reset',0,30)
    oled.show()

def confirm_reset():
    oled.fill(0)
    oled.text('Are you sure you',0,0)
    oled.text('want to reset',0,10)
    oled.text(pet.name+'?',0,20)
    oled.text('R - CANCEL',0,40)
    oled.text('G - CONFIRM',0,50)
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
        handle_input()
        delay_cycle = delay_cycle + 1

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


