import time
import numpy as np
import cv2
from datetime import datetime, timedelta
import _thread

def record_ip_cam():
	cap = cv2.VideoCapture('http://192.168.0.200/videostream.cgi?user=viewer&pwd=viewer')
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	out = cv2.VideoWriter('output_ipcam.avi', fourcc, 20.0, (640, 480))
	start = datetime.now()
	while(start > datetime.now() - timedelta(seconds=60)):
		ret, frame = cap.read()
		out.write(frame)
	cap.release()
	out.release()

def record_webcam():
	cap = cv2.VideoCapture(0)
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	out = cv2.VideoWriter('output_webcam.avi', fourcc, 20.0, (1920, 1080))
	start = datetime.now()
	while(start > datetime.now() - timedelta(seconds=60)):
		ret, frame = cap.read()
		out.write(frame)
	cap.release()
	out.release()

_thread.start_new_thread(record_ip_cam, ())
_thread.start_new_thread(record_webcam, ())
start = datetime.now()
while(start > datetime.now() - timedelta(seconds=75)):
	time.sleep(1)
# De-allocate any associated memory usage
cv2.destroyAllWindows()
