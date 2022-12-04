import paho.mqtt.client as mqtt
import time

client = mqtt.Client()

colors = [
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),

    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),

    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),

    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0)
]

colors2 = [
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    (0,255,0),
    
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0),
    (255,0,0)
]

wait_after_send = 0.1

if __name__ == "__main__":
    client.connect('192.168.2.200')

    running = True
    while running is True:
        f = colors[31]
        t = colors[0]
        colors[31] = colors[0]
        if f != t:
            client.publish('pi/addresspi/commands','1:'+str(colors[31][0])+':'+str(colors[31][1])+':'+str(colors[31][2])+':31')
            time.sleep(wait_after_send)
        for i in range(31):
            f = colors[i]
            t = colors[i+1]
            colors[i] = colors[i+1]
            if f != t:
                client.publish('pi/addresspi/commands','1:'+str(colors[i][0])+':'+str(colors[i][1])+':'+str(colors[i][2])+':'+str(i))
                time.sleep(wait_after_send)

        f = colors2[59]
        t = colors2[0]
        colors2[59] = colors2[0]
        if f != t:
            client.publish('pi/clockpi/commands','1:'+str(colors2[59][0])+':'+str(colors2[59][1])+':'+str(colors2[59][2])+':59')
            time.sleep(wait_after_send)
        for i in range(59):
            f = colors2[i]
            t = colors2[i+1]
            colors2[i] = colors2[i+1]
            if f != t:
                client.publish('pi/clockpi/commands','1:'+str(colors2[i][0])+':'+str(colors2[i][1])+':'+str(colors2[i][2])+':'+str(i))
                time.sleep(wait_after_send)
        time.sleep(3)

    client.disconnect()