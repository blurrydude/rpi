import paho.mqtt.client as mqtt
client = mqtt.Client()

client.connect("192.168.2.200")

topic = 'shellies/shellydimmer2-3C6105E411C6/light/0/set'
#payload = '{"brightness": 0,"transition": 2000}'
payload = '{"turn": "off","transition": 5000}'
#payload = '{"brightness": 50,"turn": "on","transition": 2000}'

client.publish(topic, payload)

client.disconnect()