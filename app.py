from flask import Flask , redirect , url_for , Response
import os
import cv2
import numpy as np
from HandTrackingModule import handDetector as htm

app = Flask("name")

folder_path = "header"

my_list = os.listdir(folder_path)

overlay_list = []
for image_path in my_list:
    image = cv2.imread(f'{folder_path}//{image_path}')
    overlay_list.append(image)

header = overlay_list[0]
drawColor = (0,0 ,255)

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

detector = htm.handDetector(detectionCon = 0.85)
xp , yp  = 0 ,0 
imgCanvas = np.zeros((720 , 1280 , 3 ),np.uint8)

def live_video():

    while True:
        success , img = cap.read()

        if not success:
            break
        else:
            img = cv2.flip(img , 1)
            img = detector.findHands(img)
            lmlist = detector.findPosition(img , draw = False)

            if len(lmlist) != 0:
                x1, y1 = lmlist[8][1:]
                x2, y2 = lmlist[12][1:]

                fingers = detector.fingersUp()

                if fingers[1] and fingers[2]:
                    xp , yp = 0 , 0 
                    print("Selection Mode")
                    cv2.rectangle(img , (x1,y1-15) , (x2,y2+25) , drawColor, cv2.FILLED)
                    
                    if y1<125:
                        if 150<x1<300:
                            header = overlay_list[0]
                            drawColor = (0,0,255)
                        elif 350<x1<600:
                            header = overlay_list[1]
                            drawColor = (255 , 0 ,0)
                        elif 750<x1<950:
                            header = overlay_list[2]
                            drawColor = (0,0,0)
                        elif 1050<x1<1200:
                            header = overlay_list[3]
                            imgCanvas = np.zeros((720, 1280, 3), np.uint8)

                if fingers[1] and fingers[2] == False:
                    cv2.circle(img , (x1,y1) , 15 , drawColor , cv2.FILLED)
                    print("Drawing Mode")
                    if xp == 0 and yp == 0:
                        xp , yp = x1 , y1

                    cv2.line(img , (xp , yp), (x1,y1) , drawColor , 15 )
                    cv2.line(imgCanvas , (xp , yp), (x1,y1) , drawColor , 15 )

                    if drawColor == (0,0,0):                ### Increase the size of eraser
                        cv2.line(img , (xp , yp), (x1,y1) , drawColor , 60 )
                        cv2.line(imgCanvas , (xp , yp), (x1,y1) , drawColor , 60 )
                    else:
                        cv2.line(img , (xp , yp), (x1,y1) , drawColor , 15 )
                        cv2.line(imgCanvas , (xp , yp), (x1,y1) , drawColor , 15 )

                    xp , yp = x1 , y1
            
        imgGray = cv2.cvtColor(imgCanvas , cv2.COLOR_BGR2GRAY)
        _ , imgInv = cv2.threshold(imgGray , 20 , 255 , cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv , cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img , imgInv)
        img = cv2.bitwise_or(img , imgCanvas)

        img[0:125,0:1280] = header
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/video_feed')
def video_feed():
    return Response(live_video(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == "__main__":
    app.run(debug = True)
