from macro_runner import MacroRunner
import json
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import busio
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

i2c = busio.I2C (scl=board.GP9, sda=board.GP8) # This RPi Pico way to call I2C
display_bus = displayio.I2CDisplay (i2c, device_address = 0x3C) # The address of my Board
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

def draw(text):
    splash = displayio.Group()

    color_bitmap = displayio.Bitmap(128, 64, 1) # Full screen white
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFFFFFF  # White

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)
    
    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(118, 54, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=4)
    splash.append(inner_sprite)
    display.show(splash)

    # Draw a label
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=28, y=15)
    splash.append(text_area)

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

macro = MacroRunner(0.03)
# list of pins to use (skipping GP15 on Pico because it's funky)
pins = (
    board.GP10,
    board.GP11,
    board.GP13,
    board.GP21,
    board.GP26,
    board.GP28,
    board.GP22,
    board.GP27,
    board.GP19,
    board.GP20,
    board.GP7,
    board.GP16,
    board.GP18,
    board.GP14,
    board.GP6,
    board.GP17,
    board.GP12
)

keymap = json.load(open('config.json'))
switch_count = len(pins)
switches = []
switch_state = []
for i in range(switch_count):
    switch = DigitalInOut(pins[i])
    switch.direction = Direction.INPUT
    switch.pull = Pull.UP
    switches.append(switch)
    switch_state.append(1)



while True:
    for button in range(switch_count):
        state = switches[button].value
        if switch_state[button] != state:
            switch_state[button] = state
            if state == 1:
                mac = keymap[button]
                draw(mac)
                macro.run_macro(mac)

    time.sleep(0.01)  # debounce
