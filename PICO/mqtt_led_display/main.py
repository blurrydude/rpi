from machine import Pin, PWM, I2C, RTC
from led import RGBLED
import network
from umqtt.simple import MQTTClient
import utime

def main(server="localhost"):
    c = MQTTClient("umqtt_client", server)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"shellies/#")
    c.subscribe(b"picolight")
    while True:
        if True:
            # Blocking wait for message
            c.wait_msg()
        else:
            # Non-blocking wait for message
            c.check_msg()
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            time.sleep(1)

    c.disconnect()

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    path = topic.decode('utf-8').split('/')
    data = msg.decode('utf-8')
    handle_message(path, data)

def handle_message(path, data):
    global relays
    data = "".join(data.split())
    if path[0] == "picolight":
        print(data)
        clear()
        bp = 0
        r = 0
        g = 0
        b = 0
        p = 0
        bv = ''
        x = 0
        y = 0
        for i in range(len(data)):
            v = data[i]
            bv = bv + v
            if len(bv) == 2:
                iv = int(bv,16)
                bv = ''
                if bp == 0:
                    x = iv
                    bp = 1
                elif bp == 1:
                    y = iv
                    bp = 2
                elif bp == 2:
                    r = iv
                    bp = 3
                elif bp == 3:
                    g = iv
                    bp = 4
                elif bp == 4:
                    b = iv
                    bp = 0
                    preset_pixel(x,y, (r,g,b))
                    x = x + 1
                    if x == 16:
                        x = 0
                        y = y + 1
        rgb.pixels_show(0.10)
        return
    
    device = path[1].split('-')
    if device[0] == "shelly1pm" or device[0] == "shellyswitch25" or device[0] == "shellydimmer2":
        return
        if path[2] == "relay" and len(path) == 4:
            relay_id = path[3]
            did = f"{device[1]}-{relay_id}"
        elif path[2] == "light" and len(path) == 4:
            did = device[1]
        else:
            return
        print(data)
        next_id = len(circuit)
        if did not in relays.keys():
            relays[did] = {"id":next_id,"on":False}
            circuit.append(False)
            
        relays[did]["on"] = data == "on"
        i = relays[did]["id"]
        
        if relays[did]["on"] == circuit[i]:
            return
        
        circuit[i] = relays[did]["on"]
        
        #if relays[did]["on"] is True:
        #    #pin[i].off()
        #    rgb.set_ipixel(i, (255,255,255))
        #else:
        #    #pin[i].on()
        #    rgb.set_ipixel(i, (0,0,0))
                    
                    
def get_i(x,y):
    translations = [
        [ 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56],
        [ 72, 73, 74, 75, 76, 77, 78, 79, 48, 49, 50, 51, 52, 53, 54, 55],
        [ 87, 86, 85, 84, 83, 82, 81, 80, 47, 46, 45, 44, 43, 42, 41, 40],
        [ 88, 89, 90, 91, 92, 93, 94, 95, 32, 33, 34, 35, 36, 37, 38, 39],
        [103,102,101,100, 99, 98, 97, 96, 31, 30, 29, 28, 27, 26, 25, 24],
        [104,105,106,107,108,109,110,111, 16, 17, 18, 19, 20, 21, 22, 23],
        [119,118,117,116,115,114,113,112, 15, 14, 13, 12, 11, 10,  9,  8],
        [120,121,122,123,124,125,126,127,  0,  1,  2,  3,  4,  5,  6,  7],
        [199,198,197,196,195,194,193,192,191,190,189,188,187,186,185,184],
        [200,201,202,203,204,205,206,207,176,177,178,179,180,181,182,183],
        [215,214,213,212,211,210,209,208,175,174,173,172,171,170,169,168],
        [216,217,218,219,220,221,222,223,160,161,162,163,164,165,166,167],
        [231,230,229,228,227,226,225,224,159,158,157,156,155,154,153,152],
        [232,233,234,235,236,237,238,239,144,145,146,147,148,149,150,151],
        [247,246,245,244,243,242,241,240,143,142,141,140,139,138,137,136],
        [248,249,250,251,252,253,254,255,128,129,130,131,132,133,134,135]
    ]
    return translations[y][x]
    
def clear():
    for i in range(256):
        rgb.set_ipixel(i,(0,0,0))
    rgb.pixels_show(0)

def preset_pixel(x, y, c):
    i = get_i(x, y)
    rgb.set_ipixel(i,c)
###################################################
############ SCRIPT STARTS HERE ###################
###################################################
# Set the SSID and passphrase of the ORBI56 network
ssid = 'ORBI56'
password = 'zanyballoon683'

# Set the IP address of the MQTT broker and the topic to publish to
mqtt_server = '192.168.2.200'

rgb = RGBLED(256, 7)
rgb.width = 16

circuit = []
relays = {}
rgb.breathing_led((128,0,0))
utime.sleep(0.5)
print("connecting to wifi...")
# Connect to the Wi-Fi network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, password)
# Wait for the connection to be established
while not sta_if.isconnected():
    rgb.breathing_led((0,0,128))
    utime.sleep(1)
    pass

rgb.breathing_led((0,128,0))
utime.sleep(1)
cs = [
    (255,0,0),
    (0,255,0),
    (0,0,255),
    (255,255,0),
    (255,0,255),
    (0,255,255),
    (255,255,255),
    (0,0,0)
]
ci = 0
for x in range(16):
    for y in range(16):
        if x == 5 or x == 13:
            preset_pixel(x, y, (0,0,0))
        else:
            preset_pixel(x, y, cs[ci])
        ci = ci + 1
        if ci == 8:
            ci = 0
rgb.pixels_show(0.05)
print("connected")

if __name__ == "__main__":
    main(mqtt_server)

