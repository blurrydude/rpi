import cv2
#ip_base = "184.57."
ip_base = "192.168."

# loop through each IP address and attempt to connect to MJPEG stream on port 8080
found = []
for x in range(0,1):
    for y in range(200,201):
        ip = f"{ip_base}{x}.{y}"
        try:
            # create video capture object for MJPEG stream
            stream = cv2.VideoCapture('http://' + ip + '/videostream.cgi')
            
            # check if connection was successful
            if stream.isOpened():
                print('Connected to MJPEG stream on', ip)
                found.append(ip)
            # else:
            #     print('Failed to connect to MJPEG stream on', ip)
                
            # release video capture object
            stream.release()
        except:
            pass

print(found)