import time
from datetime import datetime, timedelta
import traceback
try:
    import cv2
except:
    cv2 = None

class CameraManager:
    def __init__(self, mcp):
        self.mcp = mcp
        self.cameras = [
            cv2.VideoCapture(0),
            cv2.VideoCapture("http://192.168.0.200/videostream.cgi?user=viewer&pwd=viewer"),
            cv2.VideoCapture("http://192.168.0.201/videostream.cgi?user=viewer&pwd=viewer")
        ]
        self.running = False
        self.last_status = ""
        self.lux = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.org = (50, 50)
        self.fontScale = 1
        self.color = (255, 0, 0)
        self.thickness = 2
        #self.start()

    def on_connect(self, clent, userdata, flags, rc):
        print("client connected")

    def on_disconnect(self, client, userdata, rc):
        print("client disconnected")

    def start(self):
        self.running = True
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
            frame = cv2.putText(frame, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), self.org, self.font, self.fontScale, self.color, self.thickness, cv2.LINE_AA)
            out.write(frame)
        out.release()
        print("done capturing")
    
    def capture_still(self, camnum):
        try:
            print("grabbing still from camera "+str(camnum))
            cap = self.cameras[camnum]
            success, image = cap.read()
            image = cv2.putText(image, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), self.org, self.font, self.fontScale, self.color, self.thickness, cv2.LINE_AA)
            cv2.imwrite("output_"+str(camnum)+".jpg", image)
            print("image captured")
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            self.mcp.log("SmarterCameraManager","capture_still error: "+error)
            self.mcp.log("SmarterCameraManager","capture_still traceback: "+tb)
            self.mcp.mqtt.publish("smarter_circuits/errors/"+self.mcp.name,error)
            self.mcp.mqtt.publish("smarter_circuits/errors/"+self.mcp.name+"/traceback",tb)
    
    def dispose(self):
        self.client.disconnect()
        for cam in self.cameras:
            cam.release()
        cv2.destroyAllWindows()
        exit()
    
    def on_message(self, topic, text):
        if "stopcritter" in topic:
            self.running = False
            self.mcp.stop()
            self.dispose()
        if "crittercam" not in topic:
            return
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