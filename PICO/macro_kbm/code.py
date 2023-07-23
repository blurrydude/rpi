import time
import board
from digitalio import DigitalInOut, Direction, Pull
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
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

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

# list of pins to use (skipping GP15 on Pico because it's funky)
pins = (
    board.GP0,
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP16,
    board.GP17,
    board.GP18,
    board.GP19,
    board.GP20,
    board.GP21,
)

MEDIA = 1
KEY = 2

keymap = {
    (0): (KEY, (Keycode.GUI, Keycode.C)),
    (1): (KEY, (Keycode.GUI, Keycode.V)),
    (2): (KEY, [Keycode.THREE]),
    (3): (KEY, [Keycode.FOUR]),
    (4): (KEY, [Keycode.FIVE]),
    (5): (MEDIA, ConsumerControlCode.VOLUME_DECREMENT),
    (6): (MEDIA, ConsumerControlCode.VOLUME_INCREMENT),

    (7): (KEY, [Keycode.R]),

    (10): (KEY, (Keycode.LEFT_ALT, Keycode.TAB)),
    (11): (MEDIA, ConsumerControlCode.MUTE),
    (12): (MEDIA, ConsumerControlCode.VOLUME_DECREMENT),
    (13): (MEDIA, ConsumerControlCode.VOLUME_INCREMENT),
    (14): (MEDIA, ConsumerControlCode.PLAY_PAUSE),
    
    (15): (KEY, [Keycode.O]),
    (16): (KEY, [Keycode.LEFT_ARROW]),
    (17): (KEY, [Keycode.DOWN_ARROW]),
    (18): (KEY, [Keycode.RIGHT_ARROW]),
    (19): (KEY, [Keycode.ALT]),
    (20): (KEY, [Keycode.U]),

}

switches = []
for i in range(len(pins)):
    switch = DigitalInOut(pins[i])
    switch.direction = Direction.INPUT
    switch.pull = Pull.UP
    switches.append(switch)


switch_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

while True:
    for button in range(19):
        if switch_state[button] == 0:
            if not switches[button].value:
                try:
                    if keymap[button][0] == KEY:
                        kbd.press(*keymap[button][1])
                    else:
                        cc.send(keymap[button][1])
                except ValueError:  # deals w six key limit
                    pass
                switch_state[button] = 1

        if switch_state[button] == 1:
            if switches[button].value:
                try:
                    if keymap[button][0] == KEY:
                        kbd.release(*keymap[button][1])

                except ValueError:
                    pass
                switch_state[button] = 0

    time.sleep(0.01)  # debounce
