import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

class MacroRunner:
    def __init__(self, delay:float = 0.01):
        self.delay = delay
        self.kbd = Keyboard(usb_hid.devices)
        self.mouse = Mouse(usb_hid.devices)
        self.cc = ConsumerControl(usb_hid.devices)
        self.keycodes = {
            "a": [Keycode.A],
            "b": [Keycode.B],
            "c": [Keycode.C],
            "d": [Keycode.D],
            "e": [Keycode.E],
            "f": [Keycode.F],
            "g": [Keycode.G],
            "h": [Keycode.H],
            "i": [Keycode.I],
            "j": [Keycode.J],
            "k": [Keycode.K],
            "l": [Keycode.L],
            "m": [Keycode.M],
            "n": [Keycode.N],
            "o": [Keycode.O],
            "p": [Keycode.P],
            "q": [Keycode.Q],
            "r": [Keycode.R],
            "s": [Keycode.S],
            "t": [Keycode.T],
            "u": [Keycode.U],
            "v": [Keycode.V],
            "w": [Keycode.W],
            "x": [Keycode.X],
            "y": [Keycode.Y],
            "z": [Keycode.Z],
            "A": [Keycode.LEFT_SHIFT, Keycode.A],
            "B": [Keycode.LEFT_SHIFT, Keycode.B],
            "C": [Keycode.LEFT_SHIFT, Keycode.C],
            "D": [Keycode.LEFT_SHIFT, Keycode.D],
            "E": [Keycode.LEFT_SHIFT, Keycode.E],
            "F": [Keycode.LEFT_SHIFT, Keycode.F],
            "G": [Keycode.LEFT_SHIFT, Keycode.G],
            "H": [Keycode.LEFT_SHIFT, Keycode.H],
            "I": [Keycode.LEFT_SHIFT, Keycode.I],
            "J": [Keycode.LEFT_SHIFT, Keycode.J],
            "K": [Keycode.LEFT_SHIFT, Keycode.K],
            "L": [Keycode.LEFT_SHIFT, Keycode.L],
            "M": [Keycode.LEFT_SHIFT, Keycode.M],
            "N": [Keycode.LEFT_SHIFT, Keycode.N],
            "O": [Keycode.LEFT_SHIFT, Keycode.O],
            "P": [Keycode.LEFT_SHIFT, Keycode.P],
            "Q": [Keycode.LEFT_SHIFT, Keycode.Q],
            "R": [Keycode.LEFT_SHIFT, Keycode.R],
            "S": [Keycode.LEFT_SHIFT, Keycode.S],
            "T": [Keycode.LEFT_SHIFT, Keycode.T],
            "U": [Keycode.LEFT_SHIFT, Keycode.U],
            "V": [Keycode.LEFT_SHIFT, Keycode.V],
            "W": [Keycode.LEFT_SHIFT, Keycode.W],
            "X": [Keycode.LEFT_SHIFT, Keycode.X],
            "Y": [Keycode.LEFT_SHIFT, Keycode.Y],
            "Z": [Keycode.LEFT_SHIFT, Keycode.Z],
            "0": [Keycode.ZERO],
            "1": [Keycode.ONE],
            "2": [Keycode.TWO],
            "3": [Keycode.THREE],
            "4": [Keycode.FOUR],
            "5": [Keycode.FIVE],
            "6": [Keycode.SIX],
            "7": [Keycode.SEVEN],
            "8": [Keycode.EIGHT],
            "9": [Keycode.NINE],
            "`": [Keycode.GRAVE_ACCENT],
            "-": [Keycode.MINUS],
            "=": [Keycode.EQUALS],
            "[": [Keycode.LEFT_BRACKET],
            "]": [Keycode.RIGHT_BRACKET],
            "\\": [Keycode.BACKSLASH],
            ";": [Keycode.SEMICOLON],
            "'": [Keycode.QUOTE],
            ",": [Keycode.COMMA],
            ".": [Keycode.PERIOD],
            "/": [Keycode.FORWARD_SLASH],
            " ": [Keycode.SPACEBAR],
            "!": [Keycode.LEFT_SHIFT, Keycode.ONE],
            "@": [Keycode.LEFT_SHIFT, Keycode.TWO],
            "#": [Keycode.LEFT_SHIFT, Keycode.THREE],
            "$": [Keycode.LEFT_SHIFT, Keycode.FOUR],
            "%": [Keycode.LEFT_SHIFT, Keycode.FIVE],
            "^": [Keycode.LEFT_SHIFT, Keycode.SIX],
            "&": [Keycode.LEFT_SHIFT, Keycode.SEVEN],
            "*": [Keycode.LEFT_SHIFT, Keycode.EIGHT],
            "(": [Keycode.LEFT_SHIFT, Keycode.NINE],
            ")": [Keycode.LEFT_SHIFT, Keycode.ZERO],
            "~": [Keycode.LEFT_SHIFT, Keycode.GRAVE_ACCENT],
            "_": [Keycode.LEFT_SHIFT, Keycode.MINUS],
            "+": [Keycode.LEFT_SHIFT, Keycode.EQUALS],
            "{": [Keycode.LEFT_SHIFT, Keycode.LEFT_BRACKET],
            "}": [Keycode.LEFT_SHIFT, Keycode.RIGHT_BRACKET],
            "|": [Keycode.LEFT_SHIFT, Keycode.BACKSLASH],
            ":": [Keycode.LEFT_SHIFT, Keycode.SEMICOLON],
            '"': [Keycode.LEFT_SHIFT, Keycode.QUOTE],
            "<": [Keycode.LEFT_SHIFT, Keycode.COMMA],
            ">": [Keycode.LEFT_SHIFT, Keycode.PERIOD],
            "?": [Keycode.LEFT_SHIFT, Keycode.FORWARD_SLASH],
            "\n": [Keycode.ENTER]
        }
        self.special_chars = {
            "t": Keycode.TAB,
            "<": Keycode.HOME,
            ">": Keycode.END,
            "d": Keycode.DELETE,
            "p": Keycode.PRINT_SCREEN,
            "n": Keycode.UP_ARROW,
            "s": Keycode.DOWN_ARROW,
            "e": Keycode.RIGHT_ARROW,
            "w": Keycode.LEFT_ARROW,
            "i": Keycode.INSERT,
            "1": Keycode.F1,
            "2": Keycode.F2,
            "3": Keycode.F3,
            "4": Keycode.F4,
            "5": Keycode.F5,
            "6": Keycode.F6,
            "7": Keycode.F7,
            "8": Keycode.F8,
            "9": Keycode.F9,
            "A": Keycode.F10,
            "B": Keycode.F11,
            "C": Keycode.F12
        }
        self.modifiers = {
            "^": Keycode.LEFT_CONTROL,
            "~": Keycode.LEFT_ALT,
            "#": Keycode.GUI,
            "|": Keycode.LEFT_SHIFT
        }
        self.media_keys = {
            "#": ConsumerControlCode.PLAY_PAUSE,
            ">": ConsumerControlCode.SCAN_NEXT_TRACK,
            "<": ConsumerControlCode.SCAN_PREVIOUS_TRACK,
            "_": ConsumerControlCode.MUTE,
            "-": ConsumerControlCode.VOLUME_DECREMENT,
            "+": ConsumerControlCode.VOLUME_INCREMENT,
            "]": ConsumerControlCode.BRIGHTNESS_DECREMENT,
            "[": ConsumerControlCode.BRIGHTNESS_INCREMENT,
            "F": ConsumerControlCode.FAST_FORWARD,
            "R": ConsumerControlCode.REWIND,
            "*": ConsumerControlCode.RECORD,
            "!": ConsumerControlCode.STOP,
            "E": ConsumerControlCode.EJECT
        }
        self.mouse_keys = {
            "l": Mouse.LEFT_BUTTON,
            "r": Mouse.RIGHT_BUTTON,
            "m": Mouse.MIDDLE_BUTTON
        }
    
    def execute_mouse_command(self, mouse_command):
        commands = mouse_command.split(',')
        last_command = ''
        for command in commands:
            subs = command.split(' ')
            if subs[0] == 'c':
                self.mouse.click(self.mouse_keys[subs[1]])
            elif subs[0] == 'p':
                self.mouse.press(self.mouse_keys[subs[1]])
            elif subs[0] == 'r':
                self.mouse.release(self.mouse_keys[subs[1]])
            elif subs[0] == 'm':
                self.mouse.move(int(subs[1]), int(subs[2]), int(subs[3]))
            elif subs[0] == 'x':
                for _ in range(int(subs[1])):
                    self.execute_mouse_command(last_command)
                continue # this makes it stupid proof (i.e. m 10 0 0 x 2 x 2)
            last_command = command

    def execute_keystroke(self, keystroke):
        self.kbd.press(*keystroke)
        time.sleep(self.delay)
        self.kbd.release(*keystroke)
        time.sleep(self.delay)
    
    def run_macro(self, macro):
        escape = False
        special = False
        media = False
        mouse = False
        mouse_command = ''
        keystroke = []
        for c in macro:
            if mouse:
                if c == "}":
                    self.execute_mouse_command(mouse_command)
                    mouse_command = ''
                    mouse = False
                    continue
                mouse_command = mouse_command + c
                continue
            if media:
                self.cc.send(self.media_keys[c])
                media = False
                continue
            if special:
                keystroke.append(self.special_chars[c])
                self.execute_keystroke(keystroke)
                keystroke = []
                special = False
                continue
            if c == '\\':
                escape = True
                continue
            if escape is not True:
                if c == "&":
                    special = True
                    continue
                if c == "@":
                    media = True
                    continue
                if c == "{":
                    mouse = True
                    continue
                if c in self.modifiers.keys():
                    keystroke.append(self.modifiers[c])
                    continue
            escape = False
            keystroke = keystroke + self.keycodes[c]
            self.execute_keystroke(keystroke)
            keystroke = []
