import time
from datetime import datetime, timedelta
import traceback

from main import SmarterCircuitsMCP
try:
    import cv2
except:
    cv2 = None

class CameraManager:
    def __init__(self, mcp: SmarterCircuitsMCP):
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
    
    def capture(self, camnum, seconds):
        self.mcp.send_discord_message(self.mcp.discord_debug_room,"capturing on camera "+str(camnum))
        cap = self.cameras[camnum]
        now = datetime.now()
        nowstr = now.strftime("%Y%m%d%H%M")
        fps = [ 30.0, 15.0, 15.0 ]
        res = [(1920, 1080), (640, 480), (640, 480)]
        out = cv2.VideoWriter("output_"+str(camnum)+".avi", cv2.VideoWriter_fourcc(*'XVID'), fps[camnum], res[camnum])
        while(now > datetime.now() - timedelta(seconds=seconds)):
            ref, frame = cap.read()
            frame = cv2.putText(frame, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), (50,res[camnum][1]-50), self.font, self.fontScale, self.color, self.thickness, cv2.LINE_AA)
            out.write(frame)
        out.release()
        self.mcp.send_discord_message(self.mcp.discord_debug_room,"done capturing")
    
    def capture_still(self, camnum):
        try:
            self.mcp.send_discord_message(self.mcp.discord_debug_room,"grabbing still from camera "+str(camnum))
            cap = self.cameras[camnum]
            success, image = cap.read()
            res = [(1920, 1080), (640, 480), (640, 480)]
            image = cv2.putText(image, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), (50,res[camnum][1]-50), self.font, self.fontScale, self.color, self.thickness, cv2.LINE_AA)
            cv2.imwrite("output_"+str(camnum)+".jpg", image)
            self.mcp.send_discord_message(self.mcp.discord_debug_room,"image captured")
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            self.mcp.handle_exception(error,tb,"SmarterCameraManager")
    
    def dispose(self):
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