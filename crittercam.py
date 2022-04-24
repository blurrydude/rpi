from datetime import datetime, timedelta
import json
import time
import cv2
import paho.mqtt.client as mqtt

class CritterCam:
	def __init__(self):
		self.cameras = [
			cv2.VideoCapture(0),
			cv2.VideoCapture("http://192.168.0.200/videostream.cgi?user=viewer&pwd=viewer")
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
		self.client.subscribe("shellies/shellymotionsensor-60A42386DDE2")
		self.running = True
		self.client.loop_start()
		while self.running is True:
			time.sleep(1)
		self.dispose()
	
	def capture(self, camnum, seconds):
		print("capturing on camera "+str(camnum))
		cap = self.cameras[camnum]
		now = datetime.now()
		nowstr = now.strftime("%Y%m%d")
		fps = [ 30.0, 20.0 ]
		res = [(1920, 1080), (640, 480)]
		out = cv2.VideoWriter("output_"+str(camnum)+"_"+nowstr+".avi", cv2.VideoWriter_fourcc(*'XVID'), fps[camnum], res[camnum])
		while(now > datetime.now() - timedelta(seconds=seconds)):
			ref, frame = cap.read()
			out.write(frame)
		out.release()
	
	def dispose(self):
		self.client.disconnect()
		for cam in self.cameras:
			cam.release()
		cv2.destroyAllWindows()
		exit()
	
	def on_message(self, client, userdata, message):
		try:
			topic = message.topic
			if "stopcritter" in topic:
				self.running = False
				self.dispose()
			if "shellymotion" not in topic:
				return
			text = str(message.payload.decode("utf-8"))
			data = json.loads(text)
			status = data["motion"]
			self.lux = data["lux"]
			if self.last_status != status:
				self.last_status = status
			if self.last_status is True:
				self.motion()
		except:
			donothing = True
	
	def motion(self):
		if self.lux > 800:
			self.capture(0,60)
		else:
			self.capture(1,120)

if __name__ == "__main__":
	cc = CritterCam()
	cc.start()