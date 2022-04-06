import paho.mqtt.client as mqtt
import _thread
import time
from SmarterLogging import SmarterLog

class SmarterMQTTClient:
    def __init__(self, brokers, topics, on_message):
        self.client = mqtt.Client()
        self.client.on_message = on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect = self.on_connect
        self.connected = False
        self.running = False
        self.shutting_down = False
        self.brokers = brokers
        self.topics = topics
        self.connection_attempts = 0
        self.broker_id = 0
        self.broker = brokers[0]
        _thread.start_new_thread(self.start_listening, ())
    
    def log(self, message):
        SmarterLog.log("SmarterMQTTClient",message)
    
    def start_listening(self):
        self.connect()
        self.log("start_listening to "+self.broker)
        self.client.loop_start()
        self.running = True
        while self.running is True:
            time.sleep(1)
        self.shutdown()
    
    def stop(self):
        self.log("stop")
        self.running = False
        time.sleep(2)
    
    def shutdown(self):
        self.log("shutdown")
        if self.running is True:
            self.stop()
        self.shutting_down = True
        self.client.disconnect()

    def subscribe_to_topics(self):
        self.log("subscribe_to_topics")
        for topic in self.topics:
            self.log("subscribe to "+topic)
            self.client.subscribe(topic)

    def on_connect(self, client, userdata, flags, rc):
        self.log("connected to "+self.broker)
        self.connected = True
        self.subscribe_to_topics()

    def on_disconnect(self, client, userdata, rc):
        self.log("disconnected from "+self.broker)
        if self.shutting_down is False:
            self.connected = False
            self.connect()

    def connect(self):
        self.log("connect to "+self.broker)
        try:
            self.client.connect(self.broker)
            self.connection_attempts = 0
        except:
            if self.connection_attempts >= 3:
                self.connection_attempts = 0
                next_id = self.broker_id + 1
                if next_id >= len(self.brokers):
                    next_id = 0
                self.broker_id = next_id
                self.broker = self.brokers[self.broker_id]
            else:
                self.connection_attempts = self.connection_attempts + 1
            self.connect()
    
    def publish(self, topic, message):
        #self.log("publish '"+message+"' to '"+topic+"'")
        if self.connected is False:
            return False
        try:
            self.client.publish(topic, message)
            return True
        except:
            return False
