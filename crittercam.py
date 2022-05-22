from datetime import datetime, timedelta
import json
import time
import cv2
import paho.mqtt.client as mqtt

class CritterCam:
	def __init__(self):
		self.cameras = [
			cv2.VideoCapture(0),
			cv2.VideoCapture("http://192.168.0.200/videostream.cgi?user=viewer&pwd=viewer"),
			cv2.VideoCapture("http://192.168.0.201/videostream.cgi?user=viewer&pwd=viewer")
		]
		self.client = mqtt.Client()
		self.client.on_message = self.on_message
		self.client.on_connect = self.on_connect
		self.client.on_disconnect = self.on_disconnect
		self.running = False
		self.last_status = ""
		self.lux = 0

	def on_connect(self, clent, userdata, flags, rc):
		print("client connected")

	def on_disconnect(self, client, userdata, rc):
		print("client disconnected")

	def start(self):
		self.client.connect("192.168.2.200")
		self.client.subscribe("crittercam/#")
		self.running = True
		self.client.loop_start()
		while self.running is True:
			time.sleep(1)
		self.dispose()
	
	def capture(self, camnum, seconds):
		print("capturing on camera "+str(camnum))
		cap = self.cameras[camnum]
		now = datetime.now()
		nowstr = now.strftime("%Y%m%d%H%M")
		fps = [ 30.0, 15.0, 15.0 ]
		res = [(1920, 1080), (640, 480), (640, 480)]
		out = cv2.VideoWriter("output_"+str(camnum)+".avi", cv2.VideoWriter_fourcc(*'XVID'), fps[camnum], res[camnum])
		while(now > datetime.now() - timedelta(seconds=seconds)):
			ref, frame = cap.read()
			out.write(frame)
		out.release()
		print("done capturing")
	
	def capture_still(self, camnum):
		print("grabbing still from camera "+str(camnum))
		cap = self.cameras[camnum]
		success, image = cap.read()
		cv2.imwrite("output_"+str(camnum)+".jpg", image)
		print("image captured")
	
	def dispose(self):
		self.client.disconnect()
		for cam in self.cameras:
			cam.release()
		cv2.destroyAllWindows()
		exit()
	
	def on_message(self, client, userdata, message):
		topic = message.topic
		if "stopcritter" in topic:
			self.running = False
			self.dispose()
		if "crittercam" not in topic:
			return
		text = str(message.payload.decode("utf-8"))
		command = text.split(':')
		cam = int(command[0])
		if len(command) > 1:
			sec = int(command[1])
		else:
			sec = 0
		if sec == 0:
			self.capture_still(cam)
		else:
			self.capture(cam,sec)
	
	def motion(self):
		if self.lux > 800:
			self.capture(0,60)
		else:
			self.capture(1,120)

if __name__ == "__main__":
	cc = CritterCam()
	cc.start()
