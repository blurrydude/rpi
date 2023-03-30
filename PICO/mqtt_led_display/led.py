import array, time
from machine import Pin
import rp2

class RGBLED:
    def __init__(self, count, pin):
        self.led_count = count
        self.PIN_NUM = pin
        self.brightness = 0.1 # 0.1 = darker, 1.0 = brightest
        self.width = 8
        self.red = (255,0,0)
        self.green = (0,255,0)
        self.blue = (0,0,255)
        self.yellow = (255,255,0)
        self.cyan = (0,255,255)
        self.white = (255,255,255)
        self.blank = (0,0,0)
 
        @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT,
                    autopull=True, pull_thresh=24) # PIO configuration
 
        # define WS2812 parameters
        def ws2812():
            T1 = 2
            T2 = 5
            T3 = 3
            wrap_target()
            label("bitloop")
            out(x, 1)               .side(0)    [T3 - 1]
            jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
            jmp("bitloop")          .side(1)    [T2 - 1]
            label("do_zero")
            nop()                   .side(0)    [T2 - 1]
            wrap()
 
 
        # Create the StateMachine with the ws2812 program, outputting on pre-defined pin
        # at the 8MHz frequency
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(self.PIN_NUM))
        
        # Activate the state machine
        self.sm.active(1)
        
        # Range of LEDs stored in an array
        self.ar = array.array("I", [0 for _ in range(self.led_count)])

    def pixels_show(self,brightness_input=0.5):
        dimmer_ar = array.array("I", [0 for _ in range(self.led_count)])
        for ii,cc in enumerate(self.ar):
            r = int(((cc >> 8) & 0xFF) * brightness_input) # 8-bit red dimmed to brightness
            g = int(((cc >> 16) & 0xFF) * brightness_input) # 8-bit green dimmed to brightness
            b = int((cc & 0xFF) * brightness_input) # 8-bit blue dimmed to brightness
            dimmer_ar[ii] = (g<<16) + (r<<8) + b # 24-bit color dimmed to brightness
        self.sm.put(dimmer_ar, 8) # update the state machine with new colors
        time.sleep_ms(1)
    
    def pixels_set(self, i, color):
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2] # set 24-bit color
            
    def breathing_led(self, color):
        step = 5
        breath_amps = [ii for ii in range(0,255,step)]
        breath_amps.extend([ii for ii in range(255,-1,-step)])
        for ii in breath_amps:
            for jj in range(len(self.ar)):
                self.pixels_set(jj, color) # show all colors
            self.pixels_show(ii/255)
            time.sleep(0.01)

    def set_pixel(self, x, y, color, brightness=0.01):
        i = (y * self.width) + x
        self.pixels_set(i, color)
        self.pixels_show(brightness)

    def set_ipixel(self, i, color, brightness=0.01):
        self.pixels_set(i, color)
        self.pixels_show(brightness)

 
#while True: # loop indefinitely
#    for color in colors: 
#        breathing_led(color)
#        time.sleep(0.1) # wait between colors

# img = [
#     [1,1,blue],
#     [6,1,blue],
#     [3,3,blue],
#     [4,3,blue],
#     [1,6,blue],
#     [2,7,blue],
#     [3,7,blue],
#     [4,7,blue],
#     [5,7,blue],
#     [6,6,blue]
#     ]

# for p in img:
#     set_pixel(p[0], p[1], p[2])

